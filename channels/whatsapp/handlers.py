### channels/whatsapp/handlers.py
"""
Handler para mensagens recebidas via WhatsApp.

Placeholder — será implementado futuramente com integração real
à API do WhatsApp Business (Twilio, Meta, etc.).
"""
from core.services.finance_service import FinanceService
from core.services.user_service import UserService


class WhatsAppHandler:
    """Recebe e processa mensagens do WhatsApp."""

    def __init__(
        self,
        user_service: UserService,
        finance_service: FinanceService,
    ) -> None:
        """
        Args:
            user_service: Serviço de casos de uso de usuários.
            finance_service: Serviço de casos de uso financeiros.
        """
        self.user_service = user_service
        self.finance_service = finance_service

    def handle_message(self, text: str) -> str:
        """Processa uma mensagem de texto recebida do WhatsApp.

        Args:
            text: Texto da mensagem enviada pelo usuário.

        Returns:
            Resposta textual ao usuário.
        """
        return "Handler WhatsApp implementado futuramente"
