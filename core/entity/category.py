### core/entity/category.py
from dataclasses import dataclass


@dataclass
class Category:
    """Entidade de domínio: Categoria de transações."""

    usuario_id: int
    nome: str
    tipo_permitido: str = "ambos"  # entrada, saida, ambos
    id: int | None = None
