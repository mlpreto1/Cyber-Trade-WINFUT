# main.py
# CYBER TRADE WIN v2.1 — Main Loop

import asyncio
import logging
import os
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("main")

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"
DATA_SOURCE = os.getenv("DATA_SOURCE", "simulador")


class CyberTradeWIN:
    def __init__(self):
        self.redis_state = None
        self.db = None
        self.tg = None
        self.router = None
        self.cyber = None
        self.exec = None
        self.data_provider = None
        self.operacoes_hoje = 0

    async def iniciar(self):
        logger.info("[CYBER] WIN v2.1 started")
        logger.info(f"[MODE] {'PAPER' if PAPER_MODE else 'REAL'}")
        logger.info(f"[DATA] Source: {DATA_SOURCE}")

        await self._iniciar_componentes()
        await self._loop()

    async def _iniciar_componentes(self):
        try:
            from infrastructure.redis_state import RedisState
            self.redis_state = RedisState()

            from infrastructure.telegram_bot import TelegramBot
            self.tg = TelegramBot()

            from infrastructure.database import Database
            self.db = Database()

            from infrastructure.llm_router import LLMRouter
            self.router = LLMRouter()

            from infrastructure.data_provider import DataProvider
            self.data_provider = DataProvider(source=DATA_SOURCE)
            self.data_provider.set_redis(self.redis_state)

            from agents.cyber_agent import CyberAgent
            self.cyber = CyberAgent(self.router, self.redis_state)

            from agents.exec_agent import ExecAgent
            self.exec = ExecAgent(self.redis_state, self.db, self.tg)

            logger.info("[OK] Components initialized")
            self.tg.alertar("[OK] Cyber Trade WIN started!")
        except Exception as e:
            logger.error(f"[ERR] Init: {e}")
            import traceback
            traceback.print_exc()

    async def _loop(self):
        ciclo = 0
        while True:
            ciclo += 1
            logger.info(f"[CYCLE {ciclo}] Running...")

            if self._cutoff_atingido():
                logger.info("[STOP] Cutoff reached")
                self.tg.alertar("[STOP] Cutoff 17:30 - encerrando")
                break

            await self._ciclo(ciclo)
            await asyncio.sleep(300)

    def _cutoff_atingido(self) -> bool:
        agora = datetime.now().time()
        return agora.hour >= 17 and agora.minute >= 30

    async def _ciclo(self, num: int):
        try:
            logger.info(f"[CYCLE {num}] Getting data...")

            candles_5m = await self.data_provider.get_dados_candle("5min", 20)
            preco_atual = await self.data_provider.get_preco_atual()
            book = await self.data_provider.get_book()

            logger.info(f"[CYCLE {num}] Preco atual: {preco_atual}")
            logger.info(f"[CYCLE {num}] Candles: {len(candles_5m)}")

            self.redis_state.set("preco_atual_win", str(preco_atual))

            if PAPER_MODE and num <= 3:
                self.tg.alertar(f"[OK] Ciclo {num} | Preco: {preco_atual} | candles: {len(candles_5m)}")

        except Exception as e:
            logger.error(f"[CYCLE {num}] Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())
