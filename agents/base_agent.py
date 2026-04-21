# agents/base_agent.py
# CYBER TRADE WIN v2.1

import json
import logging
import os
from typing import Optional

logger = logging.getLogger("base_agent")


class BaseAgent:
    def __init__(self, nome: str, skill_path: str, router, max_tokens: int = 1500, temperature: float = 0.1):
        self.nome = nome
        self.skill_path = skill_path
        self.router = router
        self.max_tokens = max_tokens
        self.temperature = temperature

    async def invocar(self, user_content: str) -> dict:
        try:
            resposta = await self.router.gerar(
                agent=self.nome,
                user_content=user_content,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return self._parse_json(resposta)
        except Exception as e:
            logger.error(f"{self.nome} erro: {e}")
            raise

    def _parse_json(self, texto: str) -> dict:
        try:
            inicio = texto.find("{")
            fim = texto.rfind("}") + 1
            if inicio >= 0 and fim > inicio:
                return json.loads(texto[inicio:fim])
        except Exception:
            pass
        return {"erro": "parse_failed", "raw": texto[:200]}

    def _decisao_cancelar(self, motivo: str, cyber_input: dict, sniper_mode: bool = False) -> dict:
        logger.info(f"{self.nome} CANCELAR: {motivo}")
        return {
            "decisao": "CANCELAR",
            "motivo": motivo,
            "sniper_mode": sniper_mode,
        }