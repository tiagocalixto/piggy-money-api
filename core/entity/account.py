### core/entity/account.py
from dataclasses import dataclass


@dataclass
class Account:
    """Entidade de domínio: Conta bancária do usuário."""

    usuario_id: int
    nome: str
    tipo: str = "corrente"
    saldo_inicial: float = 0.0
    id: int | None = None
