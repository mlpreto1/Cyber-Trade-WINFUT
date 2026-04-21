# main.py
# CYBER TRADE WIN v2.4 — Main Loop Completo com LLM e Indicadores Reais

import asyncio
import logging
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from utils.indicadores import (
    calcular_ema,
    calcular_atr,
    calcular_rsi,
    calcular_macd,
    detectar_regime,
    detectar_tendencia,
    calcular_confianca
)
from utils.pixel_agents import (
    print_pixel_header,
    print_agente,
    print_status_sistema,
    print_decisao,
    print_ciclo,
    salvar_html
)

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
        logger.info("[CYBER] WIN v2.2 started")
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

            from agents.exec_agent import ExecAgent
            self.exec = ExecAgent(self.redis_state, self.db, self.tg)

            logger.info("[OK] Components initialized")
            self.tg.alertar("[OK] Cyber Trade WIN v2.2 started!")
        except Exception as e:
            logger.error(f"[ERR] Init: {e}")
            import traceback
            traceback.print_exc()

    async def _loop(self):
        ciclo = 0
        print_pixel_header()
        logger.info("[CYBER] WIN v2.4 - Pixel Agents Mode")
        
        while True:
            ciclo += 1
            logger.info(f"[CYCLE {ciclo}] Running...")

            if self._cutoff_atingido():
                logger.info("[STOP] Cutoff reached")
                self.tg.alertar("[STOP] Cutoff 17:30 - encerrando")
                break

            await self._ciclo_completo(ciclo)
            await asyncio.sleep(10)

    def _cutoff_atingido(self) -> bool:
        agora = datetime.now().time()
        return agora.hour >= 17 and agora.minute >= 30

    async def _ciclo_completo(self, num: int):
        try:
            logger.info(f"[CYCLE {num}] Step 1: Getting data...")

            candles_5m = await self.data_provider.get_dados_candle("5min", 50)
            preco_atual = await self.data_provider.get_preco_atual()
            book = await self.data_provider.get_book()
            trades = await self.data_provider.get_trades()

            if len(candles_5m) >= 20:
                indicadores = self._calcular_indicadores(candles_5m)
                fluxo = self._calcular_fluxo(book, trades)
                contexto = await self._calcular_contexto()

                capital_atual = self.redis_state.get_capital() or 1000.0
                resultado_hoje = self.db.get_resultado_hoje()
                pnl_dia_pct = (resultado_hoje / capital_atual) * 100 if capital_atual > 0 else 0.0
                self.operacoes_hoje = self.db.get_trades_hoje()

                print_ciclo(num)

                print_agente("architect", {
                    "Sinal": indicadores.get("sinal"),
                    "Confianca": indicadores.get("confianca"),
                    "EMA9": indicadores.get("ema9_5m"),
                    "ATR14": indicadores.get("atr14_5m"),
                    "RSI14": indicadores.get("rsi14_5m"),
                }, "🏗️")

                print_agente("morpheus", {
                    "Fluxo": fluxo.get("direcao_fluxo"),
                    "Forca": fluxo.get("forca_fluxo"),
                    "CVD": fluxo.get("cvd_total"),
                }, "🌊")

                print_agente("oracle", {
                    "Regime": contexto.get("regime_mercado"),
                    "Macro": contexto.get("status_macro"),
                    "Tendencia": contexto.get("tendencia_mercado"),
                }, "🔮")

            logger.info(f"[CYCLE {num}] Preco: {preco_atual} | Candles: {len(candles_5m)}")

            self.redis_state.set("preco_atual_win", str(preco_atual))
            self.redis_state.set("ciclo_atual", str(num))
            self._salvar_log("SYSTEM", f"Ciclo {num} | Preço: {preco_atual} | Candles: {len(candles_5m)}")

            if PAPER_MODE:
                self.tg.alertar(f"[{num}] Preco: {preco_atual} | Analisando...")

            logger.info(f"[CYCLE {num}] Step 2: Running AGENTS (LLM)...")

            resultado = await self._executar_agentes(candles_5m, book, trades, preco_atual)

            logger.info(f"[CYCLE {num}] Step 3: Decision = {resultado.get('decisao', 'N/A')}")

            self._salvar_log("NEO", resultado.get('decisao', 'N/A'))

            print_agente("neo", {
                "Decisao": resultado.get("decisao"),
                "Score": resultado.get("score_final"),
                "Direcao": resultado.get("direcao"),
                "Motivo": resultado.get("motivo"),
            }, "🎯")

            print_status_sistema(preco_atual, pnl_dia_pct, self.operacoes_hoje, "PAPER" if PAPER_MODE else "REAL")

            salvar_html({
                "agentes": {
                    "architect": indicadores,
                    "morpheus": fluxo,
                    "oracle": contexto,
                    "neo": resultado,
                },
                "sistema": {
                    "preco": preco_atual,
                    "pnl": pnl_dia_pct,
                    "ops": self.operacoes_hoje,
                    "modo": "PAPER" if PAPER_MODE else "REAL",
                },
                "decisao": resultado,
            })

            if resultado.get("decisao") == "ARMAR":
                score = resultado.get("score_final", 0)
                direcao = resultado.get("direcao", "?")
                entrada = resultado.get("entrada_zona", 0)
                stop = resultado.get("stop", 0)

                exec_ok = await self.exec.armar(resultado) if self.exec else False

                if exec_ok and self.exec:
                    asyncio.create_task(self.exec.executar_gatilho(resultado.get("gatilho", {})))
                    self.tg.alertar(f"[ARMADO] {direcao} | Score:{score} | Entrada:{entrada} | Stop:{stop}")
                    self._salvar_log("EXEC", f"Trade armado: {direcao} @ {entrada}")
                    logger.info(f"[CYCLE {num}] >>> ARMAR {direcao} Score:{score}")
                else:
                    self.tg.alertar(f"[REJEITADO] Validação falhou")
                    self._salvar_log("EXEC", "Falha ao armar trade")
                    resultado["decisao"] = "CANCELAR"
                    resultado["motivo"] = "Erro execução"
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

            self._salvar_log("ARCHITECT", f"Sinal: {indicadores.get('sinal')} | Conf: {indicadores.get('confianca')} | ATR: {indicadores.get('atr14_5m'):.0f}")
            self._salvar_log("MORPHEUS", f"Fluxo: {fluxo.get('direcao_fluxo')} | Forca: {fluxo.get('forca_fluxo')} | CVD: {fluxo.get('cvd_total')}")
            self._salvar_log("ORACLE", f"Regime: {contexto.get('regime_mercado')} | Macro: {contexto.get('status_macro')} | Tend: {contexto.get('tendencia_mercado')}")

            capital_atual = self.redis_state.get_capital() or 1000.0
            resultado_hoje = self.db.get_resultado_hoje()
            pnl_dia_pct = (resultado_hoje / capital_atual) * 100 if capital_atual > 0 else 0.0
            self.operacoes_hoje = self.db.get_trades_hoje()

            entrada = {
                "estado_sistema": {
                    "capital_atual": capital_atual,
                    "operacoes_hoje": self.operacoes_hoje,
                    "pnl_dia_pct": round(pnl_dia_pct, 2),
                    "resultado_hoje": resultado_hoje,
                    "nivel_atual": 1,
                    "modo": "PAPER" if PAPER_MODE else "REAL",
                    "horario_atual": datetime.now().strftime("%H:%M")
                },
                "graph": indicadores,
                "flow": fluxo,
                "context": contexto,
            }

            self._salvar_log("SYSTEM", f"PnL: {pnl_dia_pct:.2f}% | Ops: {self.operacoes_hoje} | Capital: R${capital_atual:.0f}")

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
        if not candles or len(candles) < 20:
            return {
                "sinal": "NEUTRO",
                "confianca": 0,
                "tendencia_5m": "INDEFINIDA",
                "tendencia_master_15m": "INDEFINIDA",
                "atr14_5m": 200,
                "rsi_14": 50,
                "ema9_5m": 0,
                "ema21_5m": 0,
            }

        closes = [float(c["close"]) for c in candles]
        highs = [float(c["high"]) for c in candles]
        lows = [float(c["low"]) for c in candles]

        ema9 = calcular_ema(closes, 9)
        ema21 = calcular_ema(closes, 21)
        atr14 = calcular_atr(candles, 14)
        rsi = calcular_rsi(candles, 14)
        macd = calcular_macd(candles)

        tendencia, sinal = detectar_tendencia(ema9, ema21)
        confianca = calcular_confianca(sinal, ema9, ema21, rsi, atr14)

        return {
            "sinal": sinal,
            "confianca": confianca,
            "tendencia_5m": tendencia,
            "tendencia_master_15m": tendencia,
            "atr14_5m": round(atr14, 1),
            "rsi_14": round(rsi, 1),
            "ema9_5m": round(ema9, 1),
            "ema21_5m": round(ema21, 1),
            "macd": macd["macd"],
            "macd_sinal": macd["sinal"],
            "macd_hist": macd["histograma"],
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
            candles = await self.data_provider.get_dados_candle("5min", 50)

            if len(candles) >= 20:
                regime = detectar_regime(candles, 14)
                closes = [float(c["close"]) for c in candles]
                ema9 = calcular_ema(closes, 9)
                ema21 = calcular_ema(closes, 21)

                if ema9 > ema21 * 1.005:
                    tendencia_mercado = "ALTA"
                elif ema9 < ema21 * 0.995:
                    tendencia_mercado = "BAIXA"
                else:
                    tendencia_mercado = "INDEFINIDA"
            else:
                regime = "INDISPONIVEL"
                tendencia_mercado = "INDEFINIDA"

            ibov_variacao = await self._get_ibov_variacao()

        except Exception as e:
            logger.warning(f"[ORACLE] Contexto error: {e}")
            regime = "INDISPONIVEL"
            tendencia_mercado = "INDEFINIDA"
            ibov_variacao = 0.0

        hora = datetime.now().hour

        return {
            "status_macro": "NORMAL",
            "regime_mercado": regime,
            "tendencia_mercado": tendencia_mercado,
            "alerta_finalizacao": hora >= 17,
            "score_contexto": 25,
            "ibov_variacao": round(ibov_variacao, 2),
        }

    async def _get_ibov_variacao(self) -> float:
        try:
            import yfinance as yf
            ibov = yf.Ticker("^BVSP")
            h = ibov.history(period="1d")
            if not h.empty:
                return ((h['Close'].iloc[-1] / h['Open'].iloc[0]) - 1) * 100
        except Exception as e:
            logger.warning(f"[ORACLE] IBOV error: {e}")
        return 0.0

    def _salvar_log(self, agente: str, mensagem: str):
        try:
            log_entry = {
                "agente": agente,
                "mensagem": mensagem,
                "timestamp": datetime.now().isoformat()
            }
            key = f"log:{agente.lower()}:{datetime.now().strftime('%H%M%S')}"
            self.redis_state.set(key, json.dumps(log_entry))
        except Exception as e:
            logger.warning(f"Log error: {e}")


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())