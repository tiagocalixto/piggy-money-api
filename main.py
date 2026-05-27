### main.py
"""
Bootstrap da aplicação Piggy Money API.

Inicializa banco de dados, repositórios, use cases e handlers de canais.
"""
from config.settings import DB_NAME
from infra.database.connection import engine, get_session
from infra.database.models import Base

# Repositórios
from infra.repositories.user_repository import UserRepository
from infra.repositories.transaction_repository import TransactionRepository
from infra.repositories.account_repository import AccountRepository
from infra.repositories.category_repository import CategoryRepository
from infra.repositories.credit_card_repository import CreditCardRepository
from infra.repositories.benefit_card_repository import BenefitCardRepository
from infra.repositories.invoice_repository import InvoiceRepository

# Use cases — Categorias
from core.usecases.category_usecases import (
    CreateCategoryUseCase,
    UpdateCategoryUseCase,
    DeleteCategoryUseCase,
)

# Use cases — Contas
from core.usecases.account_usecases import (
    CreateAccountUseCase,
    UpdateAccountUseCase,
    DeleteAccountUseCase,
)

# Use cases — Cartão de crédito
from core.usecases.credit_card_usecases import (
    CreateCreditCardUseCase,
    UpdateCreditCardUseCase,
    DeleteCreditCardUseCase,
)

# Use cases — Cartão de benefício
from core.usecases.benefit_card_usecases import (
    CreateBenefitCardUseCase,
    UpdateBenefitCardUseCase,
    DeleteBenefitCardUseCase,
)

# Use cases — Transações
from core.usecases.transaction_usecases import (
    CreateTransactionUseCase,
    UpdateTransactionUseCase,
    DeleteTransactionUseCase,
    ListTransactionsUseCase,
    PayCreditCardInvoiceUseCase,
    GenerateInvoiceUseCase,
)

# Handlers de canais
from channels.telegram.handlers import TelegramHandler
from channels.whatsapp.handlers import WhatsAppHandler


def bootstrap() -> dict:
    """Inicializa toda a stack da aplicação.

    Returns:
        Dicionário com as instâncias principais (use cases e handlers).
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
    credit_card_repo = CreditCardRepository(get_session)
    benefit_card_repo = BenefitCardRepository(get_session)
    invoice_repo = InvoiceRepository(get_session)

    # 4. Instanciar use cases (injeção manual de dependências)
    # Categorias
    create_category_uc = CreateCategoryUseCase(category_repo)
    update_category_uc = UpdateCategoryUseCase(category_repo)
    delete_category_uc = DeleteCategoryUseCase(category_repo, transaction_repo)

    # Contas
    create_account_uc = CreateAccountUseCase(account_repo)
    update_account_uc = UpdateAccountUseCase(account_repo)
    delete_account_uc = DeleteAccountUseCase(account_repo)

    # Cartão de crédito
    create_credit_card_uc = CreateCreditCardUseCase(credit_card_repo)
    update_credit_card_uc = UpdateCreditCardUseCase(credit_card_repo)
    delete_credit_card_uc = DeleteCreditCardUseCase(credit_card_repo)

    # Cartão de benefício
    create_benefit_card_uc = CreateBenefitCardUseCase(benefit_card_repo)
    update_benefit_card_uc = UpdateBenefitCardUseCase(benefit_card_repo)
    delete_benefit_card_uc = DeleteBenefitCardUseCase(benefit_card_repo)

    # Transações
    create_transaction_uc = CreateTransactionUseCase(
        transaction_repo, category_repo, account_repo,
        credit_card_repo, benefit_card_repo,
    )
    update_transaction_uc = UpdateTransactionUseCase(
        transaction_repo, category_repo,
    )
    delete_transaction_uc = DeleteTransactionUseCase(transaction_repo)
    list_transactions_uc = ListTransactionsUseCase(transaction_repo)
    pay_invoice_uc = PayCreditCardInvoiceUseCase(
        transaction_repo, invoice_repo, credit_card_repo, category_repo,
    )
    generate_invoice_uc = GenerateInvoiceUseCase(
        transaction_repo, invoice_repo, credit_card_repo,
    )

    # 5. Instanciar handlers de canais (recebem use cases)
    telegram_handler = TelegramHandler(
        user_repo,
        create_category_uc, update_category_uc, delete_category_uc,
        create_account_uc, update_account_uc, delete_account_uc,
        create_credit_card_uc, update_credit_card_uc, delete_credit_card_uc,
        create_benefit_card_uc, update_benefit_card_uc, delete_benefit_card_uc,
        create_transaction_uc, update_transaction_uc, delete_transaction_uc,
        list_transactions_uc, pay_invoice_uc, generate_invoice_uc,
    )
    whatsapp_handler = WhatsAppHandler(
        user_repo,
        create_category_uc, update_category_uc, delete_category_uc,
        create_account_uc, update_account_uc, delete_account_uc,
        create_credit_card_uc, update_credit_card_uc, delete_credit_card_uc,
        create_benefit_card_uc, update_benefit_card_uc, delete_benefit_card_uc,
        create_transaction_uc, update_transaction_uc, delete_transaction_uc,
        list_transactions_uc, pay_invoice_uc, generate_invoice_uc,
    )

    print("[OK] Telegram inicializado")
    print("[OK] WhatsApp inicializado")

    return {
        "use_cases": {
            "create_category": create_category_uc,
            "update_category": update_category_uc,
            "delete_category": delete_category_uc,
            "create_account": create_account_uc,
            "update_account": update_account_uc,
            "delete_account": delete_account_uc,
            "create_credit_card": create_credit_card_uc,
            "update_credit_card": update_credit_card_uc,
            "delete_credit_card": delete_credit_card_uc,
            "create_benefit_card": create_benefit_card_uc,
            "update_benefit_card": update_benefit_card_uc,
            "delete_benefit_card": delete_benefit_card_uc,
            "create_transaction": create_transaction_uc,
            "update_transaction": update_transaction_uc,
            "delete_transaction": delete_transaction_uc,
            "list_transactions": list_transactions_uc,
            "pay_invoice": pay_invoice_uc,
            "generate_invoice": generate_invoice_uc,
        },
        "telegram_handler": telegram_handler,
        "whatsapp_handler": whatsapp_handler,
    }


if __name__ == "__main__":
    app = bootstrap()
