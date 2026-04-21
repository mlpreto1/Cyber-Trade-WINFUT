# utils/capital_levels.py
# CYBER TRADE WIN v2.1

NIVEIS = [
    {"nivel":1,"nome":"INICIANTE","capital_min":1000.0,"capital_max":1999.99,"max_contratos":1,"score_minimo":72,"stop_day_pct":5.0,"stop_maximo_pts":50.0},
    {"nivel":2,"nome":"CRESCIMENTO_1","capital_min":2000.0,"capital_max":2999.99,"max_contratos":2,"score_minimo":70,"stop_day_pct":4.0,"stop_maximo_pts":80.0},
    {"nivel":3,"nome":"CRESCIMENTO_2","capital_min":3000.0,"capital_max":4999.99,"max_contratos":3,"score_minimo":68,"stop_day_pct":3.5,"stop_maximo_pts":100.0},
    {"nivel":4,"nome":"META_INICIAL","capital_min":5000.0,"capital_max":6999.99,"max_contratos":4,"score_minimo":65,"stop_day_pct":2.5,"stop_maximo_pts":120.0},
    {"nivel":5,"nome":"ESCALA_PLENA","capital_min":7000.0,"capital_max":9999.99,"max_contratos":5,"score_minimo":65,"stop_day_pct":2.5,"stop_maximo_pts":120.0},
    {"nivel":6,"nome":"MATURIDADE","capital_min":10000.0,"capital_max":999999.0,"max_contratos":5,"score_minimo":65,"stop_day_pct":2.5,"stop_maximo_pts":120.0},
]

MARCOS = [1000, 2000, 3000, 5000, 7000, 10000]


def get_nivel(capital: float) -> dict:
    for n in reversed(NIVEIS):
        if capital >= n["capital_min"]:
            return n
    return NIVEIS[0]


def proximo_marco(capital: float) -> float:
    for m in MARCOS:
        if capital < m:
            return m
    return None


def progresso(capital: float) -> dict:
    nivel = get_nivel(capital)
    proximo = proximo_marco(capital)
    if not proximo:
        return {"pct": 100.0, "faltam": 0.0}
    base = nivel["capital_min"]
    pct = (capital - base) / (proximo - base) * 100
    return {"pct": min(100.0, max(0.0, pct)), "faltam": proximo - capital}