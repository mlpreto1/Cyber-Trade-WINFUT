# guard.py
# CYBER TRADE WIN v3.0 — Watchdog + Kill Switch (PATCHED: heartbeat Redis, cutoff 17:00)

import asyncio
import logging
import os
import sys
import signal
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("./logs/guard.log")]
)
logger = logging.getLogger("guard")

HEARTBEAT_KEY = "heartbeat_main"
HEARTBEAT_TIMEOUT = 90  # segundos sem heartbeat = processo travado


class Watchdog:
    def __init__(self):
        self.ativo = True
        self.ultimo_ping = datetime.now()
        self.redis_client = None
        self.tg = None
        self._main_pid_key = "main_pid"

    def _conectar_redis(self):
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            return r
        except Exception as e:
            logger.error(f"[GUARD] Redis unavailable: {e}")
            return None

    def _conectar_telegram(self):
        try:
            from infrastructure.telegram_bot import TelegramBot
            return TelegramBot()
        except Exception as e:
            logger.warning(f"[GUARD] Telegram unavailable: {e}")
            return None

    async def iniciar(self):
        logger.info("[GUARD] Started — monitoring main.py via Redis heartbeat")
        self.redis_client = self._conectar_redis()
        self.tg = self._conectar_telegram()
        await self._loop()

    async def _loop(self):
        while self.ativo:
            await asyncio.sleep(30)

            # 1. Verificar cutoff de horário
            if self._verificar_horario():
                logger.info("[GUARD] Cutoff 17:00 WIN — stopping")
                if self.tg:
                    self.tg.alertar("🛑 [GUARD] Cutoff 17:00 WIN — encerrando sistema")
                self.ativo = False
                break

            # 2. Verificar heartbeat do main.py via Redis
            if self.redis_client:
                try:
                    hb = self.redis_client.get(HEARTBEAT_KEY)
                    if hb is None:
                        logger.warning("[GUARD] Sem heartbeat do main.py!")
                        if self.tg:
                            self.tg.alertar(
                                f"⚠️ [GUARD] main.py sem heartbeat há >{HEARTBEAT_TIMEOUT}s — verificar!"
                            )
                    else:
                        last_hb = datetime.fromisoformat(hb)
                        diff = (datetime.now() - last_hb).total_seconds()
                        if diff > HEARTBEAT_TIMEOUT:
                            logger.error(
                                f"[GUARD] HEARTBEAT EXPIRADO! Último ping: {diff:.0f}s atrás"
                            )
                            if self.tg:
                                self.tg.alertar(
                                    f"🚨 [GUARD] main.py travado! Sem resposta há {diff:.0f}s"
                                )
                        else:
                            logger.info(f"[GUARD] Heartbeat OK — {diff:.0f}s atrás")
                except Exception as e:
                    logger.error(f"[GUARD] Redis check error: {e}")

    def _verificar_horario(self) -> bool:
        agora = datetime.now()
        # WIN cutoff: 17:00 BRT
        cutoff = agora.replace(hour=17, minute=0, second=0, microsecond=0)
        return agora >= cutoff

    def ping(self):
        """Chamado pelo main.py a cada ciclo via Redis — não diretamente."""
        self.ultimo_ping = datetime.now()

    def esta_vivo(self) -> bool:
        diff = (datetime.now() - self.ultimo_ping).total_seconds()
        return diff < 60


if __name__ == "__main__":
    wd = Watchdog()
    asyncio.run(wd.iniciar())