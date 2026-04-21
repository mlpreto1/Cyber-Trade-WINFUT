# infrastructure/profit_bridge.py
# CYBER TRADE WIN v2.1 — Profit DLL Bridge (mock para testes)

import logging
from typing import Dict, Optional

logger = logging.getLogger("profit_bridge")


class ProfitBridge:
    def __init__(self):
        self.connected = False
        self._preco_atual = 0.0

    def conectar(self) -> bool:
        logger.info("[PROFIT] Mock mode - não conectado")
        return False

    def get_preco(self, ativo: str = "WIN") -> Optional[float]:
        return self._preco_atual if self._preco_atual else 133000.0

    def get_candles(self, ativo: str = "WIN", timeframe: str = "5min", n: int = 20) -> list:
        return []

    def get_book(self, ativo: str = "WIN") -> Dict:
        return {"bids": [], "asks": []}

    def get_tape(self, ativo: str = "WIN", n: int = 50) -> list:
        return []

    def enviar_ordem_mercado(self, direcao: str, contratos: int, ativo: str = "WIN") -> str:
        logger.warning("[PROFIT] Mock - ordem não enviada")
        return "MOCK_ORDER"

    def enviar_ordem_limitada(self, preco: float, direcao: str, contratos: int, ativo: str = "WIN") -> str:
        logger.warning("[PROFIT] Mock - ordem não enviada")
        return "MOCK_ORDER"

    def cancelar_ordem(self, ordem_id: str) -> bool:
        return False

    def get_posicao(self, ativo: str = "WIN") -> Dict:
        return {}