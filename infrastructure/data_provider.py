# infrastructure/data_provider.py
# Cyber Trade WIN v2.2 — Data Provider com Fontes Reais

import asyncio
import logging
import os
import requests
from datetime import datetime, timedelta
from calendar import monthcalendar

_feriados_b3_cache = {}
_ultimo_update = None

def _atualizar_feriados_se_necessario():
    global _feriados_b3_cache, _ultimo_update
    agora = datetime.now()
    ano = agora.year
    
    if _ultimo_update and _ultimo_update.year == ano and _feriados_b3_cache.get("ano") == ano:
        return
    
    if agora.month == 12 and agora.day >= 10:
        try:
            url = f"https://b3.com.br/pt_br/mercados/calendario"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                _feriados_b3_cache = {"ano": ano, "atualizado": True}
                logger.info(f"[B3] Feriados {ano} atualizados")
                _ultimo_update = agora
                return
        except:
            pass
    
    _feriados_b3_cache = {"ano": ano, "padrao": True}
    _ultimo_update = agora

def _dia_de_pregao() -> bool:
    _atualizar_feriados_se_necessario()
    
    agora = datetime.now()
    if agora.weekday() >= 5:
        return False

    FERIADOS_B3_2026 = [
        (1, 1),    # Confraternização Universal
        (2, 16),   # Carnaval
        (2, 17),   # Carnaval
        (4, 3),    # Sexta-feira Santa
        (4, 21),   # Tiradentes
        (5, 1),    # Dia do Trabalho
        (6, 4),    # Corpus Christi
        (9, 7),    # Independência do Brasil
        (10, 12),  # Nossa Senhora de Aparecida
        (11, 2),   # Finados
        (11, 20),  # Consciência Negra
        (12, 24),  # Véspera de Natal
        (12, 25),  # Natal
    ]

    if (agora.month, agora.day) in FERIADOS_B3_2026:
        return False
    return True


from typing import Dict, List, Optional

logger = logging.getLogger("data_provider")

REQUESTS_AVAILABLE = True
YFINANCE_AVAILABLE = False
MT5_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    pass

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 não disponível")

MT5_SYMBOL = "WIN$"  # Mini indice continuo
MT5_SYMBOLS = ["WIN$", "WINM26", "WINJ26", "WIN"]  # Tentativas em ordem
MT5_TIMEFRAMES = {
    "1min": mt5.TIMEFRAME_M1 if MT5_AVAILABLE else 1,
    "5min": mt5.TIMEFRAME_M5 if MT5_AVAILABLE else 5,
    "15min": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else 15,
    "30min": mt5.TIMEFRAME_M30 if MT5_AVAILABLE else 30,
    "1h": mt5.TIMEFRAME_H1 if MT5_AVAILABLE else 16385,
    "4h": mt5.TIMEFRAME_H4 if MT5_AVAILABLE else 16388,
}

def _dia_de_pregao() -> bool:
    agora = datetime.now()
    if agora.weekday() >= 5:
        return False

    FERIADOS_B3_2026 = [
        (1, 1),    # Confraternização Universal
        (2, 16),   # Carnaval
        (2, 17),   # Carnaval
        (4, 3),    # Sexta-feira Santa
        (4, 21),   # Tiradentes
        (5, 1),    # Dia do Trabalho
        (6, 4),    # Corpus Christi
        (9, 7),    # Independência do Brasil
        (10, 12),  # Nossa Senhora de Aparecida
        (11, 2),   # Finados
        (11, 20),  # Consciência Negra
        (12, 24),  # Véspera de Natal
        (12, 25),  # Natal
    ]

    if (agora.month, agora.day) in FERIADOS_B3_2026:
        return False
    return True

def _eh_dia_util(dia: datetime) -> bool:
    if dia.weekday() >= 5:
        return False
    FERIADOS = [
        (1, 1), (2, 16), (2, 17), (4, 3), (4, 21), (5, 1),
        (6, 4), (9, 7), (10, 12), (11, 2), (11, 20), (12, 24), (12, 25),
    ]
    if (dia.month, dia.day) in FERIADOS:
        return False
    return True

def _dia_util_4_semanas_atras() -> datetime:
    agora = datetime.now()
    for i in range(28, 40):
        dia = agora - timedelta(days=i)
        if _eh_dia_util(dia):
            logger.info(f"[MT5] 4 semanas atras: {dia.date()} (weekday={dia.weekday()})")
            return dia
    return agora - timedelta(days=28)

