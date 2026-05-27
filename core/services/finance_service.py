### core/services/finance_service.py
from typing import Any

from core.entity.account import Account
from core.entity.category import Category
from core.entity.transaction import Transaction
from infra.repositories.account_repository import AccountRepository
from infra.repositories.category_repository import CategoryRepository
from infra.repositories.transaction_repository import TransactionRepository


class FinanceService:
    """Casos de uso relacionados a finanças (contas, categorias, transações)."""

    def __init__(
        self,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.category_repo = category_repo

    # --- Contas ---

    def create_account(
        self,
        usuario_id: int,
        nome: str,
        tipo: str = "corrente",
        saldo_inicial: float = 0.0,
    ) -> Account:
        """Cria uma nova conta bancária para o usuário."""
        account = Account(
            usuario_id=usuario_id,
            nome=nome,
            tipo=tipo,
            saldo_inicial=saldo_inicial,
        )
        return self.account_repo.create(account)

    def get_user_accounts(self, usuario_id: int) -> list[Account]:
        """Lista todas as contas de um usuário."""
        return self.account_repo.list_by_usuario(usuario_id)

    # --- Categorias ---

    def create_category(
        self,
        usuario_id: int,
        nome: str,
        tipo_permitido: str = "ambos",
    ) -> Category:
        """Cria uma nova categoria para o usuário."""
        category = Category(
            usuario_id=usuario_id,
            nome=nome,
            tipo_permitido=tipo_permitido,
        )
        return self.category_repo.create(category)

    def get_user_categories(self, usuario_id: int) -> list[Category]:
        """Lista todas as categorias de um usuário."""
        return self.category_repo.list_by_usuario(usuario_id)

    # --- Transações ---

    def create_transaction(
        self,
        usuario_id: int,
        descricao: str,
        valor: float,
        categoria_id: int,
        tipo_movimento: str = "saida",
        **kwargs: Any,
    ) -> Transaction:
        """Cria uma nova transação financeira."""
        transaction = Transaction(
            usuario_id=usuario_id,
            descricao=descricao,
            valor=valor,
            categoria_id=categoria_id,
            tipo_movimento=tipo_movimento,
            **kwargs,
        )
        return self.transaction_repo.create(transaction)

    def get_user_transactions(self, usuario_id: int) -> list[Transaction]:
        """Lista todas as transações de um usuário."""
        return self.transaction_repo.list_by_usuario(usuario_id)
