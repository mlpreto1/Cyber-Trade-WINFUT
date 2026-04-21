# infrastructure/data_provider.py
# CYBER TRADE WIN v2.1 — Data Provider (Yahoo + Simulador)

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

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class DataProvider:
    def __init__(self, source: str = "yahoo"):
        self.source = source
        self.redis_state = None
        self._ultimo_preco = 133000.0
        self._ibov_base = 130000.0

    def set_redis(self, redis_state):
        self.redis_state = redis_state

    async def get_dados_candle(self, timeframe: str = "5min", candles: int = 20) -> List[dict]:
        if self.source == "yahoo":
            return await self._buscar_yahoo_ibov(candles)
        elif self.source == "simulador":
            return self._gerar_candles_simulado(candles)
        return self._gerar_candles_simulado(candles)

    async def get_preco_atual(self) -> float:
        if self.source == "yahoo":
            ibov = await self._get_ibov_atual()
            return self._calcular_preco_win(ibov)
        return self._gerar_preco_simulado()

    async def get_book(self) -> Dict:
        if self.source == "yahoo":
            ibov = await self._get_ibov_atual()
            preco = self._calcular_preco_win(ibov)
            return self._gerar_book_win(preco)
        return self._gerar_book_simulado()

    async def get_trades(self) -> List[dict]:
        return self._gerar_trades_simulados(10)

    def _calcular_preco_win(self, ibov: float) -> float:
        ratio = ibov / self._ibov_base
        variacao = random.uniform(-0.02, 0.02)
        preco = self._ultimo_preco * ratio * (1 + variacao)
        return round(preco, 0)

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

    async def _buscar_yahoo_ibov(self, candles: int) -> List[dict]:
        if not YFINANCE_AVAILABLE:
            return self._gerar_candles_simulado(candles)

        try:
            ibov = yf.Ticker("^BVSP")
            h = ibov.history(period="5d", interval="5m")

            if h.empty:
                return self._gerar_candles_simulado(candles)

            parsed = []
            for idx, row in h.iterrows():
                parsed.append({
                    "timestamp": idx.isoformat(),
                    "open": row['Open'],
                    "high": row['High'],
                    "low": row['Low'],
                    "close": row['Close'],
                    "volume": row['Volume'],
                })

            logger.info(f"[YAHOO] Got {len(parsed)} candles IBOV")
            return parsed[-candles:]

        except Exception as e:
            logger.error(f"Yahoo error: {e}")
            return self._gerar_candles_simulado(candles)

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

    def _gerar_book_win(self, preco: float) -> Dict:
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