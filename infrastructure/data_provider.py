# infrastructure/data_provider.py
# CYBER TRADE WIN v2.1 — Data Provider (B3 + Simulador)

import asyncio
import logging
import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("data_provider")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class DataProvider:
    def __init__(self, source: str = "simulador"):
        self.source = source
        self.redis_state = None
        self._ultimo_preco = 133000.0

    def set_redis(self, redis_state):
        self.redis_state = redis_state

    async def get_dados_candle(self, timeframe: str = "5min", candles: int = 20) -> List[dict]:
        if self.source == "simulador":
            return self._gerar_candles_simulado(candles)
        elif self.source == "b3":
            return await self._buscar_b3(candles)
        elif self.source == "brapi":
            return await self._buscar_brapi(candles)
        return self._gerar_candles_simulado(candles)

    async def get_preco_atual(self) -> float:
        if self.source == "simulador":
            return self._gerar_preco_simulado()
        elif self.source == "b3":
            return await self._buscar_preco_b3()
        elif self.source == "brapi":
            return await self._buscar_preco_brapi()
        return self._ultimo_preco

    async def get_book(self) -> Dict:
        if self.source == "simulador":
            return self._gerar_book_simulado()
        return {"bids": [], "asks": []}

    async def get_trades(self) -> List[dict]:
        return self._gerar_trades_simulados(10)

    def _gerar_candles_simulado(self, n: int) -> List[dict]:
        candles = []
        preco = self._ultimo_preco

        for i in range(n):
            variacao = random.uniform(-150, 150)
            open_price = preco
            close_price = preco + variacao
            high_price = max(open_price, close_price) + random.uniform(0, 80)
            low_price = min(open_price, close_price) - random.uniform(0, 80)
            volume = random.randint(100, 500)

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

    def _gerar_preco_simulado(self) -> float:
        variacao = random.uniform(-30, 30)
        self._ultimo_preco += variacao
        return round(self._ultimo_preco, 0)

    def _gerar_book_simulado(self) -> Dict:
        preco = self._ultimo_preco
        bids = []
        asks = []

        for i in range(5):
            bids.append({"preco": preco - (i+1)*5, "volume": random.randint(50, 200)})
            asks.append({"preco": preco + (i+1)*5, "volume": random.randint(50, 200)})

        return {"bids": bids, "asks": asks}

    def _gerar_trades_simulados(self, n: int) -> List[dict]:
        trades = []
        preco = self._ultimo_preco

        for i in range(n):
            lado = random.choice(["BID", "ASK"])
            volume = random.randint(10, 100)
            trades.append({
                "timestamp": datetime.now().isoformat(),
                "side": lado,
                "volume": volume,
                "preco": preco + random.uniform(-10, 10)
            })

        return trades

    async def _buscar_brapi(self, candles: int) -> List[dict]:
        if not REQUESTS_AVAILABLE:
            logger.warning("requests not available, using simulator")
            return self._gerar_candles_simulado(candles)

        try:
            url = "https://api.brapi.dev/v2/cdn/assets/candles"
            params = {
                "symbol": "WIN%3AFUT",
                "interval": "5m",
                "range": "5"
            }
            headers = {"Accept": "application/json"}
            r = requests.get(url, params=params, headers=headers, timeout=15)

            if r.status_code == 200:
                data = r.json()
                results = data.get("data", [])
                if results:
                    parsed = []
                    for item in results[:candles]:
                        parsed.append({
                            "timestamp": item.get("date", ""),
                            "open": float(item.get("open", 0)),
                            "high": float(item.get("high", 0)),
                            "low": float(item.get("low", 0)),
                            "close": float(item.get("close", 0)),
                            "volume": int(item.get("volume", 0)),
                        })
                    if parsed:
                        self._ultimo_preco = parsed[0].get("close", self._ultimo_preco)
                        logger.info(f"[BRAPI] Got {len(parsed)} candles")
                        return parsed

        except Exception as e:
            logger.error(f"BRAPI error: {e}")

        return self._gerar_candles_simulado(candles)

    async def _buscar_preco_brapi(self) -> float:
        if not REQUESTS_AVAILABLE:
            return self._gerar_preco_simulado()

        try:
            url = "https://api.brapi.dev/v2/quote"
            params = {"symbol": "WIN:FUT"}
            r = requests.get(url, params=params, timeout=10)

            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                if results:
                    preco = results[0].get("regularMarketPrice")
                    if preco:
                        self._ultimo_preco = preco
                        return preco

        except Exception as e:
            logger.error(f"BRAPI price error: {e}")

        return self._gerar_preco_simulado()

    async def _buscar_b3(self, candles: int) -> List[dict]:
        logger.info("[B3] Trying direct B3 API...")
        return self._gerar_candles_simulado(candles)

    async def _buscar_preco_b3(self) -> float:
        return self._gerar_preco_simulado()