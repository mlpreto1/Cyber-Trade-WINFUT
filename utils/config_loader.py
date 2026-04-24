# utils/config_loader.py
# CYBER TRADE WIN — Carregador centralizado do openclaw_win.json

import json
import os
import logging
from pathlib import Path
from functools import lru_cache

logger = logging.getLogger("config_loader")

CONFIG_PATH = Path(__file__).parent.parent / "openclaw_win.json"


@lru_cache(maxsize=1)
def carregar_config() -> dict:
    """Carrega openclaw_win.json uma vez com cache. Recarregar via reload_config()."""
    if not CONFIG_PATH.exists():
        logger.warning(f"[CONFIG] {CONFIG_PATH} não encontrado — usando defaults")
        return _config_default()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.info(f"[CONFIG] Carregado: {CONFIG_PATH} (v{config.get('version', '?')})")
            return config
    except Exception as e:
        logger.error(f"[CONFIG] Erro ao carregar config: {e} — usando defaults")
        return _config_default()


def reload_config() -> dict:
    """Força recarregamento do config (limpa cache)."""
    carregar_config.cache_clear()
    return carregar_config()


def get_score_pesos() -> dict:
    """Retorna pesos do score para composição da decisão do NEO."""
    config = carregar_config()
    pesos = config.get("score_pesos", {})
    # Validar soma = 1.0
    total = sum(pesos.values())
    if abs(total - 1.0) > 0.01:
        logger.error(f"[CONFIG] score_pesos soma {total:.2f} != 1.00 — usando defaults")
        return {"graph": 0.35, "flow": 0.30, "context": 0.30, "timing": 0.05}
    return pesos


def get_nivel_capital(capital_atual: float) -> dict:
    """Retorna o nível de capital correspondente ao capital atual."""
    config = carregar_config()
    niveis = config.get("capital_levels", {}).get("niveis", [])

    for nivel in niveis:
        if nivel["capital_min"] <= capital_atual <= nivel["capital_max"]:
            return nivel

    # Fallback: nível 1
    logger.warning(f"[CONFIG] Capital R${capital_atual:.2f} não mapeado — usando nível 1")
    return {
        "nivel": 1, "nome": "INICIANTE",
        "capital_min": 0, "capital_max": 1999.99,
        "max_contratos": 1, "score_minimo": 72, "stop_day_pct": 5.0
    }


def get_modelos_llm(paper_mode: bool) -> dict:
    """Retorna dict de modelos LLM conforme o modo de operação."""
    config = carregar_config()
    routing = config.get("llm_routing", {}).get("modelos", {})
    modo = "paper" if paper_mode else "producao"
    modelos = routing.get(modo, {})

    # Validar model strings conhecidas
    modelos_validos = {
        "gemma-4-31b-it", "gemma-4-e4b-it",
        "claude-sonnet-4-20250514", "claude-opus-4-20250514",
        "claude-haiku-4-5-20251001",
    }
    for agente, modelo in modelos.items():
        if modelo not in modelos_validos:
            logger.warning(f"[CONFIG] Modelo '{modelo}' para {agente} pode estar desatualizado")

    return modelos


def get_risk_params() -> dict:
    """Retorna parâmetros de risco do config."""
    config = carregar_config()
    risk = config.get("risk", {})

    # Garantir que VALOR_PONTO_WIN está correto (R$0.20)
    if risk.get("valor_ponto", 0) != 0.20:
        logger.error(
            f"[CONFIG] ALERTA CRÍTICO: valor_ponto={risk.get('valor_ponto')} != 0.20! "
            "Corrigindo para 0.20"
        )
        risk["valor_ponto"] = 0.20

    return risk


def _config_default() -> dict:
    """Config mínimo de fallback caso openclaw_win.json não exista."""
    return {
        "version": "DEFAULT",
        "score_pesos": {"graph": 0.35, "flow": 0.30, "context": 0.30, "timing": 0.05},
        "capital_levels": {"niveis": [
            {"nivel": 1, "nome": "INICIANTE", "capital_min": 0, "capital_max": 9999999,
            "max_contratos": 1, "score_minimo": 72, "stop_day_pct": 5.0}
        ]},
        "risk": {
            "risco_por_trade_pct": 1.0, "max_operacoes_dia": 5,
            "rr_minimo": 1.5, "atr_minimo_win": 200.0,
            "valor_ponto": 0.20, "breakeven_pts": 60.0, "trailing_floor_pts": 80.0
        },
        "llm_routing": {"modelos": {
            "paper": {"neo": "gemma-4-31b-it", "architect": "gemma-4-31b-it",
            "morpheus": "gemma-4-31b-it", "oracle": "gemma-4-e4b-it"},
            "producao": {"neo": "claude-sonnet-4-20250514", "architect": "gemma-4-31b-it",
            "morpheus": "gemma-4-31b-it", "oracle": "gemma-4-e4b-it"}
        }}
    }
