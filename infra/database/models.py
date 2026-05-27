### infra/database/models.py
"""
Modelos ORM (SQLAlchemy 2.0+) — mapeamento direto das tabelas do MySQL.

Nomes em português combinando com o schema `piggy_money`.
"""
import enum
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""
    pass


# ──────────────────────────────────────────────
# Enums (combinam com os ENUMs do MySQL)
# ──────────────────────────────────────────────

class TipoPermitido(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"
    AMBOS = "ambos"


class StatusFatura(str, enum.Enum):
    ABERTA = "aberta"
    PAGA = "paga"
    PARCIAL = "parcial"


class TipoMovimento(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class TipoBeneficio(str, enum.Enum):
    REFEICAO = "refeicao"
    ALIMENTACAO = "alimentacao"
    OUTROS = "outros"


# ──────────────────────────────────────────────
# 1. Usuario
# ──────────────────────────────────────────────

class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )
    telefone: Mapped[Optional[str]] = mapped_column(
        String(30), unique=True, nullable=True
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Relationships
    contas: Mapped[List["Conta"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    cartoes_credito: Mapped[List["CartaoCredito"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    cartoes_beneficio: Mapped[List["CartaoBeneficio"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    categorias: Mapped[List["Categoria"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    faturas: Mapped[List["FaturaCartao"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    transacoes: Mapped[List["Transacao"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


# ──────────────────────────────────────────────
# 2. Conta
# ──────────────────────────────────────────────

class Conta(Base):
    __tablename__ = "conta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, default="corrente")
    saldo_inicial: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="contas")
    transacoes: Mapped[List["Transacao"]] = relationship(back_populates="conta")
    cartoes_credito: Mapped[List["CartaoCredito"]] = relationship(
        back_populates="conta"
    )


# ──────────────────────────────────────────────
# 3. CartaoCredito
# ──────────────────────────────────────────────

class CartaoCredito(Base):
    __tablename__ = "cartao_credito"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    limite_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    dia_fechamento: Mapped[int] = mapped_column(Integer, nullable=False)
    dia_vencimento: Mapped[int] = mapped_column(Integer, nullable=False)
    conta_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conta.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="cartoes_credito")
    conta: Mapped[Optional["Conta"]] = relationship(back_populates="cartoes_credito")
    faturas: Mapped[List["FaturaCartao"]] = relationship(
        back_populates="cartao_credito", cascade="all, delete-orphan"
    )
    transacoes: Mapped[List["Transacao"]] = relationship(
        back_populates="cartao_credito"
    )


# ──────────────────────────────────────────────
# 4. CartaoBeneficio
# ──────────────────────────────────────────────

class CartaoBeneficio(Base):
    __tablename__ = "cartao_beneficio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoBeneficio] = mapped_column(
        Enum(TipoBeneficio), nullable=False
    )
    saldo_inicial: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="cartoes_beneficio")
    transacoes: Mapped[List["Transacao"]] = relationship(
        back_populates="cartao_beneficio"
    )


# ──────────────────────────────────────────────
# 5. Categoria
# ──────────────────────────────────────────────

class Categoria(Base):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_permitido: Mapped[TipoPermitido] = mapped_column(
        Enum(TipoPermitido), default=TipoPermitido.AMBOS
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="categorias")
    transacoes: Mapped[List["Transacao"]] = relationship(
        back_populates="categoria"
    )


# ──────────────────────────────────────────────
# 6. FaturaCartao
# ──────────────────────────────────────────────

class FaturaCartao(Base):
    __tablename__ = "fatura_cartao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    cartao_credito_id: Mapped[int] = mapped_column(
        ForeignKey("cartao_credito.id", ondelete="CASCADE"), nullable=False
    )
    mes_referencia: Mapped[int] = mapped_column(Integer, nullable=False)
    ano_referencia: Mapped[int] = mapped_column(Integer, nullable=False)
    data_fechamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_vencimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_fatura: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    status: Mapped[StatusFatura] = mapped_column(
        Enum(StatusFatura), default=StatusFatura.ABERTA
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="faturas")
    cartao_credito: Mapped["CartaoCredito"] = relationship(back_populates="faturas")
    transacoes: Mapped[List["Transacao"]] = relationship(back_populates="fatura")


# ──────────────────────────────────────────────
# 7. Transacao
# ──────────────────────────────────────────────

class Transacao(Base):
    __tablename__ = "transacao"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    descricao: Mapped[str] = mapped_column(String(500), nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    data: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categoria.id", ondelete="CASCADE"), nullable=False
    )
    efetivada: Mapped[bool] = mapped_column(Boolean, default=True)
    tipo_movimento: Mapped[TipoMovimento] = mapped_column(
        Enum(TipoMovimento), default=TipoMovimento.SAIDA
    )

    # FKs opcionais
    conta_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("conta.id", ondelete="SET NULL"), nullable=True
    )
    cartao_credito_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cartao_credito.id", ondelete="SET NULL"), nullable=True
    )
    cartao_beneficio_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("cartao_beneficio.id", ondelete="SET NULL"), nullable=True
    )
    parcelas_total: Mapped[int] = mapped_column(Integer, default=1)
    parcela_atual: Mapped[int] = mapped_column(Integer, default=1)
    transacao_original_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("transacao.id", ondelete="SET NULL"), nullable=True
    )
    fatura_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("fatura_cartao.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship(back_populates="transacoes")
    categoria: Mapped["Categoria"] = relationship(back_populates="transacoes")
    conta: Mapped[Optional["Conta"]] = relationship(back_populates="transacoes")
    cartao_credito: Mapped[Optional["CartaoCredito"]] = relationship(
        back_populates="transacoes"
    )
    cartao_beneficio: Mapped[Optional["CartaoBeneficio"]] = relationship(
        back_populates="transacoes"
    )
    fatura: Mapped[Optional["FaturaCartao"]] = relationship(
        back_populates="transacoes"
    )

    # Self-referential: parcelamento
    transacao_original: Mapped[Optional["Transacao"]] = relationship(
        "Transacao",
        remote_side="Transacao.id",
        back_populates="parcelas",
        foreign_keys=[transacao_original_id],
    )
    parcelas: Mapped[List["Transacao"]] = relationship(
        "Transacao",
        back_populates="transacao_original",
        foreign_keys=[transacao_original_id],
    )
