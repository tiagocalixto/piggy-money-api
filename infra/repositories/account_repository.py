### infra/repositories/account_repository.py
"""
Repositório para operações com a entidade Conta (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy.orm import Session

from core.entity.account import Account
from infra.database.models import Conta


class AccountRepository:
    """Acesso a dados da entidade Account."""

    def __init__(self, get_session_fn: Callable[[], Generator[Session, None, None]]) -> None:
        self.get_session = get_session_fn

    # ── helpers de conversão ──────────────────

    @staticmethod
    def _to_entity(db_account: Conta) -> Account:
        """Converte model ORM → entidade de domínio."""
        return Account(
            id=db_account.id,
            usuario_id=db_account.usuario_id,
            nome=db_account.nome,
            tipo=db_account.tipo,
            saldo_inicial=float(db_account.saldo_inicial),
        )

    @staticmethod
    def _to_model(account: Account, db_account: Conta | None = None) -> Conta:
        """Converte entidade de domínio → model ORM."""
        target = db_account if db_account is not None else Conta()
        target.usuario_id = account.usuario_id
        target.nome = account.nome
        target.tipo = account.tipo
        target.saldo_inicial = account.saldo_inicial
        return target

    # ── operações CRUD ────────────────────────

    def create(self, account: Account) -> Account:
        """Cria uma nova conta no banco."""
        session = next(self.get_session())
        try:
            db_account = self._to_model(account)
            session.add(db_account)
            session.commit()
            session.refresh(db_account)
            return self._to_entity(db_account)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, account_id: int) -> Account | None:
        """Busca conta pelo ID."""
        session = next(self.get_session())
        try:
            db_account = session.get(Conta, account_id)
            return self._to_entity(db_account) if db_account else None
        finally:
            session.close()

    def list_by_usuario(self, usuario_id: int) -> list[Account]:
        """Lista todas as contas de um usuário."""
        session = next(self.get_session())
        try:
            db_accounts = (
                session.query(Conta)
                .filter(Conta.usuario_id == usuario_id)
                .all()
            )
            return [self._to_entity(a) for a in db_accounts]
        finally:
            session.close()

    def update(self, account: Account) -> Account:
        """Atualiza uma conta existente."""
        session = next(self.get_session())
        try:
            db_account = session.get(Conta, account.id)
            if db_account is None:
                raise ValueError(f"Conta com id={account.id} não encontrada.")
            self._to_model(account, db_account)
            session.commit()
            session.refresh(db_account)
            return self._to_entity(db_account)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, account_id: int) -> None:
        """Remove uma conta do banco."""
        session = next(self.get_session())
        try:
            db_account = session.get(Conta, account_id)
            if db_account is None:
                raise ValueError(f"Conta com id={account_id} não encontrada.")
            session.delete(db_account)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
