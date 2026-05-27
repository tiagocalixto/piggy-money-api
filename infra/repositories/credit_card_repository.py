### infra/repositories/credit_card_repository.py
"""
Repositório para operações com a entidade CartaoCredito (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.entity.credit_card import CreditCard
from infra.database.models import CartaoCredito


class CreditCardRepository:
    """Acesso a dados da entidade CreditCard."""

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
    def _to_entity(db_card: CartaoCredito) -> CreditCard:
        """Converte model ORM → entidade de domínio."""
        return CreditCard(
            id=db_card.id,
            usuario_id=db_card.usuario_id,
            nome=db_card.nome,
            limite_total=float(db_card.limite_total),
            dia_fechamento=db_card.dia_fechamento,
            dia_vencimento=db_card.dia_vencimento,
            conta_id=db_card.conta_id,
        )

    @staticmethod
    def _to_model(
        card: CreditCard, db_card: CartaoCredito | None = None
    ) -> CartaoCredito:
        """Converte entidade de domínio → model ORM."""
        target = db_card if db_card is not None else CartaoCredito()
        target.usuario_id = card.usuario_id
        target.nome = card.nome
        target.limite_total = card.limite_total
        target.dia_fechamento = card.dia_fechamento
        target.dia_vencimento = card.dia_vencimento
        target.conta_id = card.conta_id
        return target

    # ── operações CRUD ────────────────────────

    def create(self, card: CreditCard) -> CreditCard:
        """Cria um novo cartão de crédito no banco."""
        session = next(self.get_session())
        try:
            db_card = self._to_model(card)
            session.add(db_card)
            session.commit()
            session.refresh(db_card)
            return self._to_entity(db_card)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, card_id: int) -> CreditCard | None:
        """Busca cartão de crédito pelo ID."""
        session = next(self.get_session())
        try:
            db_card = session.get(CartaoCredito, card_id)
            return self._to_entity(db_card) if db_card else None
        finally:
            session.close()

    def list_by_usuario(self, usuario_id: int) -> list[CreditCard]:
        """Lista todos os cartões de crédito de um usuário."""
        session = next(self.get_session())
        try:
            db_cards = (
                session.query(CartaoCredito)
                .filter(CartaoCredito.usuario_id == usuario_id)
                .all()
            )
            return [self._to_entity(c) for c in db_cards]
        finally:
            session.close()

    def update(self, card: CreditCard) -> CreditCard:
        """Atualiza um cartão de crédito existente."""
        session = next(self.get_session())
        try:
            db_card = session.get(CartaoCredito, card.id)
            if db_card is None:
                raise ValueError(
                    f"Cartão de crédito com id={card.id} não encontrado."
                )
            self._to_model(card, db_card)
            session.commit()
            session.refresh(db_card)
            return self._to_entity(db_card)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, card_id: int) -> None:
        """Remove um cartão de crédito do banco."""
        session = next(self.get_session())
        try:
            db_card = session.get(CartaoCredito, card_id)
            if db_card is None:
                raise ValueError(
                    f"Cartão de crédito com id={card_id} não encontrado."
                )
            session.delete(db_card)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── consultas especializadas ──────────────

    def find_by_nome(self, usuario_id: int, nome: str) -> CreditCard | None:
        """Busca cartão de crédito por nome (case insensitive) para validação de unicidade."""
        session = next(self.get_session())
        try:
            db_card = (
                session.query(CartaoCredito)
                .filter(
                    CartaoCredito.usuario_id == usuario_id,
                    func.lower(CartaoCredito.nome) == nome.lower().strip(),
                )
                .first()
            )
            return self._to_entity(db_card) if db_card else None
        finally:
            session.close()
