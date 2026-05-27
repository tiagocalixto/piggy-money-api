### core/usecases/transaction_usecases.py
"""
Use cases relacionados a transações financeiras.

Contém toda a lógica de negócio para criação, atualização, remoção,
listagem, pagamento de fatura e geração de fatura de cartão de crédito.
"""
from datetime import date, datetime
from typing import Any

from core.entity.transaction import Transaction
from core.finance import gerar_parcelas
from infra.repositories.account_repository import AccountRepository
from infra.repositories.benefit_card_repository import BenefitCardRepository
from infra.repositories.category_repository import CategoryRepository
from infra.repositories.credit_card_repository import CreditCardRepository
from infra.repositories.invoice_repository import InvoiceRepository
from infra.repositories.transaction_repository import TransactionRepository


class CreateTransactionUseCase:
    """Cria uma nova transação financeira com todas as validações de negócio.

    Regras:
    - tipo_movimento obrigatório (entrada ou saida).
    - Origem única: NO MÁXIMO uma entre conta, cartão crédito ou benefício.
    - Cartão de crédito NUNCA aceita ENTRADA, apenas SAIDA.
    - Defaults: efetivada=True, data=hoje, parcelas_total=1.
    - Se parcelas_total > 1: gera N parcelas com data ajustada.
    """

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
        account_repo: AccountRepository,
        credit_card_repo: CreditCardRepository,
        benefit_card_repo: BenefitCardRepository,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.account_repo = account_repo
        self.credit_card_repo = credit_card_repo
        self.benefit_card_repo = benefit_card_repo

    def execute(
        self,
        usuario_id: int,
        descricao: str,
        valor: float,
        categoria_id: int,
        tipo_movimento: str,
        conta_id: int | None = None,
        cartao_credito_id: int | None = None,
        cartao_beneficio_id: int | None = None,
        efetivada: bool = True,
        data: datetime | None = None,
        parcelas_total: int = 1,
    ) -> list[Transaction]:
        """Executa a criação da(s) transação(ões).

        Args:
            usuario_id: ID do usuário.
            descricao: Descrição da transação.
            valor: Valor total da transação.
            categoria_id: ID da categoria.
            tipo_movimento: 'entrada' ou 'saida'.
            conta_id: ID da conta (origem única, opcional).
            cartao_credito_id: ID do cartão de crédito (opcional).
            cartao_beneficio_id: ID do cartão de benefício (opcional).
            efetivada: Se a transação está efetivada.
            data: Data da transação (default: agora).
            parcelas_total: Número total de parcelas (default: 1).

        Returns:
            Lista de transações criadas.

        Raises:
            ValueError: Se regras de negócio forem violadas.
        """
        # Validação: tipo_movimento obrigatório
        if tipo_movimento not in ("entrada", "saida"):
            raise ValueError(
                "Tipo de movimento deve ser 'entrada' ou 'saida'."
            )

        # Validação: origem única
        origens = [
            o
            for o in (conta_id, cartao_credito_id, cartao_beneficio_id)
            if o is not None
        ]
        if len(origens) > 1:
            raise ValueError(
                "A transação deve ter NO MÁXIMO uma origem "
                "(conta, cartão de crédito ou cartão de benefício)."
            )

        # Validação: cartão de crédito NÃO aceita ENTRADA
        if cartao_credito_id and tipo_movimento == "entrada":
            raise ValueError(
                "Cartão de crédito não aceita transações do tipo ENTRADA."
            )

        # Validação: verifica se a categoria existe
        categoria = self.category_repo.get_by_id(categoria_id)
        if categoria is None:
            raise ValueError(f"Categoria com id={categoria_id} não encontrada.")

        # Validação: se origem for conta, verifica se existe
        if conta_id:
            conta = self.account_repo.get_by_id(conta_id)
            if conta is None:
                raise ValueError(f"Conta com id={conta_id} não encontrada.")

        # Validação: se origem for cartão de crédito, verifica se existe
        if cartao_credito_id:
            cartao = self.credit_card_repo.get_by_id(cartao_credito_id)
            if cartao is None:
                raise ValueError(
                    f"Cartão de crédito com id={cartao_credito_id} não encontrado."
                )

        # Validação: se origem for cartão de benefício, verifica se existe
        if cartao_beneficio_id:
            beneficio = self.benefit_card_repo.get_by_id(
                cartao_beneficio_id
            )
            if beneficio is None:
                raise ValueError(
                    f"Cartão de benefício com id={cartao_beneficio_id} não encontrado."
                )

        # Validação: parcelas_total e valor
        if parcelas_total < 1:
            raise ValueError("Número de parcelas deve ser pelo menos 1.")

        if valor <= 0:
            raise ValueError("O valor da transação deve ser maior que zero.")

        # Defaults
        if data is None:
            data = datetime.now()

        # Constrói a transação base
        transaction = Transaction(
            usuario_id=usuario_id,
            descricao=descricao.strip(),
            valor=valor,
            categoria_id=categoria_id,
            tipo_movimento=tipo_movimento,
            data=data,
            efetivada=efetivada,
            conta_id=conta_id,
            cartao_credito_id=cartao_credito_id,
            cartao_beneficio_id=cartao_beneficio_id,
            parcelas_total=parcelas_total,
            parcela_atual=1,
        )

        # Se parcelado, gera todas as parcelas
        if parcelas_total > 1:
            return gerar_parcelas(transaction, self.transaction_repo)

        # Senão, cria uma única transação
        created = self.transaction_repo.create(transaction)
        return [created]


