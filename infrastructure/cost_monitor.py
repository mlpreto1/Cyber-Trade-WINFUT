# infrastructure/cost_monitor.py
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO: Lógica 80%/100% reordenada

import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("cost_monitor")

DAILY_BUDGET_USD = float(os.getenv("DAILY_API_BUDGET_USD", "0.10"))
ALERT_THRESHOLD_PCT = float(os.getenv("COST_ALERT_THRESHOLD_PCT", "80"))
LOG_PATH = os.getenv("COST_LOG_PATH", "./logs/cost_today.json")


class CostMonitor:
    def __init__(self, telegram=None):
        self.tg = telegram
        self.orcamento = DAILY_BUDGET_USD
        self.alerta_80 = False
        self.alerta_100 = False

    def registrar(self, custo_usd: float):
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "custo": custo_usd
            }) + "\n")

    def verificar(self, custo_atual: float):
        pct = (custo_atual / self.orcamento) * 100

        if pct >= 80 and not self.alerta_80:
            self.alerta_80 = True
            msg = f"⚠️ Custos: {pct:.0f}% do orçamento"
            logger.warning(msg)
            if self.tg:
                self.tg.alertar(msg)

        if pct >= 100 and not self.alerta_100:
            self.alerta_100 = True
            msg = f"🛑 ORÇAMENTO EXCEDIDO {pct:.0f}%"
            logger.critical(msg)
            if self.tg:
                self.tg.alertar(msg)
            return True

        return False

    def dentro_orcamento(self, custo_atual: float) -> bool:
        return custo_atual < self.orcamento

    def reset_diario(self):
        self.alerta_80 = False
        self.alerta_100 = False