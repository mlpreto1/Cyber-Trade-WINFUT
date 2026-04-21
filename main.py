# main.py
# CYBER TRADE WIN v2.1 — Main Loop Completo com LLM

import asyncio
import logging
import os
import json
import random
from datetime import datetime
from datetime import timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("main")

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"
DATA_SOURCE = os.getenv("DATA_SOURCE", "yahoo")


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

            await self._ciclo_completo(ciclo)
            await asyncio.sleep(300)

    def _cutoff_atingido(self) -> bool:
        agora = datetime.now().time()
        return agora.hour >= 17 and agora.minute >= 30

    async def _ciclo_completo(self, num: int):
        try:
            logger.info(f"[CYCLE {num}] Step 1: Getting data...")
            
            candles_5m = await self.data_provider.get_dados_candle("5min", 20)
            preco_atual = await self.data_provider.get_preco_atual()
            book = await self.data_provider.get_book()
            trades = await self.data_provider.get_trades()

            logger.info(f"[CYCLE {num}] Preco: {preco_atual} | Candles: {len(candles_5m)}")

            self.redis_state.set("preco_atual_win", str(preco_atual))

            if PAPER_MODE:
                self.tg.alertar(f"[{num}] Preco: {preco_atual} | Analisando...")

            logger.info(f"[CYCLE {num}] Step 2: Running AGENTS (LLM)...")

            resultado = await self._executar_agentes(candles_5m, book, trades, preco_atual)

            logger.info(f"[CYCLE {num}] Step 3: Decision = {resultado.get('decisao', 'N/A')}")

            if resultado.get("decisao") == "ARMAR":
                score = resultado.get("score_final", 0)
                direcao = resultado.get("direcao", "?")
                entrada = resultado.get("entrada_zona", 0)
                stop = resultado.get("stop", 0)
                
                self.tg.alertar(f"[OK] ARMAR! {direcao} | Score: {score} | Entrada: {entrada} | Stop: {stop}")
                logger.info(f"[CYCLE {num}] >>> ARMAR {direcao} Score:{score}")
            else:
                motivo = resultado.get("motivo", "sem motivo")
                self.tg.alertar(f"[OK] {resultado.get('decisao', 'CANCELAR')} - {motivo}")
                logger.info(f"[CYCLE {num}] >>> {resultado.get('decisao')}: {motivo}")

        except Exception as e:
            logger.error(f"[CYCLE {num}] Error: {e}")
            import traceback
            traceback.print_exc()

    async def _executar_agentes(self, candles, book, trades, preco_atual):
        try:
            from agents.cyber_agent import CyberAgent
            
            cyber = CyberAgent(self.router, self.redis_state)

            indicadores = self._calcular_indicadores(candles)
            fluxo = self._calcular_fluxo(book, trades)
            contexto = await self._calcular_contexto()

            entrada = {
                "estado_sistema": {
                    "capital_atual": self.redis_state.get_capital() or 1000.0,
                    "operacoes_hoje": self.operacoes_hoje,
                    "pnl_dia_pct": 0.0,
                    "nivel_atual": 1,
                    "modo": "PAPER" if PAPER_MODE else "REAL",
                    "horario_atual": datetime.now().strftime("%H:%M")
                },
                "graph": indicadores,
                "flow": fluxo,
                "context": contexto,
            }

            logger.info("[AGENTS] Calling NEO...")
            resultado = await cyber.decidir(entrada)
            
            logger.info(f"[AGENTS] Result: {resultado.get('decisao', 'N/A')}")
            return resultado

        except Exception as e:
            logger.error(f"[AGENTS] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"decisao": "CANCELAR", "motivo": f"Erro agentes: {e}"}

    def _calcular_indicadores(self, candles):
        if not candles or len(candles) < 5:
            return {
                "sinal": "NEUTRO",
                "confianca": 0,
                "tendencia_5m": "INDEFINIDA",
                "tendencia_master_15m": "INDEFINIDA",
                "atr14_5m": 200,
            }

        closes = [c["close"] for c in candles]
        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

        ema9 = sum(closes[-9:]) / 9 if len(closes) >= 9 else closes[-1]
        ema21 = sum(closes[-21:]) / 21 if len(closes) >= 21 else ema9
        
        atr = (max(highs) - min(lows)) / 3

        if ema9 > ema21:
            tendencia = "ALTA"
            sinal = "COMPRA"
        elif ema9 < ema21:
            tendencia = "BAIXA"
            sinal = "VENDA"
        else:
            tendencia = "INDEFINIDA"
            sinal = "NEUTRO"

        confianca = random.randint(60, 80)

        return {
            "sinal": sinal,
            "confianca": confianca,
            "tendencia_5m": tendencia,
            "tendencia_master_15m": tendencia,
            "atr14_5m": int(atr),
            "ema9_5m": int(ema9),
            "ema21_5m": int(ema21),
        }

    def _calcular_fluxo(self, book, trades):
        bids_vol = sum(b["volume"] for b in book.get("bids", []))
        asks_vol = sum(a["volume"] for a in book.get("asks", []))
        
        cvd = bids_vol - asks_vol
        
        if cvd > 50:
            direcao = "COMPRA"
            forca = min(100, 50 + cvd)
        elif cvd < -50:
            direcao = "VENDA"
            forca = min(100, 50 + abs(cvd))
        else:
            direcao = "NEUTRO"
            forca = 50

        return {
            "direcao_fluxo": direcao,
            "forca_fluxo": forca,
            "cvd_total": cvd,
            "divergencia_cvd_preco": False,
        }

    async def _calcular_contexto(self):
        try:
            import yfinance as yf
            ibov = yf.Ticker("^BVSP")
            h = ibov.history(period="1d")
            ibov_variacao = 0.0
            if not h.empty:
                ibov_variacao = ((h['Close'].iloc[-1] / h['Open'].iloc[0]) - 1) * 100
        except:
            ibov_variacao = random.uniform(-1, 1)

        hora = datetime.now().hour
        
        if hora >= 17:
            alerta_corte = True
            regime = "ENCERRANDO"
        elif random.random() > 0.7:
            regime = "TRENDING"
        else:
            regime = "NORMAL"

        return {
            "status_macro": "NORMAL",
            "regime_mercado": regime,
            "alerta_finalizacao": hora >= 17,
            "score_contexto": 25,
            "ibov_variacao": ibov_variacao,
        }


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())
