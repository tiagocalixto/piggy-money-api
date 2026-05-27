### core/services/user_service.py
from core.entity.user import User
from infra.repositories.user_repository import UserRepository


class UserService:
    """Casos de uso relacionados ao usuário."""

    def __init__(self, user_repo: UserRepository) -> None:
        """
        Args:
            user_repo: Repositório de usuários (injeção manual).
        """
        self.user_repo = user_repo

    def register_user(
        self,
        nome: str,
        email: str | None = None,
        telefone: str | None = None,
        senha_hash: str | None = None,
    ) -> User:
        """Registra um novo usuário, validando unicidade de email/telefone."""
        if email:
            if self.user_repo.get_by_email(email):
                raise ValueError(f"Email '{email}' já cadastrado.")
        if telefone:
            if self.user_repo.get_by_telefone(telefone):
                raise ValueError(f"Telefone '{telefone}' já cadastrado.")

        user = User(
            nome=nome,
            email=email,
            telefone=telefone,
            senha_hash=senha_hash,
        )
        return self.user_repo.create(user)

    def get_user_by_id(self, user_id: int) -> User | None:
        """Busca usuário pelo ID."""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Busca usuário pelo email."""
        return self.user_repo.get_by_email(email)

    def get_user_by_telefone(self, telefone: str) -> User | None:
        """Busca usuário pelo telefone."""
        return self.user_repo.get_by_telefone(telefone)

    def update_user(self, user: User) -> User:
        """Atualiza dados de um usuário existente."""
        return self.user_repo.update(user)