def _proximo_dia_util(dia: datetime) -> datetime:
    for i in range(1, 10):
        novo_dia = dia - timedelta(days=i)
        if _eh_dia_util(novo_dia):
            logger.info(f"[MT5] Proximo dia util: {novo_dia.date()}")
            return novo_dia
    return dia - timedelta(days=1)

def _horario_mercado_aberto() -> bool:
    agora = datetime.now()
    hora_min = agora.hour * 60 + agora.minute
    return 555 <= hora_min <= 1050


class DataProvider:
    def __init__(self, source: str = "yahoo"):
        self.source = source
        self.redis_state = None
        self._ultimo_preco = 130000.0
        self._ibov_base = 130000.0
        self._preco_win_valido = False
        self._brapi_token = os.getenv("BRAPI_TOKEN", "")
        self._mt5_inicializado = False
        self._cache_candles = {}
        self._cache_ttl_segundos = 30
        self._dia_offset = 0
        self._dia_inicial = None
        self._perguntou_proximo = False
        self._ja_terminou_dia = False

    def set_redis(self, redis_state):
        self.redis_state = redis_state

    def _init_mt5(self) -> bool:
        if not MT5_AVAILABLE:
            return False
        if self._mt5_inicializado:
            return True
        try:
            MT5_PATHS = [
                "C:/Program Files/Clear Investimentos MT5 Terminal/terminal64.exe",
                "C:/Program Files/Clear Investimentos MT5 Terminal/terminal.exe",
            ]
            import os
            for path in MT5_PATHS:
                if os.path.exists(path):
                    if mt5.initialize(path):
                        self._mt5_inicializado = True
                        logger.info(f"[MT5] Inicializado: {path}")
                        return True
            
            if mt5.initialize():
                self._mt5_inicializado = True
                logger.info("[MT5] Inicializado com sucesso")
                return True
            
            erro = mt5.last_error()
            logger.warning(f"[MT5] Erro ao inicializar: {erro}")
            return False
        except Exception as e:
            logger.warning(f"[MT5] Exceção: {e}")
            return False

    def _shutdown_mt5(self):
        if self._mt5_inicializado:
            try:
                mt5.shutdown()
                self._mt5_inicializado = False
            except:
                pass

    async def get_dados_candle(self, timeframe: str = "5min", candles: int = 20) -> List[dict]:
        cache_key = f"{self.source}:{timeframe}:{candles}"
        cached = self._cache_candles.get(cache_key)
        if cached:
            if (datetime.now() - cached["timestamp"]).total_seconds() < self._cache_ttl_segundos:
                logger.debug(f"[CACHE] Candles {cache_key} retornados do cache")
                return cached["data"]

        if self.source == "mt5":
            if _dia_de_pregao() and _horario_mercado_aberto():
                self._dia_offset = 0
                self._dia_inicial = None
                self._perguntou_proximo = False
                self._ja_terminou_dia = False
                logger.info("[MT5] Mercado ABERTO - dados tempo real")
                data = await self._buscar_mt5_candles_tempo_real(timeframe, candles)
            else:
                if self._dia_inicial is None:
                    self._dia_inicial = _dia_util_4_semanas_atras()
                    self._dia_offset = 0
                    self._perguntou_proximo = False
                    self._ja_terminou_dia = False
                    logger.warning(f"[MT5] Mercado FECHADO - iniciando do dia {self._dia_inicial.date()}")
                
                data = await self._buscar_mt5_candles_por_dia(timeframe, candles, self._dia_offset)
                
                if data:
                    ultimo_candle = data[-1].get("timestamp", "")[:10]
                    if self._dia_offset == 0:
                        logger.info(f"[MT5] Dia atual: {ultimo_candle}")
                else:
                    self._ja_terminou_dia = True
        elif self.source == "brapi":
            data = await self._buscar_brapi_win(timeframe, candles)
        elif self.source == "profit":
            data = await self._buscar_profit_win(timeframe, candles)
        elif self.source == "yahoo":
            data = await self._buscar_yahoo_ibov(candles)
        else:
            data = await self._buscar_yahoo_ibov(candles)

        self._cache_candles[cache_key] = {"data": data, "timestamp": datetime.now()}
        return data

    def get_info_dados(self) -> dict:
        info = {
            "source": self.source,
            "dia_pregao": _dia_de_pregao(),
            "horario_aberto": _horario_mercado_aberto(),
            "dia_offset": self._dia_offset,
            "ja_terminou": self._ja_terminou_dia,
        }
        cache_key = f"{self.source}:5min:50"
        cached = self._cache_candles.get(cache_key)
        if cached and cached.get("data"):
            dados = cached["data"]
            if dados:
                primeiro = dados[0].get("timestamp", "")
                ultimo = dados[-1].get("timestamp", "")
                info["primeiro_candle"] = primeiro[:10] if primeiro else ""
                info["ultimo_candle"] = ultimo[:10] if ultimo else ""
                info["qtd_candles"] = len(dados)
        return info

    def pedido_proximo_dia(self) -> tuple:
        if self._ja_terminou_dia or self._perguntou_proximo:
            return (False, None)
        if not _dia_de_pregao() and not _horario_mercado_aberto():
            return (True, self._dia_offset)
        return (False, None)

    def avanca_proximo_dia(self):
        if self._dia_offset == 0 and self._dia_inicial:
            data = self._dia_inicial
            self._dia_offset = 1
        else:
            data = _proximo_dia_util(self._dia_inicial)
        self._perguntou_proximo = True
        self._ja_terminou_dia = False
        self._cache_candles = {}
        logger.info(f"[MT5] Avanzando para offset {self._dia_offset}: {data.date()}")

    async def get_preco_atual(self) -> float:
        if self.source == "mt5":
            if _dia_de_pregao() and _horario_mercado_aberto():
                return await self._get_preco_mt5()
            else:
                logger.warning("[MT5] Mercado fechado, preco historico")
                return await self._get_preco_mt5_historico()
        elif self.source == "brapi":
            return await self._get_preco_brapi()
        elif self.source == "profit":
            return await self._get_preco_win_profit()
        elif self.source == "yahoo":
            ibov = await self._get_ibov_atual()
            return self._calcular_preco_win_deterministico(ibov)
        return self._calcular_preco_win_deterministico(self._ibov_base)

    async def get_book(self) -> Dict:
        if self.source == "mt5":
            return await self._get_book_mt5()
        elif self.source == "brapi":
            return await self._get_book_brapi()
        elif self.source == "profit":
            return await self._get_book_profit()
        return self._gerar_book_simulado()

    async def get_trades(self) -> List[dict]:
        return self._gerar_trades_simulados(10)

    async def _get_preco_mt5(self) -> float:
        if not self._init_mt5():
            return self._calcular_preco_win_deterministico(await self._get_ibov_atual())

        # Try multiple WIN symbols
        for sym in MT5_SYMBOLS:
            try:
                tick = mt5.symbol_info_tick(sym)
                if tick and tick.last and tick.last > 0:
                    preco = float(tick.last)
                    self._preco_win_valido = True
                    self._ultimo_preco = preco
                    logger.info(f"[MT5] {sym} price: {preco}")
                    return preco
            except Exception as e:
                logger.warning(f"[MT5] Erro {sym}: {e}")
                continue

        logger.warning("[MT5] Nenhum preco WIN encontrado")
        return await self._get_preco_mt5_historico()

    async def _get_preco_mt5_historico(self) -> float:
        if not self._init_mt5():
            return self._ultimo_preco if self._ultimo_preco > 0 else 130000.0

        for sym in MT5_SYMBOLS:
            try:
                mt5.symbol_select(sym, True)
                rates = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_M5, 0, 1)
                if rates is not None and len(rates) > 0:
                    preco = float(rates[0][4])
                    self._preco_win_valido = True
                    self._ultimo_preco = preco
                    logger.info(f"[MT5] Ultimo preco {sym}: {preco}")
                    return preco
            except Exception as e:
                logger.warning(f"[MT5] historico error {sym}: {e}")
                continue

        return self._ultimo_preco if self._ultimo_preco > 0 else 130000.0

    async def _buscar_mt5_candles_tempo_real(self, timeframe: str, candles: int) -> List[dict]:
        if not self._init_mt5():
            return []

        tf = MT5_TIMEFRAMES.get(timeframe, mt5.TIMEFRAME_M5)

        for sym in MT5_SYMBOLS:
            try:
                mt5.symbol_select(sym, True)
                rates = mt5.copy_rates_from_pos(sym, tf, 0, candles)
                if rates is not None and len(rates) > 0:
                    candles_data = []
                    for r in rates:
                        candles_data.append({
                            "timestamp": datetime.fromtimestamp(r[0]).isoformat(),
                            "open": float(r[1]),
                            "high": float(r[2]),
                            "low": float(r[3]),
                            "close": float(r[4]),
                            "volume": int(r[5]),
                        })
                    logger.info(f"[MT5] Tempo real {sym}: {len(candles_data)} candles")
                    return candles_data
            except Exception as e:
                logger.warning(f"[MT5] tempo real error {sym}: {e}")
                continue

        return []

    async def _buscar_mt5_candles_por_dia(self, timeframe: str, candles: int, dia_offset: int) -> List[dict]:
        if not self._init_mt5():
            return []

        tf = MT5_TIMEFRAMES.get(timeframe, mt5.TIMEFRAME_M5)

        target = self._dia_inicial
        if dia_offset > 0:
            for _ in range(dia_offset):
                target = _proximo_dia_util(target)

        from_date = datetime.combine(target.date(), datetime.min.time())
        to_date = from_date + timedelta(days=1)

        for sym in MT5_SYMBOLS:
            try:
                mt5.symbol_select(sym, True)
                rates = mt5.copy_rates_range(sym, tf, from_date, to_date)
                if rates is not None and len(rates) > 0:
                    dados = []
                    for r in rates:
                        dados.append({
                            "timestamp": datetime.fromtimestamp(r[0]).isoformat(),
                            "open": float(r[1]),
                            "high": float(r[2]),
                            "low": float(r[3]),
                            "close": float(r[4]),
                            "volume": int(r[5]),
                        })
                    retornados = dados[:candles]
                    logger.info(f"[MT5] {target.date()}: {len(retornados)} candles para analise")
                    return retornados
                else:
                    logger.warning(f"[MT5] Sem dados para {target.date()}")
                    return []
            except Exception as e:
                logger.warning(f"[MT5] {sym}: {e}")
                continue
        return []

    async def _get_book_mt5(self) -> Dict:
        if not self._init_mt5():
            return self._gerar_book_simulado()

        try:
            book = mt5.market_book_get(MT5_SYMBOL)
            if book:
                bids = []
                asks = []
                for item in book:
                    if item.flags & 1:
                        bids.append({"preco": float(item.price), "volume": int(item.volume)})
                    else:
                        asks.append({"preco": float(item.price), "volume": int(item.volume)})
                return {"bids": bids[:5], "asks": asks[:5]}
        except Exception as e:
            logger.warning(f"[MT5] Book error: {e}")

        return self._gerar_book_simulado()

    def _calcular_preco_win_deterministico(self, ibov: float) -> float:
        if self._ultimo_preco > 0:
            ratio = ibov / self._ibov_base if self._ibov_base > 0 else 1.0
            diff_pct = (ratio - 1.0) * 100
            diff_pct = max(-2.0, min(2.0, diff_pct))
            novo_preco = self._ultimo_preco * (1 + (diff_pct / 1000))
            self._ultimo_preco = round(novo_preco, 0)
            return self._ultimo_preco
        return self._ibov_base

    async def _get_preco_brapi(self) -> float:
        if not REQUESTS_AVAILABLE or not self._brapi_token:
            logger.warning("[BRAPI] Token não configurado, usando fallback")
            return self._calcular_preco_win_deterministico(await self._get_ibov_atual())

        try:
            url = f"https://brapi.dev/api/quote/WIN"
            headers = {"Authorization": f"Bearer {self._brapi_token}"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    preco = data["results"][0].get("regularMarketPrice")
                    if preco and preco > 0:
                        self._preco_win_valido = True
                        self._ultimo_preco = float(preco)
                        logger.info(f"[BRAPI] WIN price: {preco}")
                        return float(preco)
        except Exception as e:
            logger.warning(f"[BRAPI] Error: {e}")

        return self._calcular_preco_win_deterministico(await self._get_ibov_atual())

    async def _buscar_brapi_win(self, timeframe: str, candles: int) -> List[dict]:
        if not REQUESTS_AVAILABLE or not self._brapi_token:
            return await self._buscar_yahoo_ibov(candles)

        try:
            url = f"https://brapi.dev/api/quote/WIN"
            params = {
                "range": "5d",
                "interval": "5m" if timeframe == "5min" else "15m",
                "fundamental": "false"
            }
            headers = {"Authorization": f"Bearer {self._brapi_token}"}
            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get("results") and len(data["results"]) > 0:
                    result = data["results"][0]
                    if "historicalDataPrice" in result:
                        hist = result["historicalDataPrice"]
                        candles_data = []
                        for item in hist[-candles:]:
                            candles_data.append({
                                "timestamp": datetime.fromtimestamp(item["date"]).isoformat(),
                                "open": float(item.get("open", 0)),
                                "high": float(item.get("high", 0)),
                                "low": float(item.get("low", 0)),
                                "close": float(item.get("close", 0)),
                                "volume": int(item.get("volume", 0)),
                            })
                        logger.info(f"[BRAPI] Got {len(candles_data)} candles WIN")
                        return candles_data
        except Exception as e:
            logger.warning(f"[BRAPI] candles error: {e}")

        return await self._buscar_yahoo_ibov(candles)

    async def _get_book_brapi(self) -> Dict:
        return self._gerar_book_simulado()

    async def _get_preco_win_profit(self) -> float:
        try:
            from infrastructure.profit_bridge import ProfitBridge
            pb = ProfitBridge()
            if pb.conectar():
                preco = pb.get_preco("WIN")
                if preco and preco > 0:
                    self._preco_win_valido = True
                    self._ultimo_preco = preco
                    return preco
        except Exception as e:
            logger.warning(f"[PROFIT] WIN price error: {e}")
        return self._calcular_preco_win_deterministico(await self._get_ibov_atual())

    async def _get_ibov_atual(self) -> float:
        if not YFINANCE_AVAILABLE:
            return self._ibov_base
        try:
            ibov = yf.Ticker("^BVSP")
            h = ibov.history(period="1d", interval="5m")
            if not h.empty:
                preco = h['Close'].iloc[-1]
                self._ibov_base = preco
                return preco
        except Exception as e:
            logger.error(f"Yahoo IBOV error: {e}")
        return self._ibov_base

    async def _buscar_profit_win(self, timeframe: str, candles: int) -> List[dict]:
        try:
            from infrastructure.profit_bridge import ProfitBridge
            pb = ProfitBridge()
            if pb.conectar():
                dados = pb.get_candles("WIN", timeframe, candles)
                if dados:
                    return dados
        except Exception as e:
            logger.warning(f"[PROFIT] WIN candles error: {e}")
        return await self._buscar_yahoo_ibov(candles)

    async def _buscar_yahoo_ibov(self, candles: int) -> List[dict]:
        if not YFINANCE_AVAILABLE:
            return self._gerar_candles_fallback(candles)

        try:
            ibov = yf.Ticker("^BVSP")
            h = ibov.history(period="5d", interval="5m")

            if h.empty:
                return self._gerar_candles_fallback(candles)

            parsed = []
            for idx, row in h.iterrows():
                parsed.append({
                    "timestamp": idx.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume']),
                })

            logger.info(f"[YAHOO] Got {len(parsed)} candles IBOV")
            return parsed[-candles:]

        except Exception as e:
            logger.error(f"Yahoo error: {e}")
            return self._gerar_candles_fallback(candles)

    def _gerar_candles_fallback(self, n: int) -> List[dict]:
        candles = []
        preco = self._ultimo_preco if self._ultimo_preco > 0 else self._ibov_base

        for i in range(n):
            variacao = (i % 5 - 2) * 30
            open_price = preco
            close_price = preco + variacao
            high_price = max(open_price, close_price) + 40
            low_price = min(open_price, close_price) - 40
            volume = 200 + (i * 10)

            base = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
            ts = base + timedelta(minutes=i * 5)

            candles.append({
                "timestamp": ts.isoformat(),
                "open": round(open_price, 0),
                "high": round(high_price, 0),
                "low": round(low_price, 0),
                "close": round(close_price, 0),
                "volume": volume,
            })
            preco = close_price

        self._ultimo_preco = preco
        return candles

    async def _get_book_profit(self) -> Dict:
        try:
            from infrastructure.profit_bridge import ProfitBridge
            pb = ProfitBridge()
            if pb.conectar():
                return pb.get_book("WIN")
        except:
            pass
        return self._gerar_book_simulado()

    def _gerar_book_simulado(self) -> Dict:
        preco = self._ultimo_preco
        bids = []
        asks = []

        for i in range(5):
            bids.append({"preco": preco - (i+1)*5, "volume": 100 + (i * 20)})
            asks.append({"preco": preco + (i+1)*5, "volume": 100 + (i * 20)})

        return {"bids": bids, "asks": asks}

    def _gerar_trades_simulados(self, n: int) -> List[dict]:
        trades = []
        preco = self._ultimo_preco

        for i in range(n):
            lado = "BID" if i % 2 == 0 else "ASK"
            volume = 50 + (i * 10)
            trades.append({
                "timestamp": datetime.now().isoformat(),
                "side": lado,
                "volume": volume,
                "preco": preco + ((i - 5) * 2)
            })

        return trades