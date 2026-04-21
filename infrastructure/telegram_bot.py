# infrastructure/telegram_bot.py
# CYBER TRADE WIN v3.0

import os
import logging
import requests

logger = logging.getLogger("telegram_bot")


class TelegramBot:
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        self._last_update_id = None
    
    def _post(self, method: str, data: dict):
        if not self.enabled:
            logger.info(f"[TELEGRAM] {method} {data}")
            return None
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        try:
            resp = requests.post(url, json=data, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Telegram {method} error: {e}")
            return None
    
    def alertar(self, mensagem: str):
        if not self.enabled:
            logger.info(f"[TELEGRAM] {mensagem}")
            return
        self._post("sendMessage", {"chat_id": self.chat_id, "text": mensagem})
    
    def send_inline(self, texto: str, button_text: str, callback_data: str):
        if not self.enabled:
            logger.info(f"[TELEGRAM] {texto} [{button_text}]")
            return
        reply_markup = {"inline_keyboard": [[{"text": button_text, "callback_data": callback_data}]]}
        self._post("sendMessage", {"chat_id": self.chat_id, "text": texto, "reply_markup": reply_markup})
    
    def get_updates(self, timeout: int = 5):
        params = {"timeout": timeout}
        if self._last_update_id:
            params["offset"] = self._last_update_id + 1
        result = self._post("getUpdates", params)
        if not result or not result.get("ok"):
            return []
        updates = result.get("result", [])
        if updates:
            self._last_update_id = updates[-1]["update_id"]
        return updates
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