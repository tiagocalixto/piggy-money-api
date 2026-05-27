### core/usecases/category_usecases.py
"""
Use cases relacionados a categorias.

Cada use case é uma classe com método execute(), recebendo dependências
via construtor (injeção manual simples).
"""
from core.entity.category import Category
from core.validations import validar_nome_unico
from infra.repositories.category_repository import CategoryRepository
from infra.repositories.transaction_repository import TransactionRepository


class CreateCategoryUseCase:
    """Cria uma nova categoria para o usuário.

    Regras:
    - Nome obrigatório e não vazio.
    - Nome único por usuário (case insensitive).
    """

    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo

    def execute(
        self, usuario_id: int, nome: str, tipo_permitido: str = "ambos"
    ) -> Category:
        """Executa a criação da categoria.

        Args:
            usuario_id: ID do usuário proprietário.
            nome: Nome da categoria.
            tipo_permitido: Tipo de transação permitida (entrada/saida/ambos).

        Returns:
            Categoria criada.

        Raises:
            ValueError: Se o nome for vazio ou já existir.
        """
        if not nome or not nome.strip():
            raise ValueError("O nome da categoria é obrigatório.")

        validar_nome_unico(self.category_repo, usuario_id, nome)

        category = Category(
            usuario_id=usuario_id,
            nome=nome.strip(),
            tipo_permitido=tipo_permitido,
        )
        return self.category_repo.create(category)


class UpdateCategoryUseCase:
    """Atualiza uma categoria existente.

    Regras:
    - Nome deve permanecer único (excluindo a própria entidade).
    """

    def __init__(self, category_repo: CategoryRepository) -> None:
        self.category_repo = category_repo

    def execute(self, category_id: int, usuario_id: int, nome: str) -> Category:
        """Executa a atualização da categoria.

        Args:
            category_id: ID da categoria a ser atualizada.
            usuario_id: ID do usuário (para validação de unicidade).
            nome: Novo nome da categoria.

        Returns:
            Categoria atualizada.

        Raises:
            ValueError: Se a categoria não existir ou o nome já estiver em uso.
        """
        category = self.category_repo.get_by_id(category_id)
        if category is None:
            raise ValueError(f"Categoria com id={category_id} não encontrada.")

        validar_nome_unico(
            self.category_repo, usuario_id, nome, entidade_id=category_id
        )

        category.nome = nome.strip()
        return self.category_repo.update(category)


class DeleteCategoryUseCase:
    """Remove uma categoria, movendo suas transações para 'Sem categoria'.

    Regras:
    - Transações NÃO são deletadas — são movidas para a categoria default.
    - Categoria 'Sem categoria' é criada automaticamente se não existir.
    """

    def __init__(
        self,
        category_repo: CategoryRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self.category_repo = category_repo
        self.transaction_repo = transaction_repo

    def execute(self, category_id: int, usuario_id: int) -> None:
        """Executa a remoção da categoria.

        Args:
            category_id: ID da categoria a ser removida.
            usuario_id: ID do usuário.

        Raises:
            ValueError: Se a categoria não existir.
        """
        category = self.category_repo.get_by_id(category_id)
        if category is None:
            raise ValueError(f"Categoria com id={category_id} não encontrada.")

        # Busca ou cria a categoria "Sem categoria"
        default_cat = self.category_repo.find_default_category(usuario_id)
        if default_cat is None:
            default_cat = self.category_repo.create(
                Category(
                    usuario_id=usuario_id,
                    nome="Sem categoria",
                    tipo_permitido="ambos",
                )
            )

        # Move todas as transações para "Sem categoria"
        transactions = self.category_repo.list_transactions_by_category(
            category_id
        )
        for tx in transactions:
            tx.categoria_id = default_cat.id
            self.transaction_repo.update(tx)

        # Remove a categoria
        self.category_repo.delete(category_id)
