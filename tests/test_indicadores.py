# tests/test_indicadores.py
# Cyber Trade WIN v3.0 — Testes para indicadores técnicos

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.indicadores import (
    calcular_ema,
    calcular_atr,
    calcular_rsi,
    calcular_macd,
    calcular_bb,
    detectar_regime,
    detectar_tendencia,
    calcular_confianca
)


def test_ema_subindo():
    precos = [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    ema9 = calcular_ema(precos, 9)
    assert ema9 > 100, f"EMA deveria ser maior que 100, got {ema9}"
    print(f"[PASS] test_ema_subindo: EMA9={ema9:.2f}")


def test_ema_descendo():
    precos = [109, 108, 107, 106, 105, 104, 103, 102, 101, 100]
    ema9 = calcular_ema(precos, 9)
    assert ema9 < 105, f"EMA deveria ser menor que 105, got {ema9}"
    print(f"[PASS] test_ema_descendo: EMA9={ema9:.2f}")


def test_ema_fallback():
    precos = [100, 101]
    ema9 = calcular_ema(precos, 9)
    assert ema9 > 0, f"EMA fallback deveria retornar média simples, got {ema9}"
    print(f"[PASS] test_ema_fallback: EMA9={ema9:.2f}")


def test_atr_positivo():
    candles = [
        {"high": 105, "low": 95, "close": 103},
        {"high": 104, "low": 96, "close": 102},
        {"high": 106, "low": 94, "close": 105},
        {"high": 107, "low": 93, "close": 106},
        {"high": 108, "low": 92, "close": 107},
    ]
    atr = calcular_atr(candles)
    assert atr > 0, f"ATR deveria ser positivo, got {atr}"
    print(f"[PASS] test_atr_positivo: ATR={atr:.2f}")


def test_atr_fallback():
    candles = [{"high": 100, "low": 95, "close": 98}]
    atr = calcular_atr(candles)
    assert atr > 0, f"ATR fallback deveria retornar valor > 0, got {atr}"
    print(f"[PASS] test_atr_fallback: ATR={atr:.2f}")


def test_rsi_faixa():
    candles = [{"high": 100, "low": 90, "close": 95 + (i % 10)} for i in range(25)]
    rsi = calcular_rsi(candles)
    assert 0 <= rsi <= 100, f"RSI deveria estar entre 0 e 100, got {rsi}"
    print(f"[PASS] test_rsi_faixa: RSI={rsi:.2f}")


def test_rsi_fallback():
    candles = [{"high": 100, "low": 90, "close": 95}]
    rsi = calcular_rsi(candles)
    assert 0 <= rsi <= 100, f"RSI fallback deveria estar entre 0 e 100, got {rsi}"
    print(f"[PASS] test_rsi_faixa: RSI={rsi:.2f}")


def test_macd():
    candles = [
        {"high": 100 + i, "low": 95 + i, "close": 98 + i}
        for i in range(50)
    ]
    macd = calcular_macd(candles)
    assert "macd" in macd, "MACD deveria ter ключ 'macd'"
    assert "sinal" in macd, "MACD deveria ter ключ 'sinal'"
    assert "histograma" in macd, "MACD deveria ter ключ 'histograma'"
    print(f"[PASS] test_macd: macd={macd['macd']:.2f}, sinal={macd['sinal']:.2f}, hist={macd['histograma']:.2f}")


def test_bb():
    candles = [
        {"high": 105, "low": 95, "close": 100 + (i % 5)}
        for i in range(25)
    ]
    bb = calcular_bb(candles)
    assert bb["superior"] > bb["medio"], "Banda superior deveria ser maior que média"
    assert bb["medio"] > bb["inferior"], "Média deveria ser maior que banda inferior"
    print(f"[PASS] test_bb: sup={bb['superior']:.2f}, mid={bb['medio']:.2f}, inf={bb['inferior']:.2f}")


def test_detectar_regime():
    candles = [
        {"high": 100 + i*2, "low": 95 + i*2, "close": 98 + i*2}
        for i in range(20)
    ]
    regime = detectar_regime(candles)
    assert regime in ["TRENDING", "RANGE", "NORMAL", "INDISPONIVEL"], f"Regime inválido: {regime}"
    print(f"[PASS] test_detectar_regime: {regime}")


def test_detectar_tendencia_alta():
    ema9, ema21 = 105, 100
    tendencia, sinal = detectar_tendencia(ema9, ema21)
    assert tendencia == "ALTA", f"Tendência deveria ser ALTA, got {tendencia}"
    assert sinal == "COMPRA", f"Sinal deveria ser COMPRA, got {sinal}"
    print(f"[PASS] test_detectar_tendencia_alta: {tendencia}/{sinal}")


def test_detectar_tendencia_baixa():
    ema9, ema21 = 95, 100
    tendencia, sinal = detectar_tendencia(ema9, ema21)
    assert tendencia == "BAIXA", f"Tendência deveria ser BAIXA, got {tendencia}"
    assert sinal == "VENDA", f"Sinal deveria ser VENDA, got {sinal}"
    print(f"[PASS] test_detectar_tendencia_baixa: {tendencia}/{sinal}")


def test_calcular_confianca():
    conf = calcular_confianca("COMPRA", ema9=105, ema21=100, rsi=50, atr=200)
    assert 0 <= conf <= 100, f"Confiança deveria estar entre 0 e 100, got {conf}"
    print(f"[PASS] test_calcular_confianca: {conf}")


def run_all_tests():
    print("\n" + "="*50)
    print("CYBER TRADE WIN v3.0 — Testes de Indicadores")
    print("="*50 + "\n")

    tests = [
        test_ema_subindo,
        test_ema_descendo,
        test_ema_fallback,
        test_atr_positivo,
        test_atr_fallback,
        test_rsi_faixa,
        test_rsi_fallback,
        test_macd,
        test_bb,
        test_detectar_regime,
        test_detectar_tendencia_alta,
        test_detectar_tendencia_baixa,
        test_calcular_confianca,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print("\n" + "="*50)
    print(f"RESULTADO: {passed} passed, {failed} failed")
    print("="*50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)