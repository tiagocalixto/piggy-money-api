### core/entity/benefit_card.py
from dataclasses import dataclass


@dataclass
class BenefitCard:
    """Entidade de domínio: Cartão de benefício (VR, VA, etc.)."""

    usuario_id: int
    nome: str
    tipo: str = "refeicao"  # refeicao, alimentacao, outros
    saldo_inicial: float = 0.0
    id: int | None = None
