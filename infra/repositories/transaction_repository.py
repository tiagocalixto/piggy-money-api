### infra/repositories/transaction_repository.py
"""
Repositório para operações com a entidade Transacao (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy.orm import Session

from core.entity.transaction import Transaction
from infra.database.models import Transacao


class TransactionRepository:
    """Acesso a dados da entidade Transaction."""

    def __init__(self, get_session_fn: Callable[[], Generator[Session, None, None]]) -> None:
        self.get_session = get_session_fn

    # ── helpers de conversão ──────────────────

    @staticmethod
    def _to_entity(db_tx: Transacao) -> Transaction:
        """Converte model ORM → entidade de domínio."""
        return Transaction(
            id=db_tx.id,
            usuario_id=db_tx.usuario_id,
            descricao=db_tx.descricao,
            valor=float(db_tx.valor),
            data=db_tx.data,
            categoria_id=db_tx.categoria_id,
            efetivada=db_tx.efetivada,
            tipo_movimento=db_tx.tipo_movimento.value
            if hasattr(db_tx.tipo_movimento, "value")
            else str(db_tx.tipo_movimento),
            conta_id=db_tx.conta_id,
            cartao_credito_id=db_tx.cartao_credito_id,
            cartao_beneficio_id=db_tx.cartao_beneficio_id,
            parcelas_total=db_tx.parcelas_total,
            parcela_atual=db_tx.parcela_atual,
            transacao_original_id=db_tx.transacao_original_id,
            fatura_id=db_tx.fatura_id,
        )

    @staticmethod
    def _to_model(
        transaction: Transaction, db_tx: Transacao | None = None
    ) -> Transacao:
        """Converte entidade de domínio → model ORM."""
        target = db_tx if db_tx is not None else Transacao()
        target.usuario_id = transaction.usuario_id
        target.descricao = transaction.descricao
        target.valor = transaction.valor
        target.categoria_id = transaction.categoria_id
        target.efetivada = transaction.efetivada
        target.tipo_movimento = transaction.tipo_movimento
        target.conta_id = transaction.conta_id
        target.cartao_credito_id = transaction.cartao_credito_id
        target.cartao_beneficio_id = transaction.cartao_beneficio_id
        target.parcelas_total = transaction.parcelas_total
        target.parcela_atual = transaction.parcela_atual
        target.transacao_original_id = transaction.transacao_original_id
        target.fatura_id = transaction.fatura_id
        # data é gerenciada pelo banco (default)
        if transaction.data is not None:
            target.data = transaction.data
        return target

    # ── operações CRUD ────────────────────────

    def create(self, transaction: Transaction) -> Transaction:
        """Cria uma nova transação no banco."""
        session = next(self.get_session())
        try:
            db_tx = self._to_model(transaction)
            session.add(db_tx)
            session.commit()
            session.refresh(db_tx)
            return self._to_entity(db_tx)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Busca transação pelo ID."""
        session = next(self.get_session())
        try:
            db_tx = session.get(Transacao, transaction_id)
            return self._to_entity(db_tx) if db_tx else None
        finally:
            session.close()

    def list_by_usuario(self, usuario_id: int) -> list[Transaction]:
        """Lista todas as transações de um usuário."""
        session = next(self.get_session())
        try:
            db_txs = (
                session.query(Transacao)
                .filter(Transacao.usuario_id == usuario_id)
                .order_by(Transacao.data.desc())
                .all()
            )
            return [self._to_entity(tx) for tx in db_txs]
        finally:
            session.close()

    def update(self, transaction: Transaction) -> Transaction:
        """Atualiza uma transação existente."""
        session = next(self.get_session())
        try:
            db_tx = session.get(Transacao, transaction.id)
            if db_tx is None:
                raise ValueError(
                    f"Transação com id={transaction.id} não encontrada."
                )
            self._to_model(transaction, db_tx)
            session.commit()
            session.refresh(db_tx)
            return self._to_entity(db_tx)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, transaction_id: int) -> None:
        """Remove uma transação do banco."""
        session = next(self.get_session())
        try:
            db_tx = session.get(Transacao, transaction_id)
            if db_tx is None:
                raise ValueError(
                    f"Transação com id={transaction_id} não encontrada."
                )
            session.delete(db_tx)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
