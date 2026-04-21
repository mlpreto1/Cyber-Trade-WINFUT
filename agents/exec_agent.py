# agents/exec_agent.py
# CYBER TRADE WIN v2.1
# VALOR_PONTO_WIN = R$0,20 por contrato

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone

logger = logging.getLogger("exec_agent_win")

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"
VALOR_PONTO_WIN = float(os.getenv("VALOR_PONTO_WIN", "0.20"))
HORARIO_FECHAR = (17, 30)
SLIPPAGE_MAX = float(os.getenv("SLIPPAGE_MAX_PTS", "10.0"))


class ExecAgent:
    def __init__(self, redis_state, db, tg):
        self.redis = redis_state
        self.db = db
        self.tg = tg
        self._posicao = None

    async def armar(self, cyber_output: dict) -> bool:
        if not self._validar_json(cyber_output):
            return False

        max_c = int(self.redis.get("max_contratos_efetivo") or 1)
        contratos = min(cyber_output.get("contratos", 1), max_c)

        estado = {
            "decisao": cyber_output["decisao"],
            "direcao": cyber_output["direcao"],
            "contratos": contratos,
            "entrada": cyber_output["entrada_zona"],
            "stop": cyber_output["stop"],
            "alvo1": cyber_output["alvo1"],
            "alvo2": cyber_output["alvo2"],
            "score": cyber_output.get("score_final", 0),
            "status": "ARMADO",
            "armado_em": datetime.now(timezone.utc).isoformat(),
        }

        self.redis.set("posicao_aberta", json.dumps(estado))
        self.tg.alertar(f"🎯 ARMADO WIN | {estado['direcao']} | {contratos}x | Score {estado['score']}")
        return True

    async def executar_gatilho(self, estado: dict):
        try:
            validade = estado.get("validade_segundos", 300)
            await asyncio.sleep(min(validade, 60))
            if estado.get("status") == "ARMADO":
                await self._executar_entrada(estado)
        except Exception as e:
            logger.error(f"Erro gatilho: {e}")

    async def _executar_entrada(self, estado: dict):
        preco = self._preco_atual()
        if preco is None:
            self.tg.alertar("❌ Preço indisponível")
            return

        slippage = abs(preco - estado["entrada"])
        if slippage > SLIPPAGE_MAX:
            self.tg.alertar(f"❌ Slippage {slippage:.0f}pts > {SLIPPAGE_MAX:.0f}")
            return

        ordem_id = f"PAPER_WIN_{uuid.uuid4().hex[:8]}"
        estado["status"] = "ABERTA"
        estado["ordem_id"] = ordem_id
        self._posicao = estado
        self.redis.set("posicao_aberta", json.dumps(estado))
        self.tg.alertar(f"✅ ENTRADA {estado['direcao']} @ {preco:.0f}")

    async def fechar(self, motivo: str):
        if not self._posicao:
            return

        preco = self._preco_atual() or self._posicao["entrada"]
        direcao = self._posicao["direcao"]
        entrada = self._posicao["entrada"]
        contratos = self._posicao["contratos"]

        resultado_pts = (preco - entrada) if direcao == "COMPRA" else (entrada - preco)
        resultado_reais = resultado_pts * VALOR_PONTO_WIN * contratos

        self.db.registrar_trade({
            "data": datetime.now().isoformat(),
            "direcao": direcao,
            "contratos": contratos,
            "entrada": entrada,
            "saida": preco,
            "resultado_pts": resultado_pts,
            "resultado_reais": resultado_reais,
            "motivo_saida": motivo,
            "score": self._posicao.get("score", 0),
            "modo": "PAPER",
            "ordem_id": self._posicao.get("ordem_id", ""),
        })

        self.redis.delete("posicao_aberta")
        emoji = "✅" if resultado_reais > 0 else "❌"
        self.tg.alertar(f"{emoji} SAIDA {motivo} | {resultado_pts:+.0f}pts | R${resultado_reais:+.2f}")
        self._posicao = None

    def _preco_atual(self) -> float:
        v = self.redis.get("preco_atual_win")
        return float(v) if v else None

    def _validar_json(self, output: dict) -> bool:
        campos = ["decisao", "direcao", "contratos", "entrada_zona", "stop", "alvo1"]
        for c in campos:
            if c not in output:
                return False
        return True