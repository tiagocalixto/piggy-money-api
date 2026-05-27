### core/usecases/credit_card_usecases.py
"""
Use cases relacionados a cartões de crédito.
"""
from core.entity.credit_card import CreditCard
from core.validations import validar_nome_unico
from infra.repositories.credit_card_repository import CreditCardRepository


class CreateCreditCardUseCase:
    """Cria um novo cartão de crédito.

    Regras:
    - Nome único por usuário (case insensitive).
    - Limite, dia_fechamento e dia_vencimento obrigatórios.
    - Conta associada é opcional.
    """

    def __init__(self, credit_card_repo: CreditCardRepository) -> None:
        self.credit_card_repo = credit_card_repo

    def execute(
        self,
        usuario_id: int,
        nome: str,
        limite_total: float,
        dia_fechamento: int,
        dia_vencimento: int,
        conta_id: int | None = None,
    ) -> CreditCard:
        """Executa a criação do cartão de crédito.

        Args:
            usuario_id: ID do usuário proprietário.
            nome: Nome do cartão.
            limite_total: Limite total do cartão.
            dia_fechamento: Dia do mês de fechamento da fatura.
            dia_vencimento: Dia do mês de vencimento da fatura.
            conta_id: ID da conta bancária associada (opcional).

        Returns:
            Cartão de crédito criado.

        Raises:
            ValueError: Se o nome for vazio, já existir, ou dados inválidos.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome do cartão de crédito é obrigatório.")

        if limite_total < 0:
            raise ValueError("O limite total não pode ser negativo.")

        if not (1 <= dia_fechamento <= 31):
            raise ValueError("Dia de fechamento deve estar entre 1 e 31.")

        if not (1 <= dia_vencimento <= 31):
            raise ValueError("Dia de vencimento deve estar entre 1 e 31.")

        validar_nome_unico(self.credit_card_repo, usuario_id, nome)

        card = CreditCard(
            usuario_id=usuario_id,
            nome=nome.strip(),
            limite_total=limite_total,
            dia_fechamento=dia_fechamento,
            dia_vencimento=dia_vencimento,
            conta_id=conta_id,
        )
        return self.credit_card_repo.create(card)


class UpdateCreditCardUseCase:
    """Atualiza um cartão de crédito existente.

    Permitido alterar: nome, limite_total, dia_fechamento, dia_vencimento, conta_id.
    Regras:
    - Nome deve permanecer único (excluindo a si mesmo).
    """

    def __init__(self, credit_card_repo: CreditCardRepository) -> None:
        self.credit_card_repo = credit_card_repo

    def execute(self, card_id: int, usuario_id: int, **kwargs) -> CreditCard:
        """Executa a atualização do cartão de crédito.

        Args:
            card_id: ID do cartão a atualizar.
            usuario_id: ID do usuário (validação de unicidade).
            **kwargs: Campos a atualizar (nome, limite_total, dia_fechamento,
                      dia_vencimento, conta_id).

        Returns:
            Cartão de crédito atualizado.

        Raises:
            ValueError: Se o cartão não existir ou dados inválidos.
        """
        card = self.credit_card_repo.get_by_id(card_id)
        if card is None:
            raise ValueError(
                f"Cartão de crédito com id={card_id} não encontrado."
            )

        if "nome" in kwargs:
            nome = kwargs["nome"]
            if not nome or not nome.strip():
                raise ValueError("O nome do cartão não pode ser vazio.")
            validar_nome_unico(
                self.credit_card_repo,
                usuario_id,
                nome,
                entidade_id=card_id,
            )
            card.nome = nome.strip()

        if "limite_total" in kwargs:
            if kwargs["limite_total"] < 0:
                raise ValueError("O limite total não pode ser negativo.")
            card.limite_total = kwargs["limite_total"]

        if "dia_fechamento" in kwargs:
            df = kwargs["dia_fechamento"]
            if not (1 <= df <= 31):
                raise ValueError("Dia de fechamento deve estar entre 1 e 31.")
            card.dia_fechamento = df

        if "dia_vencimento" in kwargs:
            dv = kwargs["dia_vencimento"]
            if not (1 <= dv <= 31):
                raise ValueError("Dia de vencimento deve estar entre 1 e 31.")
            card.dia_vencimento = dv

        if "conta_id" in kwargs:
            card.conta_id = kwargs["conta_id"]

        return self.credit_card_repo.update(card)


class DeleteCreditCardUseCase:
    """Remove um cartão de crédito e seus dados associados (cascade).

    Regras:
    - Remove transações e faturas relacionadas (cascade via banco).
    """

    def __init__(self, credit_card_repo: CreditCardRepository) -> None:
        self.credit_card_repo = credit_card_repo

    def execute(self, card_id: int) -> None:
        """Executa a remoção do cartão de crédito.

        Args:
            card_id: ID do cartão a remover.

        Raises:
            ValueError: Se o cartão não existir.
        """
        card = self.credit_card_repo.get_by_id(card_id)
        if card is None:
            raise ValueError(
                f"Cartão de crédito com id={card_id} não encontrado."
            )

        self.credit_card_repo.delete(card_id)
