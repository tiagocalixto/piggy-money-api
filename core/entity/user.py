### core/entity/user.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Entidade de domínio: Usuário do bot financeiro."""

    nome: str
    id: int | None = None
    email: str | None = None
    telefone: str | None = None
    senha_hash: str | None = None
    data_criacao: datetime | None = None
