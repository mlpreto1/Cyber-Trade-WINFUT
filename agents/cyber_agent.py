# agents/cyber_agent.py
# CYBER TRADE WIN v2.1

import json
import logging
import os
from datetime import datetime, timezone
from agents.base_agent import BaseAgent

logger = logging.getLogger("cyber_agent_win")

SNIPER_SCORE_MIN = int(os.getenv("SNIPER_SCORE_MIN", "80"))
RISCO_POR_TRADE_PCT = float(os.getenv("RISCO_POR_TRADE_PCT", "1.0"))
VALOR_PONTO_WIN = float(os.getenv("VALOR_PONTO_WIN", "0.20"))
MAX_OPERACOES_DIA = int(os.getenv("MAX_OPERACOES_DIA", "5"))


class CyberAgent(BaseAgent):
    def __init__(self, router, redis_state=None):
        super().__init__(
            nome="neo",
            skill_path="./skills/cyber_skill_win.md",
            router=router,
            max_tokens=1500,
            temperature=0.1,
        )
        self.redis = redis_state

    async def decidir(self, cyber_input: dict) -> dict:
        sniper_mode = self._ler_sniper_mode(cyber_input.get("estado_sistema", {}))
        score_min = self._score_minimo_atual(sniper_mode)
        max_c = self._max_contratos_atual(sniper_mode)
        stop_max = self._stop_maximo_atual()

        bloqueio = self._pre_filtro_deterministico(
            cyber_input.get("estado_sistema", {}),
            cyber_input.get("graph", {}),
            cyber_input.get("flow", {}),
            cyber_input.get("context", {}),
            sniper_mode, score_min, stop_max
        )
        if bloqueio:
            return self._decisao_cancelar(bloqueio, cyber_input, sniper_mode)

        user_content = json.dumps(cyber_input, ensure_ascii=False, indent=2)
        try:
            resultado = await self.invocar(user_content)
        except Exception as e:
            logger.error(f"CYBER WIN LLM falhou: {e}")
            return self._decisao_cancelar(f"Erro LLM: {e}", cyber_input, sniper_mode)

        return self._pos_validar(resultado, cyber_input, sniper_mode, score_min, max_c, stop_max)

    def _ler_sniper_mode(self, estado: dict) -> bool:
        if self.redis:
            try:
                v = self.redis.get("sniper_mode")
                return v and v.lower() == "true"
            except Exception:
                pass
        return False

    def _score_minimo_atual(self, sniper_mode: bool) -> int:
        return SNIPER_SCORE_MIN if sniper_mode else 72

    def _max_contratos_atual(self, sniper_mode: bool) -> int:
        return 2 if sniper_mode else 1

    def _stop_maximo_atual(self) -> float:
        return 50.0

    def _stop_day_pct_atual(self) -> float:
        return 5.0

    def _pre_filtro_deterministico(self, estado, graph, flow, context, sniper_mode, score_min, stop_max) -> str:
        stop_day = self._stop_day_pct_atual()
        res_dia = estado.get("resultado_dia_percentual", 0)

        if res_dia <= -stop_day:
            return f"Stop-day: {res_dia:.1f}%"
        if estado.get("operacoes_hoje", 0) >= MAX_OPERACOES_DIA:
            return f"Máx {MAX_OPERACOES_DIA} ops"
        if context.get("status_macro") == "BLOQUEADO":
            return "ORACLE: macro BLOQUEADO"
        if graph.get("sinal") == "NEUTRO" or graph.get("confianca", 0) == 0:
            return "ARCHITECT: NEUTRO"
        if graph.get("confianca", 0) < 60:
            return f"ARCHITECT: conf {graph.get('confianca')}"
        if flow.get("forca_fluxo", 0) < 40:
            return f"MORPHEUS: fluxo {flow.get('forca_fluxo')}"
        if context.get("regime_mercado") == "MORTO":
            return "Regime MORTO"
        return None

    def _pos_validar(self, resultado, entrada, sniper_mode, score_min, max_c, stop_max) -> dict:
        decisao = resultado.get("decisao", "CANCELAR")
        score = resultado.get("score_final", 0)

        if decisao == "ARMAR":
            if score < score_min:
                resultado["decisao"] = "CANCELAR"
                resultado["motivo"] = f"Score {score} < {score_min}"

        return resultado