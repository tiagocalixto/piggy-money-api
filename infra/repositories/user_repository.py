### infra/repositories/user_repository.py
"""
Repositório para operações com a entidade Usuario (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy.orm import Session

from core.entity.user import User
from infra.database.models import Usuario


class UserRepository:
    """Acesso a dados da entidade User."""

    def __init__(self, get_session_fn: Callable[[], Generator[Session, None, None]]) -> None:
        """
        Args:
            get_session_fn: Função geradora que retorna uma sessão do banco.
        """
        self.get_session = get_session_fn

    # ── helpers de conversão ──────────────────

    @staticmethod
    def _to_entity(db_user: Usuario) -> User:
        """Converte model ORM → entidade de domínio."""
        return User(
            id=db_user.id,
            nome=db_user.nome,
            email=db_user.email,
            telefone=db_user.telefone,
            senha_hash=db_user.senha_hash,
            data_criacao=db_user.data_criacao,
        )

    @staticmethod
    def _to_model(user: User, db_user: Usuario | None = None) -> Usuario:
        """Converte entidade de domínio → model ORM."""
        target = db_user if db_user is not None else Usuario()
        target.nome = user.nome
        target.email = user.email
        target.telefone = user.telefone
        target.senha_hash = user.senha_hash
        # data_criacao e id são gerenciados pelo banco
        return target

    # ── operações CRUD ────────────────────────

    def create(self, user: User) -> User:
        """Cria um novo usuário no banco."""
        session = next(self.get_session())
        try:
            db_user = self._to_model(user)
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return self._to_entity(db_user)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, user_id: int) -> User | None:
        """Busca usuário pelo ID."""
        session = next(self.get_session())
        try:
            db_user = session.get(Usuario, user_id)
            return self._to_entity(db_user) if db_user else None
        finally:
            session.close()

    def get_by_email(self, email: str) -> User | None:
        """Busca usuário pelo email."""
        session = next(self.get_session())
        try:
            db_user = (
                session.query(Usuario)
                .filter(Usuario.email == email)
                .first()
            )
            return self._to_entity(db_user) if db_user else None
        finally:
            session.close()

    def get_by_telefone(self, telefone: str) -> User | None:
        """Busca usuário pelo telefone."""
        session = next(self.get_session())
        try:
            db_user = (
                session.query(Usuario)
                .filter(Usuario.telefone == telefone)
                .first()
            )
            return self._to_entity(db_user) if db_user else None
        finally:
            session.close()

    def list(self) -> list[User]:
        """Lista todos os usuários."""
        session = next(self.get_session())
        try:
            db_users = session.query(Usuario).all()
            return [self._to_entity(u) for u in db_users]
        finally:
            session.close()

    def update(self, user: User) -> User:
        """Atualiza os dados de um usuário existente."""
        session = next(self.get_session())
        try:
            db_user = session.get(Usuario, user.id)
            if db_user is None:
                raise ValueError(f"Usuário com id={user.id} não encontrado.")
            self._to_model(user, db_user)
            session.commit()
            session.refresh(db_user)
            return self._to_entity(db_user)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, user_id: int) -> None:
        """Remove um usuário do banco."""
        session = next(self.get_session())
        try:
            db_user = session.get(Usuario, user_id)
            if db_user is None:
                raise ValueError(f"Usuário com id={user_id} não encontrado.")
            session.delete(db_user)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