class UpdateTransactionUseCase:
    """Atualiza uma transação existente.

    Permitido alterar: descrição, valor, categoria, data, efetivada.
    Regras:
    - A origem financeira NÃO pode ser alterada.
    - O impacto financeiro é recalculado automaticamente (saldo/limite on-demand).
    """

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo

    def execute(self, transaction_id: int, **kwargs) -> Transaction:
        """Executa a atualização da transação.

        Args:
            transaction_id: ID da transação a atualizar.
            **kwargs: Campos a alterar (descricao, valor, categoria_id, data, efetivada).

        Returns:
            Transação atualizada.

        Raises:
            ValueError: Se a transação ou categoria não existir, ou dados inválidos.
        """
        tx = self.transaction_repo.get_by_id(transaction_id)
        if tx is None:
            raise ValueError(
                f"Transação com id={transaction_id} não encontrada."
            )

        if "descricao" in kwargs:
            desc = kwargs["descricao"]
            if not desc or not desc.strip():
                raise ValueError("A descrição não pode ser vazia.")
            tx.descricao = desc.strip()

        if "valor" in kwargs:
            if kwargs["valor"] <= 0:
                raise ValueError("O valor deve ser maior que zero.")
            tx.valor = kwargs["valor"]

        if "categoria_id" in kwargs:
            cat = self.category_repo.get_by_id(kwargs["categoria_id"])
            if cat is None:
                raise ValueError(
                    f"Categoria com id={kwargs['categoria_id']} não encontrada."
                )
            tx.categoria_id = kwargs["categoria_id"]

        if "data" in kwargs:
            tx.data = kwargs["data"]

        if "efetivada" in kwargs:
            tx.efetivada = kwargs["efetivada"]

        return self.transaction_repo.update(tx)


class DeleteTransactionUseCase:
    """Remove uma transação, desfazendo seu impacto financeiro.

    Regras:
    - Ao deletar, o saldo/limite é ajustado automaticamente
      (calculado on-demand nos repositórios).
    """

    def __init__(
        self, transaction_repo: TransactionRepository
    ) -> None:
        self.transaction_repo = transaction_repo

    def execute(self, transaction_id: int) -> None:
        """Executa a remoção da transação.

        Args:
            transaction_id: ID da transação a remover.

        Raises:
            ValueError: Se a transação não existir.
        """
        tx = self.transaction_repo.get_by_id(transaction_id)
        if tx is None:
            raise ValueError(
                f"Transação com id={transaction_id} não encontrada."
            )

        self.transaction_repo.delete(transaction_id)


class ListTransactionsUseCase:
    """Único use case de consulta de transações com filtros dinâmicos.

    Filtros suportados (todos opcionais e combináveis):
    - data_inicio, data_fim
    - categoria_id, conta_id
    - cartao_credito_id, cartao_beneficio_id
    - tipo_movimento, efetivada
    """

    def __init__(
        self, transaction_repo: TransactionRepository
    ) -> None:
        self.transaction_repo = transaction_repo

    def execute(self, usuario_id: int, **filters) -> list[Transaction]:
        """Lista transações com filtros dinâmicos.

        Args:
            usuario_id: ID do usuário (obrigatório).
            **filters: Filtros opcionais (data_inicio, data_fim, categoria_id,
                       conta_id, cartao_credito_id, cartao_beneficio_id,
                       tipo_movimento, efetivada).

        Returns:
            Lista de transações que atendem aos filtros.
        """
        return self.transaction_repo.list_with_filters(usuario_id, filters)


