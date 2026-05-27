### infra/repositories/category_repository.py
"""
Repositório para operações com a entidade Categoria (MySQL ↔ domínio).
"""
from typing import Callable, Generator

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.entity.category import Category
from core.entity.transaction import Transaction
from infra.database.models import Categoria, Transacao


class CategoryRepository:
    """Acesso a dados da entidade Category."""

    def __init__(self, get_session_fn: Callable[[], Generator[Session, None, None]]) -> None:
        self.get_session = get_session_fn

    # ── helpers de conversão ──────────────────

    @staticmethod
    def _to_entity(db_cat: Categoria) -> Category:
        """Converte model ORM → entidade de domínio."""
        return Category(
            id=db_cat.id,
            usuario_id=db_cat.usuario_id,
            nome=db_cat.nome,
            tipo_permitido=db_cat.tipo_permitido.value
            if hasattr(db_cat.tipo_permitido, "value")
            else str(db_cat.tipo_permitido),
        )

    @staticmethod
    def _to_model(
        category: Category, db_cat: Categoria | None = None
    ) -> Categoria:
        """Converte entidade de domínio → model ORM."""
        target = db_cat if db_cat is not None else Categoria()
        target.usuario_id = category.usuario_id
        target.nome = category.nome
        target.tipo_permitido = category.tipo_permitido
        return target

    # ── operações CRUD ────────────────────────

    def create(self, category: Category) -> Category:
        """Cria uma nova categoria no banco."""
        session = next(self.get_session())
        try:
            db_cat = self._to_model(category)
            session.add(db_cat)
            session.commit()
            session.refresh(db_cat)
            return self._to_entity(db_cat)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_by_id(self, category_id: int) -> Category | None:
        """Busca categoria pelo ID."""
        session = next(self.get_session())
        try:
            db_cat = session.get(Categoria, category_id)
            return self._to_entity(db_cat) if db_cat else None
        finally:
            session.close()

    def list_by_usuario(self, usuario_id: int) -> list[Category]:
        """Lista todas as categorias de um usuário."""
        session = next(self.get_session())
        try:
            db_cats = (
                session.query(Categoria)
                .filter(Categoria.usuario_id == usuario_id)
                .all()
            )
            return [self._to_entity(c) for c in db_cats]
        finally:
            session.close()

    def update(self, category: Category) -> Category:
        """Atualiza uma categoria existente."""
        session = next(self.get_session())
        try:
            db_cat = session.get(Categoria, category.id)
            if db_cat is None:
                raise ValueError(
                    f"Categoria com id={category.id} não encontrada."
                )
            self._to_model(category, db_cat)
            session.commit()
            session.refresh(db_cat)
            return self._to_entity(db_cat)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, category_id: int) -> None:
        """Remove uma categoria do banco."""
        session = next(self.get_session())
        try:
            db_cat = session.get(Categoria, category_id)
            if db_cat is None:
                raise ValueError(
                    f"Categoria com id={category_id} não encontrada."
                )
            session.delete(db_cat)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    # ── consultas especializadas ──────────────

    def find_by_nome(self, usuario_id: int, nome: str) -> Category | None:
        """Busca categoria por nome (case insensitive) para validação de unicidade."""
        session = next(self.get_session())
        try:
            db_cat = (
                session.query(Categoria)
                .filter(
                    Categoria.usuario_id == usuario_id,
                    func.lower(Categoria.nome) == nome.lower().strip(),
                )
                .first()
            )
            return self._to_entity(db_cat) if db_cat else None
        finally:
            session.close()

    def find_default_category(self, usuario_id: int) -> Category | None:
        """Busca a categoria 'Sem categoria' do usuário."""
        return self.find_by_nome(usuario_id, "Sem categoria")

    def list_transactions_by_category(
        self, categoria_id: int
    ) -> list[Transaction]:
        """Lista todas as transações vinculadas a uma categoria."""
        session = next(self.get_session())
        try:
            db_txs = (
                session.query(Transacao)
                .filter(Transacao.categoria_id == categoria_id)
                .all()
            )
            from infra.repositories.transaction_repository import (
                TransactionRepository,
            )

            return [
                TransactionRepository._to_entity(tx) for tx in db_txs
            ]
        finally:
            session.close()
