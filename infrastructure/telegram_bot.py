# infrastructure/telegram_bot.py
# CYBER TRADE WIN v2.1

import os
import logging
import requests

logger = logging.getLogger("telegram_bot")


class TelegramBot:
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)

    def alertar(self, mensagem: str):
        if not self.enabled:
            logger.info(f"[TELEGRAM] {mensagem}")
            return

        try:
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {"chat_id": self.chat_id, "text": mensagem}
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            logger.error(f"Telegram erro: {e}")

    def status(self) -> dict:
        capital = "R$1.000,00 (simulado)"
        return {
            "status": "ONLINE",
            "capital": capital,
            "modo": "PAPER",
            "telegram": "✅" if self.enabled else "⚠️"
        }