class PayCreditCardInvoiceUseCase:
    """Realiza o pagamento (parcial ou total) de uma fatura de cartão de crédito.

    Regras:
    - Cria transação de SAIDA na conta vinculada ao cartão.
    - Ao efetivar, libera limite proporcional (calculado on-demand).
    - Atualiza status da fatura: 'paga' se paga integralmente, 'parcial' caso contrário.

    Exemplo:
        Limite total = 1000, utilizado = 700, pagamento = 300
        Novo limite utilizado = 400 (liberado automaticamente ao mudar status).
    """

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        invoice_repo: InvoiceRepository,
        credit_card_repo: CreditCardRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.invoice_repo = invoice_repo
        self.credit_card_repo = credit_card_repo
        self.category_repo = category_repo

    def execute(
        self,
        usuario_id: int,
        invoice_id: int,
        valor_pago: float,
        categoria_id: int,
        data: datetime | None = None,
    ) -> Transaction:
        """Executa o pagamento da fatura.

        Args:
            usuario_id: ID do usuário.
            invoice_id: ID da fatura a pagar.
            valor_pago: Valor a ser pago.
            categoria_id: Categoria para a transação de pagamento.
            data: Data do pagamento (default: agora).

        Returns:
            Transação de pagamento criada.

        Raises:
            ValueError: Se a fatura não existir, já estiver paga, ou valor inválido.
        """
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if invoice is None:
            raise ValueError(f"Fatura com id={invoice_id} não encontrada.")

        if invoice.status == "paga":
            raise ValueError("Esta fatura já está totalmente paga.")

        if valor_pago <= 0:
            raise ValueError("O valor do pagamento deve ser maior que zero.")

        # Busca o cartão de crédito para obter a conta vinculada
        card = self.credit_card_repo.get_by_id(invoice.cartao_credito_id)
        if card is None:
            raise ValueError("Cartão de crédito associado não encontrado.")

        if card.conta_id is None:
            raise ValueError(
                "O cartão de crédito não possui conta bancária vinculada para pagamento."
            )

        # Cria transação de saída na conta vinculada
        if data is None:
            data = datetime.now()

        payment_tx = Transaction(
            usuario_id=usuario_id,
            descricao=f"Pagamento fatura {invoice.mes_referencia:02d}/{invoice.ano_referencia}",
            valor=valor_pago,
            categoria_id=categoria_id,
            tipo_movimento="saida",
            data=data,
            efetivada=True,
            conta_id=card.conta_id,
        )
        created = self.transaction_repo.create(payment_tx)

        # Atualiza status da fatura
        valor_restante = invoice.total_fatura - valor_pago
        if valor_restante <= 0:
            invoice.status = "paga"
        else:
            invoice.status = "parcial"

        self.invoice_repo.update(invoice)

        return created


class GenerateInvoiceUseCase:
    """Gera uma fatura para um cartão de crédito em um determinado mês/ano.

    Regras:
    - Soma todas as transações do cartão no período (parcelas que caem naquele mês).
    - Cria registro de fatura com status 'aberta'.
    - Vincula as transações à fatura gerada (via fatura_id).
    """

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        invoice_repo: InvoiceRepository,
        credit_card_repo: CreditCardRepository,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.invoice_repo = invoice_repo
        self.credit_card_repo = credit_card_repo

    def execute(
        self,
        usuario_id: int,
        cartao_credito_id: int,
        mes_referencia: int,
        ano_referencia: int,
    ) -> object:
        """Gera a fatura do cartão de crédito para o mês/ano.

        Args:
            usuario_id: ID do usuário.
            cartao_credito_id: ID do cartão de crédito.
            mes_referencia: Mês de referência (1-12).
            ano_referencia: Ano de referência.

        Returns:
            Fatura gerada (Invoice).

        Raises:
            ValueError: Se o cartão não existir ou a fatura já existir.
        """
        card = self.credit_card_repo.get_by_id(cartao_credito_id)
        if card is None:
            raise ValueError(
                f"Cartão de crédito com id={cartao_credito_id} não encontrado."
            )

        # Verifica se já existe fatura para este mês/ano
        existing = self.invoice_repo.find_by_cartao_mes(
            usuario_id, cartao_credito_id, mes_referencia, ano_referencia
        )
        if existing:
            raise ValueError(
                f"Já existe uma fatura para {mes_referencia:02d}/{ano_referencia} neste cartão."
            )

        # Busca todas as transações do cartão (saida, efetivada)
        all_transactions = self.transaction_repo.list_by_cartao_credito(
            cartao_credito_id
        )

        # Filtra transações cuja data (considerando parcela) cai no mês/ano
        transacoes_fatura = []
        total = 0.0

        for tx in all_transactions:
            if tx.tipo_movimento != "saida" or not tx.efetivada:
                continue
            if tx.fatura_id is not None:
                continue  # Já está em outra fatura

            tx_date = tx.data
            if tx_date is None:
                continue

            # Converte datetime para date se necessário
            if isinstance(tx_date, datetime):
                tx_date = tx_date.date()
            elif not isinstance(tx_date, date):
                tx_date = date(tx_date.year, tx_date.month, tx_date.day)

            if tx_date.month == mes_referencia and tx_date.year == ano_referencia:
                transacoes_fatura.append(tx)
                total += tx.valor

        # Cria a fatura
        from core.entity.invoice import Invoice

        fatura = Invoice(
            usuario_id=usuario_id,
            cartao_credito_id=cartao_credito_id,
            mes_referencia=mes_referencia,
            ano_referencia=ano_referencia,
            data_fechamento=date.today(),
            data_vencimento=date(ano_referencia, mes_referencia, card.dia_vencimento),
            total_fatura=round(total, 2),
            status="aberta",
        )
        created_invoice = self.invoice_repo.create(fatura)

        # Vincula as transações à fatura
        for tx in transacoes_fatura:
            tx.fatura_id = created_invoice.id
            self.transaction_repo.update(tx)

        return created_invoice
