# utils/indicadores.py
# Cyber Trade WIN v3.0 — Indicadores Técnicos Reais

import pandas as pd
from typing import List, Dict

def calcular_ema(precos: List[float], periodo: int) -> float:
    """EMA exponencial real via pandas ewm"""
    if len(precos) < periodo:
        return sum(precos) / len(precos) if precos else 0
    
    series = pd.Series(precos)
    ema = series.ewm(span=periodo, adjust=False).mean().iloc[-1]
    return float(ema)


def calcular_atr(candles: List[Dict], periodo: int = 14) -> float:
    """ATR verdadeiro (True Range) - média móvel do True Range"""
    if len(candles) < periodo + 1:
        return 200.0
    
    trs = []
    for i in range(1, len(candles)):
        high = float(candles[i].get("high", 0))
        low = float(candles[i].get("low", 0))
        prev_close = float(candles[i-1].get("close", 0))
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        trs.append(tr)
    
    if len(trs) < periodo:
        return sum(trs) / len(trs) if trs else 200.0
    
    return sum(trs[-periodo:]) / periodo


def calcular_rsi(candles: List[Dict], periodo: int = 14) -> float:
    """RSI de 14 períodos ( Wilder )"""
    if len(candles) < periodo + 1:
        return 50.0
    
    closes = [float(c.get("close", 0)) for c in candles]
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    
    gains = [d for d in deltas[-periodo:] if d > 0]
    losses = [-d for d in deltas[-periodo:] if d < 0]
    
    avg_gain = sum(gains) / periodo if gains else 0.0
    avg_loss = sum(losses) / periodo if losses else 0.0
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)


def calcular_macd(candles: List[Dict], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """MACD - Moving Average Convergence Divergence"""
    if len(candles) < slow + signal:
        return {"macd": 0, "sinal": 0, "histograma": 0}
    
    closes = [float(c.get("close", 0)) for c in candles]
    series = pd.Series(closes)
    
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histograma = macd_line - signal_line
    
    return {
        "macd": float(macd_line.iloc[-1]),
        "sinal": float(signal_line.iloc[-1]),
        "histograma": float(histograma.iloc[-1])
    }


def calcular_bb(candles: List[Dict], periodo: int = 20, std_dev: float = 2.0) -> Dict:
    """Bollinger Bands"""
    if len(candles) < periodo:
        return {"superior": 0, "inferior": 0, "medio": 0}
    
    closes = [float(c.get("close", 0)) for c in candles]
    series = pd.Series(closes)
    
    media = series.rolling(window=periodo).mean().iloc[-1]
    std = series.rolling(window=periodo).std().iloc[-1]
    
    return {
        "superior": float(media + (std * std_dev)),
        "inferior": float(media - (std * std_dev)),
        "medio": float(media)
    }


def calcular_obv(candles: List[Dict]) -> float:
    """On-Balance Volume"""
    if len(candles) < 2:
        return 0.0
    
    obv = 0.0
    closes = [float(c.get("close", 0)) for c in candles]
    volumes = [float(c.get("volume", 0)) for c in candles]
    
    for i in range(1, len(candles)):
        if closes[i] > closes[i-1]:
            obv += volumes[i]
        elif closes[i] < closes[i-1]:
            obv -= volumes[i]
    
    return float(obv)


def detectar_regime(candles: List[Dict], atr_periodo: int = 14) -> str:
    """Detecta regime de mercado baseado em ATR real"""
    if len(candles) < atr_periodo + 1:
        return "INDISPONIVEL"
    
    atr = calcular_atr(candles, atr_periodo)
    closes = [float(c.get("close", 0)) for c in candles[-atr_periodo:]]
    media_preco = sum(closes) / len(closes) if closes else 1
    
    atr_pct = (atr / media_preco) * 100 if media_preco > 0 else 0
    
    if atr_pct > 1.5:
        return "TRENDING"
    elif atr_pct < 0.5:
        return "RANGE"
    else:
        return "NORMAL"


def detectar_tendencia(ema9: float, ema21: float) -> tuple:
    """Detecta tendência baseado em EMAs"""
    if ema9 > ema21 * 1.005:
        return ("ALTA", "COMPRA")
    elif ema9 < ema21 * 0.995:
        return ("BAIXA", "VENDA")
    else:
        return ("INDEFINIDA", "NEUTRO")


def calcular_confianca(sinal: str, ema9: float, ema21: float, rsi: float, atr: float) -> int:
    """Calcula confiança da análise (0-100)"""
    conf = 50
    
    if sinal == "COMPRA" or sinal == "VENDA":
        diff_ema = abs(ema9 - ema21) / ema21 * 100
        
        if diff_ema > 2.0:
            conf += 25
        elif diff_ema > 1.0:
            conf += 15
        else:
            conf += 5
        
        if 30 < rsi < 70:
            conf += 15
        
        if 100 < atr < 400:
            conf += 10
    
    return min(100, max(0, conf))