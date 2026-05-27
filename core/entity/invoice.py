### core/entity/invoice.py
from dataclasses import dataclass
from datetime import date


@dataclass
class Invoice:
    """Entidade de domínio: Fatura de cartão de crédito."""

    usuario_id: int
    cartao_credito_id: int
    mes_referencia: int
    ano_referencia: int
    data_fechamento: date | None = None
    data_vencimento: date | None = None
    total_fatura: float = 0.0
    status: str = "aberta"  # aberta, paga, parcial
    id: int | None = None
