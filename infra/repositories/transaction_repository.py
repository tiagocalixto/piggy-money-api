### infra/repositories/transaction_repository.py
"""
Repositório para operações com a entidade Transacao (MySQL ↔ domínio).
"""
from datetime import datetime
from typing import Any, Callable, Generator

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.entity.transaction import Transaction
from infra.database.models import FaturaCartao, StatusFatura, Transacao


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

    # ── consultas especializadas ──────────────

    def list_with_filters(
        self, usuario_id: int, filters: dict[str, Any]
    ) -> list[Transaction]:
        """Lista transações com filtros dinâmicos e combináveis.

        Args:
            usuario_id: ID do usuário (filtro obrigatório).
            filters: Dicionário com filtros opcionais:
                - data_inicio: datetime | None
                - data_fim: datetime | None
                - categoria_id: int | None
                - conta_id: int | None
                - cartao_credito_id: int | None
                - cartao_beneficio_id: int | None
                - tipo_movimento: str | None
                - efetivada: bool | None
        """
        session = next(self.get_session())
        try:
            query = session.query(Transacao).filter(
                Transacao.usuario_id == usuario_id
            )

            if filters.get("data_inicio"):
                query = query.filter(
                    Transacao.data >= filters["data_inicio"]
                )
            if filters.get("data_fim"):
                query = query.filter(
                    Transacao.data <= filters["data_fim"]
                )
            if filters.get("categoria_id") is not None:
                query = query.filter(
                    Transacao.categoria_id == filters["categoria_id"]
                )
            if filters.get("conta_id") is not None:
                query = query.filter(
                    Transacao.conta_id == filters["conta_id"]
                )
            if filters.get("cartao_credito_id") is not None:
                query = query.filter(
                    Transacao.cartao_credito_id
                    == filters["cartao_credito_id"]
                )
            if filters.get("cartao_beneficio_id") is not None:
                query = query.filter(
                    Transacao.cartao_beneficio_id
                    == filters["cartao_beneficio_id"]
                )
            if filters.get("tipo_movimento"):
                query = query.filter(
                    Transacao.tipo_movimento
                    == filters["tipo_movimento"]
                )
            if filters.get("efetivada") is not None:
                query = query.filter(
                    Transacao.efetivada == filters["efetivada"]
                )

            db_txs = query.order_by(Transacao.data.desc()).all()
            return [self._to_entity(tx) for tx in db_txs]
        finally:
            session.close()

    def list_by_conta(self, conta_id: int) -> list[Transaction]:
        """Lista transações de uma conta específica."""
        session = next(self.get_session())
        try:
            db_txs = (
                session.query(Transacao)
                .filter(Transacao.conta_id == conta_id)
                .order_by(Transacao.data.desc())
                .all()
            )
            return [self._to_entity(tx) for tx in db_txs]
        finally:
            session.close()

    def list_by_cartao_credito(
        self, cartao_credito_id: int
    ) -> list[Transaction]:
        """Lista transações de um cartão de crédito específico."""
        session = next(self.get_session())
        try:
            db_txs = (
                session.query(Transacao)
                .filter(
                    Transacao.cartao_credito_id == cartao_credito_id
                )
                .order_by(Transacao.data.desc())
                .all()
            )
            return [self._to_entity(tx) for tx in db_txs]
        finally:
            session.close()

    def list_by_cartao_beneficio(
        self, beneficio_id: int
    ) -> list[Transaction]:
        """Lista transações de um cartão de benefício específico."""
        session = next(self.get_session())
        try:
            db_txs = (
                session.query(Transacao)
                .filter(
                    Transacao.cartao_beneficio_id == beneficio_id
                )
                .order_by(Transacao.data.desc())
                .all()
            )
            return [self._to_entity(tx) for tx in db_txs]
        finally:
            session.close()

    def get_sum_by_conta(
        self, conta_id: int, tipo_movimento: str
    ) -> float:
        """Soma os valores das transações efetivadas de uma conta por tipo."""
        session = next(self.get_session())
        try:
            result = (
                session.query(func.coalesce(func.sum(Transacao.valor), 0.0))
                .filter(
                    Transacao.conta_id == conta_id,
                    Transacao.tipo_movimento == tipo_movimento,
                    Transacao.efetivada == True,
                )
                .scalar()
            )
            return float(result)
        finally:
            session.close()

    def get_sum_by_cartao_credito(self, cartao_credito_id: int) -> float:
        """Soma dos gastos (saidas) não pagos do cartão de crédito.

        Considera transações efetivadas do tipo 'saida' que estão
        vinculadas a faturas com status 'aberta' ou 'parcial',
        OU que ainda não possuem fatura vinculada.
        """
        session = next(self.get_session())
        try:
            # Transações em faturas abertas/parciais
            gastos_em_faturas_abertas = (
                session.query(func.coalesce(func.sum(Transacao.valor), 0.0))
                .join(FaturaCartao, Transacao.fatura_id == FaturaCartao.id)
                .filter(
                    Transacao.cartao_credito_id == cartao_credito_id,
                    Transacao.tipo_movimento == "saida",
                    Transacao.efetivada == True,
                    FaturaCartao.status.in_(
                        [StatusFatura.ABERTA, StatusFatura.PARCIAL]
                    ),
                )
                .scalar()
            )

            # Transações sem fatura vinculada (ainda não faturadas)
            gastos_sem_fatura = (
                session.query(func.coalesce(func.sum(Transacao.valor), 0.0))
                .filter(
                    Transacao.cartao_credito_id == cartao_credito_id,
                    Transacao.tipo_movimento == "saida",
                    Transacao.efetivada == True,
                    Transacao.fatura_id.is_(None),
                )
                .scalar()
            )

            return float(gastos_em_faturas_abertas) + float(gastos_sem_fatura)
        finally:
            session.close()
