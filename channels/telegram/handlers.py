### channels/telegram/handlers.py
"""
Handler para mensagens recebidas via Telegram.

Placeholder — será implementado futuramente com integração real
ao bot do Telegram (python-telegram-bot ou similar).
"""
from infra.repositories.user_repository import UserRepository


class TelegramHandler:
    """Recebe e processa mensagens do Telegram."""

    def __init__(
        self,
        user_repo: UserRepository,
        create_category_uc,
        update_category_uc,
        delete_category_uc,
        create_account_uc,
        update_account_uc,
        delete_account_uc,
        create_credit_card_uc,
        update_credit_card_uc,
        delete_credit_card_uc,
        create_benefit_card_uc,
        update_benefit_card_uc,
        delete_benefit_card_uc,
        create_transaction_uc,
        update_transaction_uc,
        delete_transaction_uc,
        list_transactions_uc,
        pay_invoice_uc,
        generate_invoice_uc,
    ) -> None:
        """
        Args:
            user_repo: Repositório de usuários.
            *_uc: Use cases injetados manualmente.
        """
        self.user_repo = user_repo
        self.create_category_uc = create_category_uc
        self.update_category_uc = update_category_uc
        self.delete_category_uc = delete_category_uc
        self.create_account_uc = create_account_uc
        self.update_account_uc = update_account_uc
        self.delete_account_uc = delete_account_uc
        self.create_credit_card_uc = create_credit_card_uc
        self.update_credit_card_uc = update_credit_card_uc
        self.delete_credit_card_uc = delete_credit_card_uc
        self.create_benefit_card_uc = create_benefit_card_uc
        self.update_benefit_card_uc = update_benefit_card_uc
        self.delete_benefit_card_uc = delete_benefit_card_uc
        self.create_transaction_uc = create_transaction_uc
        self.update_transaction_uc = update_transaction_uc
        self.delete_transaction_uc = delete_transaction_uc
        self.list_transactions_uc = list_transactions_uc
        self.pay_invoice_uc = pay_invoice_uc
        self.generate_invoice_uc = generate_invoice_uc

    def handle_message(self, text: str) -> str:
        """Processa uma mensagem de texto recebida do Telegram.

        Args:
            text: Texto da mensagem enviada pelo usuário.

        Returns:
            Resposta textual ao usuário.
        """
        return "Handler Telegram implementado futuramente"
