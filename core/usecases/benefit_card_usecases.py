### core/usecases/benefit_card_usecases.py
"""
Use cases relacionados a cartões de benefício (VR, VA, etc.).
"""
from core.entity.benefit_card import BenefitCard
from core.validations import validar_nome_unico
from infra.repositories.benefit_card_repository import BenefitCardRepository


class CreateBenefitCardUseCase:
    """Cria um novo cartão de benefício.

    Regras:
    - Nome único por usuário (case insensitive).
    """

    def __init__(self, benefit_card_repo: BenefitCardRepository) -> None:
        self.benefit_card_repo = benefit_card_repo

    def execute(
        self,
        usuario_id: int,
        nome: str,
        tipo: str = "refeicao",
        saldo_inicial: float = 0.0,
    ) -> BenefitCard:
        """Executa a criação do cartão de benefício.

        Args:
            usuario_id: ID do usuário proprietário.
            nome: Nome do cartão.
            tipo: Tipo do benefício (refeicao, alimentacao, outros).
            saldo_inicial: Saldo inicial do cartão.

        Returns:
            Cartão de benefício criado.

        Raises:
            ValueError: Se o nome for vazio ou já existir.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome do cartão de benefício é obrigatório.")

        validar_nome_unico(self.benefit_card_repo, usuario_id, nome)

        card = BenefitCard(
            usuario_id=usuario_id,
            nome=nome.strip(),
            tipo=tipo,
            saldo_inicial=saldo_inicial,
        )
        return self.benefit_card_repo.create(card)


class UpdateBenefitCardUseCase:
    """Atualiza um cartão de benefício existente.

    Permitido alterar: nome e saldo_inicial.
    Regras:
    - Nome deve permanecer único (excluindo a si mesmo).
    """

    def __init__(self, benefit_card_repo: BenefitCardRepository) -> None:
        self.benefit_card_repo = benefit_card_repo

    def execute(
        self,
        card_id: int,
        usuario_id: int,
        nome: str | None = None,
        saldo_inicial: float | None = None,
    ) -> BenefitCard:
        """Executa a atualização do cartão de benefício.

        Args:
            card_id: ID do cartão a atualizar.
            usuario_id: ID do usuário (validação de unicidade).
            nome: Novo nome (None = mantém atual).
            saldo_inicial: Novo saldo inicial (None = mantém atual).

        Returns:
            Cartão de benefício atualizado.

        Raises:
            ValueError: Se o cartão não existir ou o nome já estiver em uso.
        """
        card = self.benefit_card_repo.get_by_id(card_id)
        if card is None:
            raise ValueError(
                f"Cartão de benefício com id={card_id} não encontrado."
            )

        if nome is not None:
            validar_nome_unico(
                self.benefit_card_repo,
                usuario_id,
                nome,
                entidade_id=card_id,
            )
            card.nome = nome.strip()

        if saldo_inicial is not None:
            card.saldo_inicial = saldo_inicial

        return self.benefit_card_repo.update(card)


class DeleteBenefitCardUseCase:
    """Remove um cartão de benefício e suas transações (cascade).

    Regras:
    - Remove transações relacionadas (cascade via banco).
    """

    def __init__(self, benefit_card_repo: BenefitCardRepository) -> None:
        self.benefit_card_repo = benefit_card_repo

    def execute(self, card_id: int) -> None:
        """Executa a remoção do cartão de benefício.

        Args:
            card_id: ID do cartão a remover.

        Raises:
            ValueError: Se o cartão não existir.
        """
        card = self.benefit_card_repo.get_by_id(card_id)
        if card is None:
            raise ValueError(
                f"Cartão de benefício com id={card_id} não encontrado."
            )

        self.benefit_card_repo.delete(card_id)
