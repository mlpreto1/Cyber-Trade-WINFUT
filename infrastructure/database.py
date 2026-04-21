# infrastructure/database.py
# CYBER TRADE WIN v3.0

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("database")


class Database:
    def __init__(self, path=r"H:\Meu Drive\Cyber Trade\Winfut\logs\cyber_trade_win.db"):
        self.path = path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                direcao TEXT,
                contratos INTEGER,
                entrada REAL,
                saida REAL,
                resultado_pts REAL,
                resultado_reais REAL,
                motivo_saida TEXT,
                score INTEGER,
                modo TEXT,
                ordem_id TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS capital_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                capital REAL,
                variacao REAL
            )
        """)
        conn.commit()
        conn.close()

    def registrar_trade(self, trade: dict):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO trades (data, direcao, contratos, entrada, saida,
                          resultado_pts, resultado_reais, motivo_saida, score, modo, ordem_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade.get("data", datetime.now().isoformat()),
            trade.get("direcao"),
            trade.get("contratos"),
            trade.get("entrada"),
            trade.get("saida"),
            trade.get("resultado_pts"),
            trade.get("resultado_reais"),
            trade.get("motivo_saida"),
            trade.get("score"),
            trade.get("modo"),
            trade.get("ordem_id"),
        ))
        conn.commit()
        conn.close()

    def get_trades_hoje(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM trades WHERE data LIKE ?", (f"{datetime.now().date()}%",))
        r = c.fetchone()
        conn.close()
        return r[0] if r else 0

    def get_resultado_hoje(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        c.execute("SELECT SUM(resultado_reais) FROM trades WHERE data LIKE ?", (f"{datetime.now().date()}%",))
        r = c.fetchone()
        conn.close()
        return r[0] if r and r[0] else 0.0