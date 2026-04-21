# tape/tape_reader.py
# CYBER TRADE WIN v3.0 — Polars Engine

import json
import logging
from typing import Dict, List

logger = logging.getLogger("tape_reader")

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None


class TapeReader:
    def __init__(self, redis_state=None):
        self.redis = redis_state
        self.metrics = {}

    def processar(self, book: dict, trades: list) -> dict:
        if not POLARS_AVAILABLE:
            return self._fallback(book, trades)

        try:
            df = pl.DataFrame(trades)
            metrics = self._calcular_metricas(df)
            self._salvar_metricas(metrics)
            return metrics
        except Exception as e:
            logger.error(f"Tape error: {e}")
            return self._fallback(book, trades)

    def _calcular_metricas(self, df) -> dict:
        if df.is_empty():
            return {"cvd_total": 0, "forca_fluxo": 50}

        cvd = df.group_by("side").sum("volume")
        bids_vol = cvd.filter(pl.col("side") == "BID")["volume"][0] if len(cvd.filter(pl.col("side") == "BID")) else 0
        asks_vol = cvd.filter(pl.col("side") == "ASK")["volume"][0] if len(cvd.filter(pl.col("side") == "ASK")) else 0

        return {
            "cvd_total": bids_vol - asks_vol,
            "forca_fluxo": 50 + ((bids_vol - asks_vol) / 100),
        }

    def _fallback(self, book, trades) -> dict:
        return {"cvd_total": 0, "forca_fluxo": 50}

    def _salvar_metricas(self, metrics: dict):
        if self.redis:
            self.redis.set("tape_metricas", json.dumps(metrics))

    def get_metricas(self) -> dict:
        if self.redis:
            v = self.redis.get("tape_metricas")
            if v:
                return json.loads(v)
        return {}