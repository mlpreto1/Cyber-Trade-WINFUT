# guard.py
# CYBER TRADE WIN v2.1 — Watchdog + Kill Switch

import asyncio
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("./logs/guard.log")]
)
logger = logging.getLogger("guard")


class Watchdog:
    def __init__(self):
        self.ativo = True
        self.ultimo_ping = datetime.now()
        self.redis_state = None

    async def iniciar(self):
        logger.info("🛡️ GUARD iniciado")
        await self._loop()

    async def _loop(self):
        while self.ativo:
            await asyncio.sleep(30)
            if self._verificar_horario():
                logger.info("🛑 Cutoff 17:30 → GUARD encerra")
                self.ativo = False
                break

    def _verificar_horario(self) -> bool:
        agora = datetime.now().time()
        return agora.hour >= 17 and agora.minute >= 30

    def ping(self):
        self.ultimo_ping = datetime.now()

    def esta_vivo(self) -> bool:
        diff = (datetime.now() - self.ultimo_ping).seconds
        return diff < 60


if __name__ == "__main__":
    wd = Watchdog()
    asyncio.run(wd.iniciar())