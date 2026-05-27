### core/validations.py
"""
Módulo de validações de domínio — funções puras, sem dependência de infraestrutura.

Regras de negócio globais aplicadas antes de persistir qualquer entidade.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasFindByNome(Protocol):
    """Protocolo para repositórios que possuem método find_by_nome."""

    def find_by_nome(self, usuario_id: int, nome: str):
        ...


def validar_nome_unico(
    repo: HasFindByNome,
    usuario_id: int,
    nome: str,
    entidade_id: int | None = None,
) -> None:
    """Valida se o nome é único para o usuário (case insensitive).

    Lança ValueError se já existir outra entidade do mesmo tipo com o mesmo nome.

    Args:
        repo: Repositório com método find_by_nome(usuario_id, nome).
        usuario_id: ID do usuário dono da entidade.
        nome: Nome a ser validado.
        entidade_id: ID da própria entidade (para excluir a si mesma em updates).

    Raises:
        ValueError: Se o nome já estiver em uso.
    """
    if not nome or not nome.strip():
        raise ValueError("O nome é obrigatório e não pode estar vazio.")

    existente = repo.find_by_nome(usuario_id, nome.strip())
    if existente and existente.id != entidade_id:
        raise ValueError(
            f"Já existe um registro com o nome '{nome}' para este usuário."
        )
