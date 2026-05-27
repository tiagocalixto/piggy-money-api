### infra/repositories/invoice_repository.py
"""
Repositório para operações com a entidade FaturaCartao (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.entity.invoice import Invoice
from infra.database.models import FaturaCartao, StatusFatura


class InvoiceRepository:
    """Acesso a dados da entidade Invoice (FaturaCartao)."""

    def __init__(
        self,
        get_session_fn: Callable[[], Generator[Session, None, None]],
    ) -> None:
        """
        Args:
            get_session_fn: Função geradora que retorna uma sessão do banco.
        """
        self.get_session = get_session_fn

    # ── helpers de conversão ──────────────────

    @staticmethod
    def _to_entity(db_invoice: FaturaCartao) -> Invoice:
        """Converte model ORM → entidade de domínio."""
        return Invoice(
            id=db_invoice.id,
            usuario_id=db_invoice.usuario_id,
            cartao_credito_id=db_invoice.cartao_credito_id,
            mes_referencia=db_invoice.mes_referencia,
            ano_referencia=db_invoice.ano_referencia,
            data_fechamento=db_invoice.data_fechamento,
            data_vencimento=db_invoice.data_vencimento,
            total_fatura=float(db_invoice.total_fatura),
            status=db_invoice.status.value
            if hasattr(db_invoice.status, "value")
            else str(db_invoice.status),
        )

    @staticmethod
    def _to_model(
        invoice: Invoice, db_invoice: FaturaCartao | None = None
    ) -> FaturaCartao:
        """Converte entidade de domínio → model ORM."""
        target = db_invoice if db_invoice is not None else FaturaCartao()
        target.usuario_id = invoice.usuario_id
        target.cartao_credito_id = invoice.cartao_credito_id
        target.mes_referencia = invoice.mes_referencia
        target.ano_referencia = invoice.ano_referencia
        target.data_fechamento = invoice.data_fechamento
        target.data_vencimento = invoice.data_vencimento
        target.total_fatura = invoice.total_fatura
        target.status = invoice.status
        return target

    # ── operações CRUD ────────────────────────

    def create(self, invoice: Invoice) -> Invoice:
        """Cria uma nova fatura no banco."""
        session = next(self.get_session())
        try:
            db_invoice = self._to_model(invoice)
            session.add(db_invoice)
            session.commit()
            session.refresh(db_invoice)
            return self._to_entity(db_invoice)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, invoice_id: int) -> Invoice | None:
        """Busca fatura pelo ID."""
        session = next(self.get_session())
        try:
            db_invoice = session.get(FaturaCartao, invoice_id)
            return self._to_entity(db_invoice) if db_invoice else None
        finally:
            session.close()

    def list_by_usuario(self, usuario_id: int) -> list[Invoice]:
        """Lista todas as faturas de um usuário."""
        session = next(self.get_session())
        try:
            db_invoices = (
                session.query(FaturaCartao)
                .filter(FaturaCartao.usuario_id == usuario_id)
                .order_by(
                    FaturaCartao.ano_referencia.desc(),
                    FaturaCartao.mes_referencia.desc(),
                )
                .all()
            )
            return [self._to_entity(inv) for inv in db_invoices]
        finally:
            session.close()

    def update(self, invoice: Invoice) -> Invoice:
        """Atualiza uma fatura existente."""
        session = next(self.get_session())
        try:
            db_invoice = session.get(FaturaCartao, invoice.id)
            if db_invoice is None:
                raise ValueError(
                    f"Fatura com id={invoice.id} não encontrada."
                )
            self._to_model(invoice, db_invoice)
            session.commit()
            session.refresh(db_invoice)
            return self._to_entity(db_invoice)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, invoice_id: int) -> None:
        """Remove uma fatura do banco."""
        session = next(self.get_session())
        try:
            db_invoice = session.get(FaturaCartao, invoice_id)
            if db_invoice is None:
                raise ValueError(
                    f"Fatura com id={invoice_id} não encontrada."
                )
            session.delete(db_invoice)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── consultas especializadas ──────────────

    def find_by_cartao_mes(
        self, usuario_id: int, cartao_credito_id: int, mes: int, ano: int
    ) -> Invoice | None:
        """Busca fatura pelo cartão de crédito e mês/ano de referência."""
        session = next(self.get_session())
        try:
            db_invoice = (
                session.query(FaturaCartao)
                .filter(
                    FaturaCartao.usuario_id == usuario_id,
                    FaturaCartao.cartao_credito_id == cartao_credito_id,
                    FaturaCartao.mes_referencia == mes,
                    FaturaCartao.ano_referencia == ano,
                )
                .first()
            )
            return self._to_entity(db_invoice) if db_invoice else None
        finally:
            session.close()

    def find_abertas_by_cartao(
        self, usuario_id: int, cartao_credito_id: int
    ) -> list[Invoice]:
        """Lista faturas abertas (status 'aberta' ou 'parcial') de um cartão."""
        session = next(self.get_session())
        try:
            db_invoices = (
                session.query(FaturaCartao)
                .filter(
                    FaturaCartao.usuario_id == usuario_id,
                    FaturaCartao.cartao_credito_id == cartao_credito_id,
                    FaturaCartao.status.in_(
                        [StatusFatura.ABERTA, StatusFatura.PARCIAL]
                    ),
                )
                .all()
            )
            return [self._to_entity(inv) for inv in db_invoices]
        finally:
            session.close()
