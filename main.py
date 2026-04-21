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


class CyberTradeWIN:
    def __init__(self):
        self.redis_state = None
        self.db = None
        self.tg = None
        self.router = None
        self.cyber = None
        self.exec = None
        self.operacoes_hoje = 0

    async def iniciar(self):
        logger.info("[CYBER] WIN v2.1 started")
        logger.info(f"[MODE] {'PAPER' if PAPER_MODE else 'REAL'}")

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

            from agents.cyber_agent import CyberAgent
            self.cyber = CyberAgent(self.router, self.redis_state)

            from agents.exec_agent import ExecAgent
            self.exec = ExecAgent(self.redis_state, self.db, self.tg)

            logger.info("[OK] Components initialized")
        except Exception as e:
            logger.error(f"[ERR] Init: {e}")

    async def _loop(self):
        while True:
            if self._cutoff_atingido():
                logger.info("[STOP] Cutoff reached")
                break

            await self._ciclo()
            await asyncio.sleep(300)

    def _cutoff_atingido(self) -> bool:
        agora = datetime.now().time()
        return agora.hour >= 17 and agora.minute >= 30

    async def _ciclo(self):
        logger.info("[CYCLE] Running...")
        self.tg.alertar("[OK] Cycle active")


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())
