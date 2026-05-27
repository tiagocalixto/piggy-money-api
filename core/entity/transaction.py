### core/entity/transaction.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Entidade de domínio: Transação financeira."""

    usuario_id: int
    descricao: str
    valor: float
    categoria_id: int
    tipo_movimento: str = "saida"  # entrada, saida
    data: datetime | None = None
    efetivada: bool = True
    conta_id: int | None = None
    cartao_credito_id: int | None = None
    cartao_beneficio_id: int | None = None
    parcelas_total: int = 1
    parcela_atual: int = 1
    transacao_original_id: int | None = None
    fatura_id: int | None = None
    id: int | None = None
