# main.py
# CYBER TRADE WIN v3.1 — PATCHED: Cutoff 17:15, Shutdown gracioso, Horarios proibidos, Config loader, Rate limit TG

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
from utils.horarios import cutoff_atingido, horario_proibido, get_status_horario, minutos_para_cutoff
from utils.config_loader import carregar_config, get_nivel_capital, get_score_pesos, get_risk_params
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
DATA_SOURCE = os.getenv("DATA_SOURCE", "mt5")


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
        logger.info("[CYBER] WIN v3.0 started")
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
            self.tg.alertar("[OK] Cyber Trade WIN v3.0 started!")
        except Exception as e:
            logger.error(f"[ERR] Init: {e}")
            import traceback
            traceback.print_exc()

    async def _shutdown_gracioso(self):
        logger.info("[SHUTDOWN] Iniciando encerramento gracioso...")
        self.tg.alertar("🛑 [SHUTDOWN] Cutoff atingido — encerrando sistema")

        try:
            if self.exec:
                posicao = await self.exec.get_posicao_atual()
                if posicao and posicao.get("ativa"):
                    logger.warning(f"[SHUTDOWN] Posição aberta detectada: {posicao}")
                    self.tg.alertar(
                        f"⚠️ [SHUTDOWN] Fechando posição aberta: "
                        f"{posicao.get('direcao')} @ {posicao.get('preco_entrada')}"
                    )
                    try:
                        await self.exec.fechar_posicao(motivo="cutoff_horario")
                        self._salvar_log("EXEC", "Posição fechada no cutoff")
                    except Exception as e:
                        logger.error(f"[SHUTDOWN] Erro ao fechar posição: {e}")
                        self.tg.alertar(f"🚨 [SHUTDOWN] ERRO ao fechar posição: {e}")
                else:
                    logger.info("[SHUTDOWN] Nenhuma posição aberta")

            if self.db:
                resultado_final = self.db.get_resultado_hoje()
                ops_total = self.db.get_trades_hoje()
                capital = self.redis_state.get_capital() if self.redis_state else 0
                logger.info(f"[SHUTDOWN] Resultado dia: R${resultado_final:.2f} | Ops: {ops_total} | Capital: R${capital:.2f}")
                self.tg.alertar(
                    f"📊 [RESULTADO DIA]\nPnL: R${resultado_final:.2f}\nOperações: {ops_total}\nCapital: R${capital:.2f}"
                )

            if self.redis_state:
                self.redis_state.set("sistema_status", "ENCERRADO")
                self.redis_state.set("ultimo_encerramento", datetime.now().isoformat())

        except Exception as e:
            logger.error(f"[SHUTDOWN] Erro no encerramento gracioso: {e}")
            import traceback
            traceback.print_exc()

        logger.info("[SHUTDOWN] Encerramento completo")

    async def _loop(self):
        ciclo = 0
        print_pixel_header()
        logger.info("[CYBER] WIN v3.1 - Pixel Agents Mode")
        
        while True:
            ciclo += 1
            logger.info(f"[CYCLE {ciclo}] Running...")
            try:
                self.redis_state.set("heartbeat_main", datetime.now().isoformat(), ex=90)
            except Exception:
                pass

            await self._poll_telegram()

            if self._cutoff_atingido():
                logger.info("[STOP] Cutoff 17:15 WIN — encerrando")
                await self._shutdown_gracioso()
                break

            mins = minutos_para_cutoff()
            if mins <= 15 and mins > 0:
                logger.warning(f"[WARN] {mins} minutos para cutoff 17:15")

            await self._ciclo_completo(ciclo)
            await asyncio.sleep(10)

    async def _poll_telegram(self):
        try:
            updates = self.tg.get_updates()
            for update in updates:
                if "callback_query" in update:
                    cb = update["callback_query"]
                    data = cb.get("data", "")
                    if data == "proximo_dia":
                        self.tg.alertar("🔄 Buscando dia anterior...")
                        self.data_provider.avanca_proximo_dia()
                        if hasattr(self.data_provider, "limpar_cache"):
                            self.data_provider.limpar_cache()
                        elif hasattr(self.data_provider, "_cache_candles"):
                            self.data_provider._cache_candles = {}
                            logger.debug("[POLL] Cache de candles limpo via atributo interno")
        except Exception as e:
            logger.debug(f"Telegram poll: {e}")

    def _cutoff_atingido(self) -> bool:
        return cutoff_atingido()

    async def _ciclo_completo(self, num: int):
        try:
            proibido, motivo_horario = horario_proibido()
            # --- [SISTEMA] Atualiza Dashboard mesmo em horario proibido ---
            # Mover a atualização do HTML para cá para o dashboard não congelar no almoço
            if 'indicadores' in locals() and 'fluxo' in locals() and 'contexto' in locals():
                capital_atual = self.redis_state.get_capital() or 1000.0
                resultado_hoje = self.db.get_resultado_hoje()
                pnl_dia_pct = (resultado_hoje / capital_atual) * 100 if capital_atual > 0 else 0.0
                
                salvar_html({
                    "agentes": {
                        "architect": indicadores,
                        "morpheus": fluxo,
                        "oracle": contexto,
                        "neo": {} if 'resultado' not in locals() else resultado,
                    },
                    "sistema": {
                        "preco": preco_atual,
                        "pnl": pnl_dia_pct,
                        "ops": self.operacoes_hoje,
                        "modo": "PAPER" if PAPER_MODE else "REAL",
                        "info_dados": info_dados,
                    },
                    "decisao": {} if 'resultado' not in locals() else resultado,
                })



            logger.info(f"[CYCLE {num}] Step 1: Getting data...")

            candles_5m = await self.data_provider.get_dados_candle("5min", 50)
            preco_atual = await self.data_provider.get_preco_atual()
            book = await self.data_provider.get_book()
            trades = await self.data_provider.get_trades()
            info_dados = self.data_provider.get_info_dados()

            candles_15m = []
            if len(candles_5m) >= 20:
                try:
                    candles_15m = await self.data_provider.get_dados_candle("15min", 30)
                except Exception:
                    candles_15m = []
                indicadores = self._calcular_indicadores(candles_5m, candles_15m=candles_15m)
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

            logger.info(f"[CYCLE {num}] Preco: {preco_atual} | Candles: {len(candles_5m)} | Dados: {info_dados.get('ultimo_candle', 'N/A')}")

            # Verificar se dia historico terminou
            if info_dados.get("ja_terminou") and not info_dados.get("dia_pregao"):
                dia_fim = info_dados.get("ultimo_candle", "?")
                self.tg.send_inline(
                    f"📅 Dados do dia {dia_fim} finalizados.\nBuscar dia anterior?",
                    "▶️ Proximo dia",
                    "proximo_dia"
                )

            self.redis_state.set("preco_atual_win", str(preco_atual))
            self.redis_state.set("ciclo_atual", str(num))
            self.redis_state.set("info_dados", json.dumps(info_dados))
            self._salvar_log("SYSTEM", f"Ciclo {num} | Preço: {preco_atual} | Dados: {info_dados.get('ultimo_candle', 'N/A')}")

            if PAPER_MODE:
                self._alertar_telegram(f"[{num}] Preco: {preco_atual} | Dados: {info_dados.get('ultimo_candle', 'N/A')} | Analisando...")

            logger.info(f"[CYCLE {num}] Step 2: Running AGENTS (LLM)...")

            resultado = await self._executar_agentes(
                candles_5m, book, trades, preco_atual,
                indicadores=indicadores, fluxo=fluxo, contexto=contexto
            )

            logger.info(f"[CYCLE {num}] Step 3: Decision = {resultado.get('decisao', 'N/A')}")

            self._salvar_log("NEO", resultado.get('decisao', 'N/A'))

            print_agente("neo", {
                "Decisao": resultado.get("decisao"),
                "Score": resultado.get("score_final"),
                "Direcao": resultado.get("direcao"),
                "Motivo": resultado.get("motivo"),
            }, "🎯")

            print_status_sistema(preco_atual, pnl_dia_pct, self.operacoes_hoje, "PAPER" if PAPER_MODE else "REAL", info_dados)

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
                    "info_dados": info_dados,
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
                    gatilho = resultado.get("gatilho", {})

                    def _on_gatilho_done(task: asyncio.Task):
                        if task.cancelled():
                            logger.warning("[EXEC] Task gatilho cancelada")
                            self.tg.alertar("⚠️ [EXEC] Task de gatilho foi cancelada")
                        elif task.exception():
                            err = task.exception()
                            logger.error(f"[EXEC] FALHA NO GATILHO: {err}", exc_info=err)
                            self.tg.alertar(f"🚨 [EXEC] Gatilho falhou: {type(err).__name__}: {err}")
                            self._salvar_log("EXEC", f"ERRO gatilho: {err}")

                    task = asyncio.create_task(self.exec.executar_gatilho(gatilho))
                    task.add_done_callback(_on_gatilho_done)

                    self._alertar_telegram(
                        f"🎯 [ARMADO] {direcao} | Score:{score} | Entrada:{entrada} | Stop:{stop}",
                        prioridade="urgente"
                    )
                    self._salvar_log("EXEC", f"Trade armado: {direcao} @ {entrada}")
                    logger.info(f"[CYCLE {num}] >>> ARMAR {direcao} Score:{score}")
                else:
                    self.tg.alertar(f"[REJEITADO] Validação falhou")
                    self._salvar_log("EXEC", "Falha ao armar trade")
                    resultado["decisao"] = "CANCELAR"
                    resultado["motivo"] = "Erro execução"
            else:
                motivo = resultado.get("motivo", "sem motivo")
                self._alertar_telegram(f"[OK] {resultado.get('decisao', 'CANCELAR')} - {motivo}")
                logger.info(f"[CYCLE {num}] >>> {resultado.get('decisao')}: {motivo}")

        except Exception as e:
            logger.error(f"[CYCLE {num}] Error: {e}")
            import traceback
            traceback.print_exc()

    async def _executar_agentes(self, candles, book, trades, preco_atual,
                                 indicadores=None, fluxo=None, contexto=None):
        try:
            from agents.cyber_agent import CyberAgent

            cyber = CyberAgent(self.router, self.redis_state)

            if indicadores is None:
                indicadores = self._calcular_indicadores(candles)
            if fluxo is None:
                fluxo = self._calcular_fluxo(book, trades)
            if contexto is None:
                contexto = await self._calcular_contexto()

            self._salvar_log("ARCHITECT", f"Sinal: {indicadores.get('sinal')} | Conf: {indicadores.get('confianca')} | ATR: {indicadores.get('atr14_5m'):.0f}")
            self._salvar_log("MORPHEUS", f"Fluxo: {fluxo.get('direcao_fluxo')} | Forca: {fluxo.get('forca_fluxo')} | CVD: {fluxo.get('cvd_total')}")
            self._salvar_log("ORACLE", f"Regime: {contexto.get('regime_mercado')} | Macro: {contexto.get('status_macro')} | Tend: {contexto.get('tendencia_mercado')}")

            capital_atual = self.redis_state.get_capital() or 1000.0
            resultado_hoje = self.db.get_resultado_hoje()
            pnl_dia_pct = (resultado_hoje / capital_atual) * 100 if capital_atual > 0 else 0.0
            self.operacoes_hoje = self.db.get_trades_hoje()

            nivel_info = get_nivel_capital(capital_atual)
            status_horario = get_status_horario()

            entrada = {
                "estado_sistema": {
                    "capital_atual": capital_atual,
                    "operacoes_hoje": self.operacoes_hoje,
                    "pnl_dia_pct": round(pnl_dia_pct, 2),
                    "resultado_hoje": resultado_hoje,
                    "nivel_atual": nivel_info["nivel"],
                    "nivel_nome": nivel_info["nome"],
                    "max_contratos": nivel_info["max_contratos"],
                    "score_minimo": nivel_info["score_minimo"],
                    "modo": "PAPER" if PAPER_MODE else "REAL",
                    "horario": status_horario,
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

    def _calcular_indicadores(self, candles, candles_15m=None):
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

        tendencia_5m, sinal = detectar_tendencia(ema9, ema21)
        confianca = calcular_confianca(sinal, ema9, ema21, rsi, atr14)

        if candles_15m and len(candles_15m) >= 20:
            closes_15m = [float(c["close"]) for c in candles_15m]
            ema9_15m = calcular_ema(closes_15m, 9)
            ema21_15m = calcular_ema(closes_15m, 21)
            tendencia_15m, _ = detectar_tendencia(ema9_15m, ema21_15m)
        else:
            tendencia_15m = "INDISPONIVEL_15M"
            logger.debug("[ARCHITECT] Candles 15m não disponíveis — tendencia_master indisponível")

        return {
            "sinal": sinal,
            "confianca": confianca,
            "tendencia_5m": tendencia_5m,
            "tendencia_master_15m": tendencia_15m,
            "atr14_5m": round(atr14, 1),
            "rsi_14": round(rsi, 1),
            "ema9_5m": round(ema9, 1),
            "ema21_5m": round(ema21, 1),
            "macd": macd["macd"],
            "macd_sinal": macd["sinal"],
            "macd_hist": macd["histograma"],
        }

    def _calcular_fluxo(self, book, trades):
        cvd_tape = 0
        vol_compra = 0
        vol_venda = 0

        if trades:
            for t in trades:
                vol = float(t.get("volume", t.get("qty", 0)))
                side = str(t.get("side", t.get("type", ""))).upper()
                if side in ("BUY", "COMPRA", "B", "1"):
                    vol_compra += vol
                    cvd_tape += vol
                elif side in ("SELL", "VENDA", "S", "2"):
                    vol_venda += vol
                    cvd_tape -= vol

        if vol_compra == 0 and vol_venda == 0:
            bids_vol = sum(float(b.get("volume", b.get("qty", 0))) for b in book.get("bids", []))
            asks_vol = sum(float(a.get("volume", a.get("qty", 0))) for a in book.get("asks", []))
            cvd_tape = bids_vol - asks_vol
            vol_compra = bids_vol
            vol_venda = asks_vol

        vol_total = vol_compra + vol_venda
        if vol_total == 0:
            vol_total = 1

        delta_pct = (cvd_tape / vol_total) * 100

        THRESHOLD_FORTE = 20.0
        THRESHOLD_FRACO = 5.0

        if delta_pct >= THRESHOLD_FORTE:
            direcao = "COMPRA"
            forca = min(100, 50 + delta_pct * 2)
        elif delta_pct <= -THRESHOLD_FORTE:
            direcao = "VENDA"
            forca = min(100, 50 + abs(delta_pct) * 2)
        elif delta_pct >= THRESHOLD_FRACO:
            direcao = "COMPRA_FRACA"
            forca = 30 + delta_pct
        elif delta_pct <= -THRESHOLD_FRACO:
            direcao = "VENDA_FRACA"
            forca = 30 + abs(delta_pct)
        else:
            direcao = "NEUTRO"
            forca = 50

        return {
            "direcao_fluxo": direcao,
            "forca_fluxo": round(forca, 1),
            "cvd_total": round(cvd_tape, 0),
            "cvd_delta_pct": round(delta_pct, 2),
            "vol_compra": round(vol_compra, 0),
            "vol_venda": round(vol_venda, 0),
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

        if ibov_variacao > 1.5:
            status_macro = "BULL_FORTE"
            score_contexto = 80
        elif ibov_variacao > 0.5:
            status_macro = "BULL"
            score_contexto = 65
        elif ibov_variacao >= -0.5:
            status_macro = "NEUTRO"
            score_contexto = 50
        elif ibov_variacao >= -1.5:
            status_macro = "BEAR"
            score_contexto = 35
        else:
            status_macro = "BEAR_FORTE"
            score_contexto = 15

        if regime == "TRENDING":
            score_contexto = min(100, score_contexto + 10)
        elif regime == "RANGING":
            score_contexto = max(0, score_contexto - 10)
        elif regime in ("INDISPONIVEL", "INDEFINIDO"):
            score_contexto = 25

        status_horario = get_status_horario()

        return {
            "status_macro": status_macro,
            "regime_mercado": regime,
            "tendencia_mercado": tendencia_mercado,
            "alerta_finalizacao": status_horario["alerta_pre_cutoff"],
            "minutos_para_cutoff": status_horario["minutos_para_cutoff"],
            "score_contexto": score_contexto,
            "ibov_variacao": round(ibov_variacao, 2),
        }

    async def _get_ibov_variacao(self) -> float:
        CACHE_KEY = "cache_ibov_variacao"
        CACHE_TTL = 300

        try:
            cached = self.redis_state.get(CACHE_KEY)
            if cached is not None:
                return float(cached)
        except Exception:
            pass

        try:
            import yfinance as yf
            ibov = yf.Ticker("^BVSP")
            h = ibov.history(period="1d")
            if not h.empty:
                variacao = ((h['Close'].iloc[-1] / h['Open'].iloc[0]) - 1) * 100
                try:
                    self.redis_state.set(CACHE_KEY, str(round(variacao, 4)), ex=CACHE_TTL)
                except Exception:
                    pass
                logger.debug(f"[ORACLE] IBOV atualizado: {variacao:.2f}%")
                return variacao
        except Exception as e:
            logger.warning(f"[ORACLE] IBOV error: {e}")

        return 0.0

    def _alertar_telegram(self, mensagem: str, prioridade: str = "normal"):
        import time

        if not hasattr(self, "_tg_ultimo_envio"):
            self._tg_ultimo_envio = 0
            self._tg_fila_normal = []

        agora = time.time()

        if prioridade == "urgente":
            try:
                self.tg.alertar(mensagem)
                self._tg_ultimo_envio = agora
            except Exception as e:
                logger.warning(f"[TG] Falha ao enviar urgente: {e}")
            return

        MIN_INTERVALO = 8.0
        if (agora - self._tg_ultimo_envio) >= MIN_INTERVALO:
            try:
                self.tg.alertar(mensagem)
                self._tg_ultimo_envio = agora
            except Exception as e:
                logger.warning(f"[TG] Falha ao enviar: {e}")
        else:
            logger.debug(f"[TG] Throttled: {mensagem[:50]}...")

    def _salvar_log(self, agente: str, mensagem: str):
        try:
            log_entry = {
                "agente": agente,
                "mensagem": mensagem,
                "timestamp": datetime.now().isoformat()
            }
            ts = datetime.now().strftime('%H%M%S%f')
            key = f"log:{agente.lower()}:{ts}"
            self.redis_state.set(key, json.dumps(log_entry), ex=86400)
        except Exception as e:
            logger.warning(f"Log error: {e}")


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())