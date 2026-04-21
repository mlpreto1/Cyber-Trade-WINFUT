# agents/cyber_agent.py
# CYBER TRADE WIN v3.0 — NEO Agent com LLM

import json
import logging
import os
import random
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
        self._pesos = self._carregar_pesos()

    def _carregar_pesos(self) -> dict:
        pesos_padrao = {"confianca": 0.5, "forca_fluxo": 0.25, "atr": 0.15, "cvd": 0.1}
        try:
            config_path = r"H:\Meu Drive\Cyber Trade\Winfut\openclaw_win.json"
            if os.path.exists(config_path):
                with open(config_path) as f:
                    config = json.load(f)
                    pesos = config.get("pesos_score", {})
                    if pesos:
                        return pesos
        except:
            pass
        return pesos_padrao

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

        graph = cyber_input.get("graph", {})
        flow = cyber_input.get("flow", {})
        context = cyber_input.get("context", {})

        if self.router:
            try:
                resultado = await self._chamar_llm(graph, flow, context, cyber_input.get("estado_sistema", {}))
                if resultado:
                    return self._pos_validar(resultado, cyber_input, sniper_mode, score_min, max_c, stop_max)
            except Exception as e:
                logger.error(f"[NEO] LLM error: {e}")

        return self._decisao_simulado(graph, flow, context, sniper_mode, score_min)

    async def _chamar_llm(self, graph, flow, context, estado):
        try:
            prompt = self._montar_prompt(graph, flow, context, estado)
            
            resposta = await self.router.gerar(
                agent="neo",
                user_content=prompt,
                max_tokens=1000,
                temperature=0.1,
            )

            logger.info(f"[NEO] LLM response: {resposta[:200]}...")
            
            return self._parse_json_resultado(resposta)
        except Exception as e:
            logger.error(f"[NEO] LLM call failed: {e}")
            return None

    def _montar_prompt(self, graph, flow, context, estado):
        return f"""
Você é o NEO, orquestrador do Cyber Trade WIN.
Analise os dados e retorne uma decisão.

## Estado do Sistema
- Capital: R$ {estado.get('capital_atual', 1000)}
- Operações hoje: {estado.get('operacoes_hoje', 0)}
- Nível: {estado.get('nivel_atual', 1)}
- Modo: {estado.get('modo', 'PAPER')}

## ARCHITECT (Gráfico)
- Sinal: {graph.get('sinal', 'NEUTRO')}
- Confiança: {graph.get('confianca', 0)}
- Tendência 15m: {graph.get('tendencia_master_15m', 'INDEFINIDA')}
- ATR: {graph.get('atr14_5m', 200)}

## MORPHEUS (Fluxo)
- Direção: {flow.get('direcao_fluxo', 'NEUTRO')}
- Força: {flow.get('forca_fluxo', 0)}
- CVD: {flow.get('cvd_total', 0)}

## ORACLE (Contexto)
- Regime: {context.get('regime_mercado', 'NORMAL')}
- Status: {context.get('status_macro', 'NORMAL')}
- Alerta corte: {context.get('alerta_finalizacao', False)}

## Regras
- Score >= 65 = ARMAR (PADRÃO)
- Score >= 85 = ARMAR (PREMIUM)
- Score < 65 = CANCELAR
- Dúvida = CANCELAR

Retorne JSON:
{{
  "decisao": "ARMAR|CANCELAR",
  "score_final": 0-100,
  "direcao": "COMPRA|VENDA|NEUTRO",
  "entrada_zona": 0,
  "stop": 0,
  "alvo1": 0,
  "alvo2": 0,
  "gatilho": {{"tipo": "ROMPIMENTO", "validade_segundos": 300}},
  "motivo": "explicação curta"
}}
"""

    def _parse_json_resultado(self, texto: str) -> dict:
        try:
            inicio = texto.find("{")
            fim = texto.rfind("}") + 1
            if inicio >= 0 and fim > inicio:
                return json.loads(texto[inicio:fim])
        except Exception as e:
            logger.error(f"[NEO] Parse error: {e}")
        return {}

    def _decisao_simulado(self, graph, flow, context, sniper_mode, score_min):
        graph_sinal = graph.get("sinal", "NEUTRO")
        graph_conf = graph.get("confianca", 0)
        flow_forca = flow.get("forca_fluxo", 0)
        regime = context.get("regime_mercado", "NORMAL")
        
        if regime == "MORTO":
            return self._decisao_cancelar("Regime MORTO", {}, sniper_mode)
        
        if graph_sinal == "NEUTRO" or graph_conf < 60:
            return self._decisao_cancelar("Sinal fraco", {}, sniper_mode)
        
        if flow_forca < 40:
            return self._decisao_cancelar("Fluxo fraco", {}, sniper_mode)

        score = self._calcular_score_dinamico(graph, flow)
        
        if score >= score_min:
            direcao = graph_sinal
            preco = graph.get("ema9_5m", 130000)
            
            if direcao == "COMPRA":
                stop = preco - 50
                alvo1 = preco + 100
                alvo2 = preco + 150
            else:
                stop = preco + 50
                alvo1 = preco - 100
                alvo2 = preco - 150

            return {
                "decisao": "ARMAR",
                "score_final": score,
                "direcao": direcao,
                "entrada_zona": preco,
                "stop": stop,
                "alvo1": alvo1,
                "alvo2": alvo2,
                "gatilho": {"tipo": "ROMPIMENTO", "validade_segundos": 300},
                "motivo": f"Simulado score={score}"
            }

        return self._decisao_cancelar(f"Score {score} < {score_min}", {}, sniper_mode)

    def _calcular_score_dinamico(self, graph: dict, flow: dict) -> int:
        w = self._pesos
        conf = graph.get("confianca", 0)
        forca = flow.get("forca_fluxo", 0)
        atr = graph.get("atr14_5m", 100)
        cvd = flow.get("cvd_total", 0)

        atr_score = min(100, int(atr / 10))
        cvd_score = min(100, max(-100, int(cvd / 100)))

        score = (
            conf * w.get("confianca", 0.5) +
            forca * w.get("forca_fluxo", 0.25) +
            atr_score * w.get("atr", 0.15) +
            cvd_score * w.get("cvd", 0.1)
        )
        return min(100, int(score))

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
        if context.get("alerta_finalizacao", False):
            return "Corte 17:30 próximo"
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
