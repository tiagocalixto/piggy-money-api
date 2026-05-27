### infra/repositories/benefit_card_repository.py
"""
Repositório para operações com a entidade CartaoBeneficio (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.entity.benefit_card import BenefitCard
from infra.database.models import CartaoBeneficio


class BenefitCardRepository:
    """Acesso a dados da entidade BenefitCard."""

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
    def _to_entity(db_card: CartaoBeneficio) -> BenefitCard:
        """Converte model ORM → entidade de domínio."""
        return BenefitCard(
            id=db_card.id,
            usuario_id=db_card.usuario_id,
            nome=db_card.nome,
            tipo=db_card.tipo.value
            if hasattr(db_card.tipo, "value")
            else str(db_card.tipo),
            saldo_inicial=float(db_card.saldo_inicial),
        )

    @staticmethod
    def _to_model(
        card: BenefitCard, db_card: CartaoBeneficio | None = None
    ) -> CartaoBeneficio:
        """Converte entidade de domínio → model ORM."""
        target = db_card if db_card is not None else CartaoBeneficio()
        target.usuario_id = card.usuario_id
        target.nome = card.nome
        target.tipo = card.tipo
        target.saldo_inicial = card.saldo_inicial
        return target

    # ── operações CRUD ────────────────────────

    def create(self, card: BenefitCard) -> BenefitCard:
        """Cria um novo cartão de benefício no banco."""
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

    def get_by_id(self, card_id: int) -> BenefitCard | None:
        """Busca cartão de benefício pelo ID."""
        session = next(self.get_session())
        try:
            db_card = session.get(CartaoBeneficio, card_id)
            return self._to_entity(db_card) if db_card else None
        finally:
            session.close()

    def list_by_usuario(self, usuario_id: int) -> list[BenefitCard]:
        """Lista todos os cartões de benefício de um usuário."""
        session = next(self.get_session())
        try:
            db_cards = (
                session.query(CartaoBeneficio)
                .filter(CartaoBeneficio.usuario_id == usuario_id)
                .all()
            )
            return [self._to_entity(c) for c in db_cards]
        finally:
            session.close()

    def update(self, card: BenefitCard) -> BenefitCard:
        """Atualiza um cartão de benefício existente."""
        session = next(self.get_session())
        try:
            db_card = session.get(CartaoBeneficio, card.id)
            if db_card is None:
                raise ValueError(
                    f"Cartão de benefício com id={card.id} não encontrado."
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
        """Remove um cartão de benefício do banco."""
        session = next(self.get_session())
        try:
            db_card = session.get(CartaoBeneficio, card_id)
            if db_card is None:
                raise ValueError(
                    f"Cartão de benefício com id={card_id} não encontrado."
                )
            session.delete(db_card)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── consultas especializadas ──────────────

    def find_by_nome(self, usuario_id: int, nome: str) -> BenefitCard | None:
        """Busca cartão de benefício por nome (case insensitive) para validação de unicidade."""
        session = next(self.get_session())
        try:
            db_card = (
                session.query(CartaoBeneficio)
                .filter(
                    CartaoBeneficio.usuario_id == usuario_id,
                    func.lower(CartaoBeneficio.nome) == nome.lower().strip(),
                )
                .first()
            )
            return self._to_entity(db_card) if db_card else None
        finally:
            session.close()
