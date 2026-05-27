### core/entity/credit_card.py
from dataclasses import dataclass


@dataclass
class CreditCard:
    """Entidade de domínio: Cartão de crédito."""

    usuario_id: int
    nome: str
    limite_total: float = 0.0
    dia_fechamento: int = 1
    dia_vencimento: int = 10
    conta_id: int | None = None
    id: int | None = None
