### core/usecases/account_usecases.py
"""
Use cases relacionados a contas bancárias.
"""
from core.entity.account import Account
from core.validations import validar_nome_unico
from infra.repositories.account_repository import AccountRepository


class CreateAccountUseCase:
    """Cria uma nova conta bancária.

    Regras:
    - Nome obrigatório e único por usuário (case insensitive).
    - Saldo inicial obrigatório (default 0.0).
    """

    def __init__(self, account_repo: AccountRepository) -> None:
        self.account_repo = account_repo

    def execute(
        self,
        usuario_id: int,
        nome: str,
        tipo: str = "corrente",
        saldo_inicial: float = 0.0,
    ) -> Account:
        """Executa a criação da conta.

        Args:
            usuario_id: ID do usuário proprietário.
            nome: Nome da conta.
            tipo: Tipo da conta (corrente, poupanca, etc.).
            saldo_inicial: Saldo inicial da conta.

        Returns:
            Conta criada.

        Raises:
            ValueError: Se o nome for vazio ou já existir.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome da conta é obrigatório.")

        validar_nome_unico(self.account_repo, usuario_id, nome)

        account = Account(
            usuario_id=usuario_id,
            nome=nome.strip(),
            tipo=tipo,
            saldo_inicial=saldo_inicial,
        )
        return self.account_repo.create(account)


class UpdateAccountUseCase:
    """Atualiza uma conta existente.

    Permitido alterar: nome e saldo_inicial.
    Regras:
    - Nome deve permanecer único (excluindo a própria entidade).
    """

    def __init__(self, account_repo: AccountRepository) -> None:
        self.account_repo = account_repo

    def execute(
        self,
        account_id: int,
        usuario_id: int,
        nome: str | None = None,
        saldo_inicial: float | None = None,
    ) -> Account:
        """Executa a atualização da conta.

        Args:
            account_id: ID da conta a atualizar.
            usuario_id: ID do usuário (validação de unicidade).
            nome: Novo nome (None = mantém atual).
            saldo_inicial: Novo saldo inicial (None = mantém atual).

        Returns:
            Conta atualizada.

        Raises:
            ValueError: Se a conta não existir ou o nome já estiver em uso.
        """
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise ValueError(f"Conta com id={account_id} não encontrada.")

        if nome is not None:
            validar_nome_unico(
                self.account_repo, usuario_id, nome, entidade_id=account_id
            )
            account.nome = nome.strip()

        if saldo_inicial is not None:
            account.saldo_inicial = saldo_inicial

        return self.account_repo.update(account)


class DeleteAccountUseCase:
    """Remove uma conta e suas transações (cascade).

    Regras:
    - Remove transações relacionadas (cascade via banco).
    """

    def __init__(self, account_repo: AccountRepository) -> None:
        self.account_repo = account_repo

    def execute(self, account_id: int) -> None:
        """Executa a remoção da conta.

        Args:
            account_id: ID da conta a remover.

        Raises:
            ValueError: Se a conta não existir.
        """
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise ValueError(f"Conta com id={account_id} não encontrada.")

        self.account_repo.delete(account_id)
