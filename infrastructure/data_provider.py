# infrastructure/data_provider.py
# Cyber Trade WIN v2.2 — Data Provider com Fontes Reais

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("data_provider")

REQUESTS_AVAILABLE = False
YFINANCE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    pass

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    pass


class DataProvider:
    def __init__(self, source: str = "yahoo"):
        self.source = source
        self.redis_state = None
        self._ultimo_preco = 130000.0
        self._ibov_base = 130000.0
        self._preco_win_valido = False
        self._brapi_token = os.getenv("BRAPI_TOKEN", "")

    def set_redis(self, redis_state):
        self.redis_state = redis_state

    async def get_dados_candle(self, timeframe: str = "5min", candles: int = 20) -> List[dict]:
        if self.source == "brapi":
            return await self._buscar_brapi_win(timeframe, candles)
        elif self.source == "profit":
            return await self._buscar_profit_win(timeframe, candles)
        elif self.source == "yahoo":
            return await self._buscar_yahoo_ibov(candles)
        return await self._buscar_yahoo_ibov(candles)

    async def get_preco_atual(self) -> float:
        if self.source == "brapi":
            return await self._get_preco_brapi()
        elif self.source == "profit":
            return await self._get_preco_win_profit()
        elif self.source == "yahoo":
            ibov = await self._get_ibov_atual()
            return self._calcular_preco_win_deterministico(ibov)
        return self._calcular_preco_win_deterministico(self._ibov_base)

    async def get_book(self) -> Dict:
        if self.source == "brapi":
            return await self._get_book_brapi()
        elif self.source == "profit":
            return await self._get_book_profit()
        return await self._gerar_book_simulado()

    async def get_trades(self) -> List[dict]:
        return self._gerar_trades_simulados(10)

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
        return await self._gerar_book_simulado()

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
        return await self._gerar_book_simulado()

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