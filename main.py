### main.py
"""
Bootstrap da aplicação Piggy Money API.

Inicializa banco de dados, repositórios, serviços e handlers de canais.
"""
from config.settings import DB_NAME
from infra.database.connection import engine, get_session
from infra.database.models import Base

# Repositórios
from infra.repositories.user_repository import UserRepository
from infra.repositories.transaction_repository import TransactionRepository
from infra.repositories.account_repository import AccountRepository
from infra.repositories.category_repository import CategoryRepository

# Serviços (casos de uso)
from core.services.user_service import UserService
from core.services.finance_service import FinanceService

# Handlers de canais
from channels.telegram.handlers import TelegramHandler
from channels.whatsapp.handlers import WhatsAppHandler


def bootstrap() -> dict:
    """Inicializa toda a stack da aplicação.

    Returns:
        Dicionário com as instâncias principais (services e handlers).
    """
    # 1. Conexão com banco de dados
    print(f"[OK] Banco conectado: {DB_NAME}")

    # 2. Criar tabelas (se não existirem)
    Base.metadata.create_all(bind=engine)
    print("[OK] Tabelas carregadas")

    # 3. Instanciar repositórios (recebem a fábrica de sessões)
    user_repo = UserRepository(get_session)
    transaction_repo = TransactionRepository(get_session)
    account_repo = AccountRepository(get_session)
    category_repo = CategoryRepository(get_session)

    # 4. Instanciar serviços (injeção manual de dependências)
    user_service = UserService(user_repo)
    finance_service = FinanceService(
        transaction_repo, account_repo, category_repo
    )

    # 5. Instanciar handlers de canais (injeção de serviços)
    telegram_handler = TelegramHandler(user_service, finance_service)
    whatsapp_handler = WhatsAppHandler(user_service, finance_service)

    print("[OK] Telegram inicializado")
    print("[OK] WhatsApp inicializado")

    return {
        "user_service": user_service,
        "finance_service": finance_service,
        "telegram_handler": telegram_handler,
        "whatsapp_handler": whatsapp_handler,
    }


if __name__ == "__main__":
    app = bootstrap()
