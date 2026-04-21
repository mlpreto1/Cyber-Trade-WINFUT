# CYBER TRADE WIN v2.1 — BUNDLE COMPLETO PARA DEPLOY
Mini Índice Futuro B3 (WINFUT) | Scalping 5min | Arquitetura OpenClaw Skynet
8 Agentes | Polars Engine | Capital Levels R$1K→R$10K | Cutoff Rígido 17:30
**v2.1 — Versão com bugs corrigidos** | Abril/2026

> ⚠️ AVISO LEGAL: Documento educacional. Operar contratos futuros na B3 com automação envolve
> risco de perda superior ao capital investido. Paper trading obrigatório ≥ 8 semanas.

---
## 🐛 CORREÇÕES APLICADAS v2.1
| # | Arquivo | Bug | Correção |
|---|---------|-----|----------|
| 1 | `cyber_agent.py` | Código TRUNCADO — arquivo reiniciava no meio do método | Código completo reimplementado |
| 2 | `tape_reader_polars.py` | Chave Redis `tape_metrics_win` ≠ `tape_metricas` no exec | Padronizado para `tape_metricas` em todos os módulos |
| 3 | `openclaw_win.json` | `score_pesos` somam 0.90 (faltam 10%) | Corrigido: context 0.20→0.30, total = 1.00 |
| 4 | `oracle_skill.md` | `alerta_finalizacao >= 15:45` (horário WDO, não WIN) | Corrigido para `>= 17:15` (WIN encerra 17:30) |
| 5 | `tape_reader_polars.py` | `pl.sum().filter()` inválido no Polars 0.20+ | Corrigido para `pl.when().then().otherwise().sum()` |
| 6 | `openclaw_win.json` (parte 3) | Model string `claude-sonnet-4-20250514` depreciada | Corrigido para `claude-sonnet-4-6` |
| 7 | `guard.py` | `alvo.replace(day=alvo.day + 1)` estoura em dia 31 | Corrigido para `alvo + timedelta(days=1)` |
| 8 | `CLAUDE.md` | Naming inconsistente (nomes v5.2 vs Skynet) | Padronizado para nomes Skynet v2.1 |
| 9 | `main.py` | Ciclo LEARN frágil (sleep fixo pode pular dias) | Controle via timestamp de último ciclo |
| 10 | `cost_monitor.py` | Alerta 80% nunca dispara se custo for direto a 100%+ | Lógica reordenada com flags independentes |
| 11 | `llm_router.py` | Fallback recursivo (Claude falha → chama Claude novamente) | Fallback direto para Gemma sem recursão |

---
## 📋 ÍNDICE
- [1] Diferenças Críticas WIN vs WDO
- [2] Sistema de Níveis de Capital + Projeções
- [3] Matemática do Risco com R$1.000
- [4] Instruções de Deploy
- [5] CLAUDE.md (✅ Naming Skynet corrigido)
- [6] .env.template
- [7] openclaw_win.json (✅ score_pesos e model string corrigidos)
- [8] utils/capital_levels.py
- [9] agents/exec_agent.py WIN
- [10] agents/cyber_agent.py WIN (✅ Código truncado corrigido)
- [11] utils/risk_manager.py WIN
- [12] infrastructure/llm_router.py (✅ Fallback recursivo corrigido)
- [13] infrastructure/cost_monitor.py (✅ Lógica 80%/100% corrigida)
- [14] tape/tape_reader_polars.py (✅ Chave Redis + Polars syntax corrigidos)
- [15] skills/context_skill_win.md (✅ Horário alerta corrigido para 17:15)
- [16] skills/graph_skill_win.md
- [17] skills/cyber_skill_win.md
- [18] guard.py WIN (✅ Bug de data corrigido)
- [19] main.py WIN (✅ Ciclo LEARN corrigido)
- [20] CHECKLIST_WIN.md

═══════════════════════════════════════════════════════════════
[1] DIFERENÇAS CRÍTICAS WIN vs WDO
═══════════════════════════════════════════════════════════════
| Item | WDO (Mini Dólar) | WIN (Mini Índice) |
|------|-----------------|-------------------|
| Símbolo | WDOFUT | WINFUT |
| Valor do ponto | R$5,00/pt/contrato | R$0,20/pt/contrato |
| Tick mínimo | 0,5 ponto | 5 pontos |
| Preço típico | ~5.800 pts | ~130.000–135.000 pts |
| ATR 5min típico | 5–30 pts | 200–800 pts |
| ATR diário típico | 20–80 pts | 1.500–5.000 pts |
| Driver macro | DXY / Ptax | S&P500 / IBOV / VIX / DI1F |
| Margem intraday (~) | R$200/contrato | R$80–150/contrato |
| Stop mínimo razoável | 5–15 pts | 80–300 pts |
| Horário operação | 09:15–16:00 BRT | 09:15–17:30 BRT |
| Valor ponto para sizing | R$5,00 | **R$0,20 (CRÍTICO)** |
| Ptax relevante | SIM | NÃO |
| Agente alerta cutoff | >= 15:45 | >= 17:15 (✅ corrigido) |

═══════════════════════════════════════════════════════════════
[2] SISTEMA DE NÍVEIS DE CAPITAL + PROJEÇÕES
═══════════════════════════════════════════════════════════════
NÍVEL 1 │ R$1.000 – R$1.999 │ Máx 1 contrato │ Score ≥ 72 │ Stop-day -5%   │ Est. 10-14 meses
NÍVEL 2 │ R$2.000 – R$2.999 │ Máx 2 contratos │ Score ≥ 70 │ Stop-day -4%   │ Est. 8-10 meses
NÍVEL 3 │ R$3.000 – R$4.999 │ Máx 3 contratos │ Score ≥ 68 │ Stop-day -3.5% │ Est. 5-7 meses
NÍVEL 4 │ R$5.000 – R$6.999 │ Máx 4 contratos │ Score ≥ 65 │ Stop-day -2.5% ★ META
NÍVEL 5 │ R$7.000 – R$9.999 │ Máx 5 contratos │ Score ≥ 65 │ Stop-day -2.5%
NÍVEL 6 │ R$10.000+          │ Máx 5 contratos │ Score ≥ 65 │ Stop-day -2.5% ★ MATURIDADE

Gatilho automático ao cruzar R$2K, R$3K, R$5K, R$7K, R$10K:
1. Notifica via Telegram com alerta comemorativo
2. Atualiza max_contratos no Redis
3. Ajusta score_minimo dinamicamente
4. Registra o marco no SQLite
5. Ajusta stop_day_pct adaptativo

Regra de reinvestimento: 100% dos lucros reinvestidos até R$5.000.

═══════════════════════════════════════════════════════════════
[3] MATEMÁTICA DO RISCO COM R$1.000 (HARD LOCK)
═══════════════════════════════════════════════════════════════
Premissas:
• Capital inicial: R$1.000,00
• Risco por trade: 1% = R$10,00 (sagrado)
• Valor do ponto WIN: R$0,20 por contrato
• Stop técnico típico WIN: 80–120 pts

Cálculo:
  Nível 1 — stop hard cap 50pts:
    risco_contrato = 50 × 0,20 = R$10,00 → 1 contrato ✓ (risco exato 1%)

  Stop técnico 100pts com 1 contrato:
    risco real = 100 × 0,20 = R$20,00 = 2% (viola 1%)
    → Aceitar no Nível 1 ou aumentar capital

  Para stop 100pts dentro de 1%:
    capital mínimo = R$20 / 0,01 = R$2.000 → Nível 2

═══════════════════════════════════════════════════════════════
[4] INSTRUÇÕES DE DEPLOY
═══════════════════════════════════════════════════════════════
# 1. Estrutura
mkdir cyber_trade_win && cd cyber_trade_win
mkdir -p agents infrastructure tape utils skills workspaces logs

# 2. Copiar arquivos (cada seção abaixo)

# 3. Dependências
pip install polars==0.20.10 psutil==5.9.8 redis==5.0.4 anthropic==0.28.0 \
            google-genai==0.4.0 python-dotenv==1.0.1 pydantic==2.7.0 \
            loguru==0.7.2 aiohttp==3.9.5 numpy==1.26.4

# 4. Configurar .env
cp .env.template .env
# Editar .env com suas chaves

# 5. Redis
redis-server &
redis-cli ping  # deve retornar PONG

# 6. OpenClaw
openclaw start  # Gateway localhost:3000

# 7. Iniciar (ORDEM IMPORTA)
python guard.py    # Terminal 1 — PRIMEIRO (Watchdog)
python main.py     # Terminal 2

# 8. Verificar via Telegram
/status    # → mostra Nível INICIANTE, contratos=1
/nivel     # → progresso até R$2.000
/projecao  # → estimativas de tempo

═══════════════════════════════════════════════════════════════
[5] CLAUDE.md (✅ Naming Skynet padronizado)
═══════════════════════════════════════════════════════════════
# CYBER TRADE WIN v2.1 — CLAUDE CODE PROJECT

## CONTEXTO
Sistema de trading algorítmico WINFUT (Mini Índice B3). Scalping 5min.
Horário: 09:15–17:30 BRT.
**ATENÇÃO: Valor do ponto WIN = R$0,20/contrato (≠ R$5,00 WDO)**

Stack: Python 3.11+, asyncio, Redis, SQLite, Telegram Bot
LLMs: Gemma 4 (Google AI Studio) + Claude Sonnet 4.6 (Anthropic)
Dados: ProfitDLL (Nelogica Profit Pro) via bridge Python

Capital inicial: R$1.000 | Meta: R$5.000 | Limite: 5 contratos

## ARQUITETURA — 8 AGENTES SKYNET (✅ CORRIGIDO)
| Agente | Persona | Função | Paper | Produção |
|--------|---------|--------|-------|----------|
| `architect` | ARCHITECT | Técnico 5m+15m WIN | Gemma 4 31B | Gemma 4 31B |
| `morpheus` | MORPHEUS | Tape + CVD + Iceberg | Gemma 4 31B | Gemma 4 31B |
| `oracle` | ORACLE | Macro S&P500+VIX+DI1F | Gemma 4 E4B | Gemma 4 E4B |
| `neo` | NEO | Orquestrador+Decisão | Gemma 4 31B | Claude Sonnet 4.6 |
| `terminator` | TERMINATOR | Execução de ordens | Python puro | Python puro |
| `sentinel` | SENTINEL | Watchdog+Heartbeat | Python puro | Python puro |
| `cyberdyne` | CYBERDYNE | Evolutivo+LEARN | Gemma 4 26B | Claude Sonnet 4.6 |
| `reaper` | REAPER | Monitor de custos | Python puro | Python puro |

## FLUXO POR CANDLE (5min)
FASE 1: Pré-filtro local (ATR_WIN, horário, cool-down, stop-day, nível capital)
FASE 2: ProfitDLL → candles WIN, book, tape
FASE 3: asyncio.gather → ARCHITECT + MORPHEUS + ORACLE em paralelo (~3-4s)
FASE 4: NEO → 7 passos → CANCELAR | AGUARDAR | ARMAR
FASE 5: Se ARMAR → TERMINATOR monitora gatilho via tape_reader
FASE 6: Gatilho → ordem → gestão (break-even + trailing ATR_WIN)
FASE 7: SENTINEL verifica capital level após cada trade fechado

## GESTÃO DE RISCO WIN
Valor ponto WIN   : R$0,20/pt/contrato (IMUTÁVEL)
Risco por trade   : 1,0% do capital (NUNCA alterável)
Stop-day          : adaptativo por nível (NUNCA alterável)
Max contratos     : 5 hard cap | aumenta por nível
Max trades/dia    : 5
Cool-down         : 3 losses → 30min pausa
Stop > 2×ATR_WIN  : NUNCA (exceto Nível 1 hard cap 50pts)
R:R < 1,5         : NUNCA autorizar
ATR mínimo WIN    : 200 pts (mercado morto = não operar)
Cutoff WIN        : 17:30 BRT (FECHAMENTO ABSOLUTO)

## CÁLCULO RESULTADO WIN
```python
resultado_pts   = preco_saida - preco_entrada
resultado_reais = resultado_pts * 0.20 * contratos
# +200pts × 0.20 × 1 contrato = +R$40,00
# -150pts × 0.20 × 2 contratos = -R$60,00
```

═══════════════════════════════════════════════════════════════
[6] .env.template
═══════════════════════════════════════════════════════════════
# CYBER TRADE WIN v2.1 — ENVIRONMENT
# ⚠️ NUNCA versionar. PAPER_MODE=true até validação completa.

ANTHROPIC_API_KEY=sk-ant-api03-SUBSTITUA_AQUI
GOOGLE_AI_API_KEY=AI_SUBSTITUA_AQUI
TELEGRAM_BOT_TOKEN=123456789:AAH_SUBSTITUA_AQUI
TELEGRAM_CHAT_ID=-1001234567890

PAPER_MODE=true
DAILY_API_BUDGET_USD=0.10
COST_ALERT_THRESHOLD_PCT=80
COST_LOG_PATH=./logs/cost_today.json

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

DB_PATH=./cyber_trade_win.db
MEMORY_DB_PATH=./learn_memory_win.db
OPENCLAW_JSON_PATH=./openclaw_win.json

# WIN — valores críticos
CAPITAL_INICIAL=1000.00
VALOR_PONTO_WIN=0.20
PRECO_BASE_SIMULADO=132500.0
RISCO_POR_TRADE_PCT=1.0
STOP_DAY_PCT=5.0
MAX_OPERACOES_DIA=5
ATR_MINIMO=200.0
MAX_CONTRATOS_NORMAL=1
SNIPER_SCORE_MIN=80
SNIPER_MAX_CONTRATOS=2
SNIPER_SLIPPAGE_MAX=10.0
SCORE_MIN_NORMAL=72
SLIPPAGE_MAX_PTS=10.0
RR_MINIMO=1.5
LATENCIA_MAX_S=5.0
DESLOCAMENTO_MAX_PTS=50.0
BREAKEVEN_PTS=60.0
TRAILING_FLOOR_PTS=80.0
TRAILING_ATR_MIN=3
COOL_DOWN_LOSSES=3
COOL_DOWN_MINUTOS=30
LOG_LEVEL=INFO

═══════════════════════════════════════════════════════════════
[7] openclaw_win.json (✅ score_pesos e model string corrigidos)
═══════════════════════════════════════════════════════════════
```json
{
  "version": "WIN-2.1",
  "description": "Cyber Trade WIN v2.1 — Mini Índice Futuro B3 | Skynet 8 Agentes | Cutoff 17:30",
  "gateway": "localhost:3000",
  "contrato": "WINFUT",
  "valor_ponto": 0.20,
  "tick_minimo": 5,

  "llm_routing": {
    "paper_mode_env": "PAPER_MODE",
    "modelos": {
      "paper": {
        "architect": "gemma-4-31b-it",
        "morpheus":  "gemma-4-31b-it",
        "oracle":    "gemma-4-e4b-it",
        "neo":       "gemma-4-31b-it",
        "cyberdyne": "gemma-4-31b-it"
      },
      "producao": {
        "architect": "gemma-4-31b-it",
        "morpheus":  "gemma-4-31b-it",
        "oracle":    "gemma-4-e4b-it",
        "neo":       "claude-sonnet-4-6",
        "cyberdyne": "claude-sonnet-4-6"
      }
    }
  },

  "cost_monitor": {
    "orcamento_diario_usd_paper": 0.10,
    "orcamento_diario_usd_producao": 2.00,
    "alert_threshold_pct": 80,
    "throttle_agentes_secundarios": ["architect", "morpheus", "oracle"],
    "custo_maximo_por_chamada_usd": 0.50
  },

  "capital_levels": {
    "reinvestir_ate": 5000.0,
    "niveis": [
      {"nivel":1,"nome":"INICIANTE","emoji":"🌱","capital_min":1000.0,"capital_max":1999.99,"max_contratos":1,"max_contratos_sniper":1,"score_minimo":72,"score_sniper":85,"stop_day_pct":5.0,"stop_maximo_pts":50.0,"breakeven_pts":60.0,"trailing_floor_pts":80.0,"projecao_dias_base":260,"projecao_dias_otimista":180,"projecao_dias_conservador":420},
      {"nivel":2,"nome":"CRESCIMENTO_1","emoji":"📈","capital_min":2000.0,"capital_max":2999.99,"max_contratos":2,"max_contratos_sniper":1,"score_minimo":70,"score_sniper":83,"stop_day_pct":4.0,"stop_maximo_pts":80.0,"breakeven_pts":70.0,"trailing_floor_pts":90.0,"projecao_dias_base":200,"projecao_dias_otimista":120,"projecao_dias_conservador":300},
      {"nivel":3,"nome":"CRESCIMENTO_2","emoji":"🚀","capital_min":3000.0,"capital_max":4999.99,"max_contratos":3,"max_contratos_sniper":2,"score_minimo":68,"score_sniper":81,"stop_day_pct":3.5,"stop_maximo_pts":100.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":140,"projecao_dias_otimista":90,"projecao_dias_conservador":210},
      {"nivel":4,"nome":"META_INICIAL","emoji":"💰","capital_min":5000.0,"capital_max":6999.99,"max_contratos":4,"max_contratos_sniper":2,"score_minimo":65,"score_sniper":80,"stop_day_pct":2.5,"stop_maximo_pts":120.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":105,"projecao_dias_otimista":70,"projecao_dias_conservador":150},
      {"nivel":5,"nome":"ESCALA_PLENA","emoji":"🏆","capital_min":7000.0,"capital_max":9999.99,"max_contratos":5,"max_contratos_sniper":3,"score_minimo":65,"score_sniper":80,"stop_day_pct":2.5,"stop_maximo_pts":120.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":95,"projecao_dias_otimista":60,"projecao_dias_conservador":140},
      {"nivel":6,"nome":"MATURIDADE","emoji":"⭐","capital_min":10000.0,"capital_max":999999.0,"max_contratos":5,"max_contratos_sniper":3,"score_minimo":65,"score_sniper":80,"stop_day_pct":2.5,"stop_maximo_pts":120.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":null,"projecao_dias_otimista":null,"projecao_dias_conservador":null}
    ],
    "marcos_telegram": [1000, 2000, 3000, 5000, 7000, 10000]
  },

  "risk": {
    "risco_por_trade_pct": 1.0,
    "max_operacoes_dia": 5,
    "max_contratos_absoluto": 5,
    "rr_minimo": 1.5,
    "score_premium": 85,
    "atr_minimo_win": 200.0,
    "slippage_maximo_pts": 10.0,
    "cool_down_losses": 3,
    "cool_down_minutos": 30,
    "equity_filter_hard_pct": -3.0,
    "equity_filter_soft_pct": -1.5,
    "latencia_max_segundos": 5.0,
    "deslocamento_max_pts": 50.0,
    "valor_ponto": 0.20,
    "breakeven_pts": 60.0,
    "trailing_floor_pts": 80.0
  },

  "sniper_mode": {
    "ativo": false,
    "redis_key": "sniper_mode",
    "telegram_toggle": "SNIPER ON / SNIPER OFF",
    "parametros": {
      "score_minimo": 80,
      "held_vol_base": 500,
      "iceberg_multiplo": 4.0,
      "breakeven_pts": 60.0,
      "trailing_atr_minutos": 2,
      "slippage_maximo_pts": 8.0
    }
  },

  "tape_reader": {
    "versao": "4.3-WIN",
    "held_prints_min": 2,
    "held_vol_base": 200,
    "iceberg_multiplo": 3.0,
    "iceberg_janela_ms": 60000,
    "spoof_vol_min": 100,
    "spoof_ms_max": 2000,
    "sweep_niveis_min": 3,
    "sweep_ms_max": 3000,
    "cvd_limiar_divergencia": 200
  },

  "horarios": {
    "inicio": "09:15",
    "fim": "17:55",
    "operacao_fim": "17:30",
    "proibidos": [
      {"nome": "Abertura",       "inicio": "09:00", "fim": "09:15"},
      {"nome": "Almoco",         "inicio": "12:00", "fim": "13:30"},
      {"nome": "Pre_fechamento", "inicio": "17:30", "fim": "17:55"}
    ]
  },

  "sessoes": {
    "ABERTURA":      {"inicio": "09:00", "fim": "09:15", "qualidade": "PROIBIDO",   "fator": 0.0},
    "MANHA_INICIAL": {"inicio": "09:15", "fim": "10:30", "qualidade": "MODERADA",   "fator": 0.85},
    "NY_TRANSICAO":  {"inicio": "10:30", "fim": "10:48", "qualidade": "CAUTELA",    "fator": 0.75},
    "MANHA_ATIVA":   {"inicio": "10:48", "fim": "12:00", "qualidade": "EXCELENTE",  "fator": 1.00},
    "ALMOCO":        {"inicio": "12:00", "fim": "13:30", "qualidade": "PROIBIDO",   "fator": 0.0},
    "TARDE_INICIAL": {"inicio": "13:30", "fim": "14:15", "qualidade": "MODERADA",   "fator": 0.80},
    "TARDE_ATIVA":   {"inicio": "14:15", "fim": "16:30", "qualidade": "BOA",        "fator": 0.90},
    "TARDE_FINAL":   {"inicio": "16:30", "fim": "17:15", "qualidade": "MODERADA",   "fator": 0.60},
    "ENCERRANDO":    {"inicio": "17:15", "fim": "17:30", "qualidade": "PROIBIDO",   "fator": 0.0},
    "PRE_FECHAMENTO":{"inicio": "17:30", "fim": "17:55", "qualidade": "PROIBIDO",   "fator": 0.0}
  },

  "score_pesos": {
    "graph":   0.35,
    "flow":    0.30,
    "context": 0.30,
    "timing":  0.05
  },

  "score_ajustes": {
    "iceberg_detectado":         10,
    "held_confirmacao_dupla":     7,
    "absorcao":                   5,
    "delta_candle_alto":          5,
    "sweep_massivo":              5,
    "sp500_alinhado":             5,
    "ibov_alinhado":              5,
    "rompimento_fraco":          -5,
    "divergencia_delta_preco":  -10,
    "volume_relativo_baixo":    -10,
    "divergencia_win_sp500":    -10,
    "desalinhamento_timeframes":-10,
    "sp500_contra":             -10,
    "vix_alto":                 -10,
    "spoof_detectado":          -15
  },

  "learn_changes": []
}
```

═══════════════════════════════════════════════════════════════
[8] utils/capital_levels.py
═══════════════════════════════════════════════════════════════
```python
# utils/capital_levels.py
# CYBER TRADE WIN v2.1

import json
import logging
import os
from typing import Optional

logger = logging.getLogger("capital_levels")

NIVEIS = [
    {"nivel":1,"nome":"INICIANTE","emoji":"🌱","capital_min":1000.0,"capital_max":1999.99,"max_contratos":1,"max_contratos_sniper":1,"score_minimo":72,"score_sniper":85,"stop_day_pct":5.0,"stop_maximo_pts":50.0,"breakeven_pts":60.0,"trailing_floor_pts":80.0,"projecao_dias_base":260,"projecao_dias_otimista":180,"projecao_dias_conservador":420,"nota":"Ultra-conservador. 1 contrato fixo. Stop máx 50pts."},
    {"nivel":2,"nome":"CRESCIMENTO_1","emoji":"📈","capital_min":2000.0,"capital_max":2999.99,"max_contratos":2,"max_contratos_sniper":1,"score_minimo":70,"score_sniper":83,"stop_day_pct":4.0,"stop_maximo_pts":80.0,"breakeven_pts":70.0,"trailing_floor_pts":90.0,"projecao_dias_base":200,"projecao_dias_otimista":120,"projecao_dias_conservador":300,"nota":"Primeiro upgrade. Stop até 80pts."},
    {"nivel":3,"nome":"CRESCIMENTO_2","emoji":"🚀","capital_min":3000.0,"capital_max":4999.99,"max_contratos":3,"max_contratos_sniper":2,"score_minimo":68,"score_sniper":81,"stop_day_pct":3.5,"stop_maximo_pts":100.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":140,"projecao_dias_otimista":90,"projecao_dias_conservador":210,"nota":"Stops técnicos adequados."},
    {"nivel":4,"nome":"META_INICIAL","emoji":"💰","capital_min":5000.0,"capital_max":6999.99,"max_contratos":4,"max_contratos_sniper":2,"score_minimo":65,"score_sniper":80,"stop_day_pct":2.5,"stop_maximo_pts":120.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":105,"projecao_dias_otimista":70,"projecao_dias_conservador":150,"nota":"META R$5.000 ATINGIDA!"},
    {"nivel":5,"nome":"ESCALA_PLENA","emoji":"🏆","capital_min":7000.0,"capital_max":9999.99,"max_contratos":5,"max_contratos_sniper":3,"score_minimo":65,"score_sniper":80,"stop_day_pct":2.5,"stop_maximo_pts":120.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":95,"projecao_dias_otimista":60,"projecao_dias_conservador":140,"nota":"Escala máxima. 5 contratos disponíveis."},
    {"nivel":6,"nome":"MATURIDADE","emoji":"⭐","capital_min":10000.0,"capital_max":float("inf"),"max_contratos":5,"max_contratos_sniper":3,"score_minimo":65,"score_sniper":80,"stop_day_pct":2.5,"stop_maximo_pts":120.0,"breakeven_pts":80.0,"trailing_floor_pts":100.0,"projecao_dias_base":None,"projecao_dias_otimista":None,"projecao_dias_conservador":None,"nota":"R$10.000 conquistados."},
]

MARCOS_TELEGRAM = [1000, 2000, 3000, 5000, 7000, 10000]


def get_nivel(capital: float) -> dict:
    for n in reversed(NIVEIS):
        if capital >= n["capital_min"]:
            return n
    return NIVEIS[0]


def proximo_marco(capital: float) -> Optional[float]:
    for marco in MARCOS_TELEGRAM:
        if capital < marco:
            return float(marco)
    return None


def progresso_para_proximo_marco(capital: float) -> dict:
    nivel_atual = get_nivel(capital)
    proximo = proximo_marco(capital)
    if proximo is None:
        return {"pct": 100.0, "faltam": 0.0, "proximo": None}
    base = nivel_atual["capital_min"]
    pct = (capital - base) / (proximo - base) * 100
    return {
        "pct": round(min(100.0, max(0.0, pct)), 1),
        "faltam": round(proximo - capital, 2),
        "proximo": proximo,
    }


def projecao_tempo(nivel_num: int, capital: float) -> dict:
    nivel = get_nivel(capital)
    if nivel["nivel"] >= 6:
        return {"base_dias": None, "otimista_dias": None, "conservador_dias": None,
                "base_meses": None, "otimista_meses": None, "conservador_meses": None}
    return {
        "base_dias": nivel["projecao_dias_base"],
        "otimista_dias": nivel["projecao_dias_otimista"],
        "conservador_dias": nivel["projecao_dias_conservador"],
        "base_meses": round(nivel["projecao_dias_base"] / 22) if nivel["projecao_dias_base"] else None,
        "otimista_meses": round(nivel["projecao_dias_otimista"] / 22) if nivel["projecao_dias_otimista"] else None,
        "conservador_meses": round(nivel["projecao_dias_conservador"] / 22) if nivel["projecao_dias_conservador"] else None,
    }


class CapitalLevelManager:
    def __init__(self, redis_state, tg, db):
        self.redis = redis_state
        self.tg = tg
        self.db = db

    def _nivel_salvo(self) -> int:
        try:
            v = self.redis.get("nivel_capital_atual")
            return int(v) if v else 0
        except Exception:
            return 0

    def _salvar_nivel(self, nivel: int):
        self.redis.set("nivel_capital_atual", str(nivel))

    def aplicar_nivel_ao_redis(self, nivel_dict: dict):
        sniper = str(self.redis.get("sniper_mode") or "false").lower() == "true"
        max_c = nivel_dict["max_contratos_sniper"] if sniper else nivel_dict["max_contratos"]
        self.redis.set("max_contratos_nivel",   str(nivel_dict["max_contratos"]))
        self.redis.set("max_contratos_efetivo", str(max_c))
        self.redis.set("score_minimo_nivel",    str(nivel_dict["score_minimo"]))
        self.redis.set("score_sniper_nivel",    str(nivel_dict["score_sniper"]))
        self.redis.set("stop_day_pct_nivel",    str(nivel_dict["stop_day_pct"]))
        self.redis.set("stop_maximo_pts_nivel", str(nivel_dict.get("stop_maximo_pts", 120.0)))
        self.redis.set("breakeven_pts_nivel",   str(nivel_dict.get("breakeven_pts", 80.0)))
        self.redis.set("trailing_floor_nivel",  str(nivel_dict.get("trailing_floor_pts", 100.0)))
        self.redis.set("nome_nivel_capital",    nivel_dict["nome"])

    async def verificar_nivel(self):
        capital = self.redis.get_capital()
        if capital is None:
            capital = float(os.getenv("CAPITAL_INICIAL", "1000"))
        nivel_atual = get_nivel(capital)
        nivel_salvo = self._nivel_salvo()
        self.aplicar_nivel_ao_redis(nivel_atual)
        if nivel_atual["nivel"] != nivel_salvo:
            subiu = nivel_atual["nivel"] > nivel_salvo
            self._salvar_nivel(nivel_atual["nivel"])
            await self._alertar_transicao(capital, nivel_atual, subiu)
        await self._checar_marcos(capital)

    async def _alertar_transicao(self, capital: float, nivel: dict, subiu: bool):
        prog = progresso_para_proximo_marco(capital)
        proj = projecao_tempo(nivel["nivel"], capital)
        if subiu:
            msg = (
                f"{nivel['emoji']} NOVO NÍVEL! Nível {nivel['nivel']}: {nivel['nome']}\n"
                f"Capital: R${capital:,.2f}\n"
                f"✅ Max contratos: {nivel['max_contratos']}\n"
                f"✅ Score mínimo: {nivel['score_minimo']}\n"
                f"✅ Stop-day: {nivel['stop_day_pct']:.1f}%\n"
                f"✅ Stop máx: {nivel.get('stop_maximo_pts', 120):.0f}pts\n"
                f"📊 {nivel['nota']}\n"
            )
            if prog["proximo"]:
                msg += f"🎯 Próximo: R${prog['proximo']:,.0f} (faltam R${prog['faltam']:,.2f})\n"
                if proj["base_meses"]:
                    msg += f"⏱️ Est: {proj['base_meses']}m base | {proj['otimista_meses']}m otimista"
        else:
            msg = (
                f"⚠️ CAPITAL CAIU DE NÍVEL\n"
                f"Nível {nivel['nivel']}: {nivel['nome']} | Capital: R${capital:,.2f}\n"
                f"Contratos: {nivel['max_contratos']} | Stop-day: {nivel['stop_day_pct']:.1f}%\n"
                f"💡 Mantenha disciplina."
            )
        logger.info(f"[CAPITAL_LEVELS] → {nivel['nome']}")
        if self.tg:
            self.tg.alertar(msg)

    async def _checar_marcos(self, capital: float):
        marcos_str = self.redis.get("marcos_capital_atingidos") or "[]"
        try:
            atingidos = json.loads(marcos_str)
        except Exception:
            atingidos = []
        for marco in MARCOS_TELEGRAM:
            if capital >= marco and marco not in atingidos:
                atingidos.append(marco)
                self.redis.set("marcos_capital_atingidos", json.dumps(atingidos))
                if marco == 5000:
                    msg = (
                        f"🎉🎉🎉 META R$5.000 ATINGIDA! 🎉🎉🎉\n"
                        f"Capital: R${capital:,.2f}\n"
                        f"Você quintuplicou! Max contratos: 4 | Stop-day: 2.5%"
                    )
                elif marco == 10000:
                    msg = f"⭐ R$10.000 CONQUISTADOS! Capital: R${capital:,.2f}"
                else:
                    msg = f"✨ Marco R${marco:,} atingido! Capital: R${capital:,.2f}"
                logger.info(f"[CAPITAL_LEVELS] Marco R${marco:,}!")
                if self.tg:
                    self.tg.alertar(msg)

    def relatorio_capital(self, capital: float) -> str:
        nivel = get_nivel(capital)
        prog = progresso_para_proximo_marco(capital)
        proj = projecao_tempo(nivel["nivel"], capital)
        capital_ini = float(os.getenv("CAPITAL_INICIAL", "1000"))
        ganho = capital - capital_ini
        pct = ganho / capital_ini * 100
        barra_n = int(prog["pct"] / 5)
        barra = "█" * barra_n + "░" * (20 - barra_n)
        msg = (
            f"{nivel['emoji']} NÍVEL {nivel['nivel']}: {nivel['nome']}\n"
            f"Capital:  R${capital:>10,.2f}\n"
            f"Ganho:    R${ganho:>+10,.2f} ({pct:+.1f}%)\n"
            f"Contratos: {nivel['max_contratos']} (Sniper: {nivel['max_contratos_sniper']})\n"
            f"Score mín: {nivel['score_minimo']} | Stop-day: {nivel['stop_day_pct']:.1f}%\n"
        )
        if prog["proximo"]:
            msg += (
                f"Próximo: R${prog['proximo']:,.0f} — faltam R${prog['faltam']:,.2f}\n"
                f"[{barra}] {prog['pct']:.0f}%\n"
            )
            if proj["base_meses"]:
                msg += (
                    f"⏱️ Est: {proj['base_meses']}m base | "
                    f"{proj['otimista_meses']}m otimista | "
                    f"{proj['conservador_meses']}m conservador"
                )
        else:
            msg += "✅ Todos os marcos atingidos! Modo máximo ativo."
        return msg
```

═══════════════════════════════════════════════════════════════
[9] agents/exec_agent.py WIN
═══════════════════════════════════════════════════════════════
```python
# agents/exec_agent.py
# CYBER TRADE WIN v2.1
# VALOR_PONTO_WIN = R$0,20 por contrato (CRÍTICO — não é R$5,00)

import asyncio, json, logging, os, uuid
from datetime import datetime, time as dtime, timezone

logger = logging.getLogger("exec_agent_win")

PAPER_MODE      = os.getenv("PAPER_MODE", "true").lower() == "true"
VALOR_PONTO_WIN = float(os.getenv("VALOR_PONTO_WIN", "0.20"))
HORARIO_FECHAR  = dtime(17, 30)
SLIPPAGE_MAX    = float(os.getenv("SLIPPAGE_MAX_PTS", "10.0"))


class ExecAgent:

    def __init__(self, redis_state, db, tg, profit_bridge=None):
        self.redis   = redis_state
        self.db      = db
        self.tg      = tg
        self.profit  = profit_bridge
        self._posicao    = None
        self._loop_ativo = False

    async def armar(self, cyber_output: dict):
        if not self._validar_json_cyber(cyber_output):
            return

        max_c_nivel = int(self.redis.get("max_contratos_efetivo") or 1)
        contratos_prop = cyber_output.get("contratos", 1)
        contratos = min(contratos_prop, max_c_nivel)

        breakeven_pts  = float(self.redis.get("breakeven_pts_nivel")  or os.getenv("BREAKEVEN_PTS", "60.0"))
        trailing_floor = float(self.redis.get("trailing_floor_nivel") or os.getenv("TRAILING_FLOOR_PTS", "80.0"))

        estado = {
            "decisao":        cyber_output["decisao"],
            "direcao":        cyber_output["direcao"],
            "contratos":      contratos,
            "entrada":        cyber_output["entrada_zona"],
            "stop":           cyber_output["stop"],
            "alvo1":          cyber_output["alvo1"],
            "alvo2":          cyber_output["alvo2"],
            "rr_alvo1":       cyber_output["rr_alvo1"],
            "gatilho":        cyber_output["gatilho"],
            "risco_reais":    cyber_output["risco_financeiro_reais"],
            "score":          cyber_output["score_final"],
            "status":         "ARMADO",
            "armado_em":      datetime.now(timezone.utc).isoformat(),
            "breakeven_pts":  breakeven_pts,
            "trailing_floor": trailing_floor,
        }

        self.redis.set("posicao_aberta", json.dumps(estado))
        stop_pts   = abs(estado["entrada"] - estado["stop"])
        risco_real = stop_pts * VALOR_PONTO_WIN * contratos
        score      = cyber_output["score_final"]
        classi     = cyber_output.get("setup_classificacao", "PADRÃO")

        self.tg.alertar(
            f"🎯 {'PREMIUM' if classi == 'PREMIUM' else 'SETUP'} ARMADO WIN [Score {score}]\n"
            f"  {estado['direcao']} | {contratos}x | Entrada: {estado['entrada']:,.0f}\n"
            f"  Stop: {estado['stop']:,.0f} ({stop_pts:.0f}pts) | Alvo1: {estado['alvo1']:,.0f} | R:R {estado['rr_alvo1']:.2f}\n"
            f"  Risco: R${risco_real:.2f} | Gatilho: {estado['gatilho']['tipo']} | "
            f"Validade: {estado['gatilho']['validade_segundos']}s"
        )

        if not self._loop_ativo:
            self._loop_ativo = True
            asyncio.create_task(self._loop_gatilho(estado))

    async def _loop_gatilho(self, estado: dict):
        from datetime import datetime as dt, timezone as tz
        validade_str = estado["gatilho"].get("validade_expira_em")
        try:
            while True:
                agora = dt.now(tz.utc)
                if validade_str:
                    validade = dt.fromisoformat(validade_str)
                    if agora >= validade:
                        self.tg.alertar(f"⏱️ Gatilho WIN expirado: {estado['gatilho']['tipo']}")
                        self._desarmar(); return
                if agora.astimezone().time() >= HORARIO_FECHAR:
                    self._desarmar(); return
                if self._gatilho_ativado(estado):
                    await self._executar_entrada(estado); return
                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"Loop gatilho WIN: {e}")
            self._desarmar()
        finally:
            self._loop_ativo = False

    def _gatilho_ativado(self, estado: dict) -> bool:
        tipo    = estado["gatilho"]["tipo"]
        preco   = self._preco_atual()
        if preco is None: return False
        entrada = estado["entrada"]
        direcao = estado["direcao"]
        try:
            # ✅ Chave Redis padronizada: tape_metricas
            tape = json.loads(self.redis.get("tape_metricas") or "{}")
        except Exception:
            tape = {}
        delta   = tape.get("cvd_total", 0)
        burst   = tape.get("burst_detectado", False)
        held    = tape.get("held_bid_detectado" if direcao == "COMPRA" else "held_offer_detectado", False)
        prints  = tape.get("held_bid_prints_confirmadores" if direcao == "COMPRA" else "held_offer_prints_confirmadores", 0)

        if tipo == "ROMPIMENTO":
            trigger = entrada + 5 if direcao == "COMPRA" else entrada - 5
            cond = preco >= trigger if direcao == "COMPRA" else preco <= trigger
            return cond and abs(delta) > 100 and burst
        elif tipo == "PULLBACK_ABSORÇÃO":
            return abs(preco - entrada) <= 10 and held and prints >= 2
        elif tipo == "CONTINUAÇÃO":
            return abs(delta) >= 80 and abs(preco - entrada) <= 15
        elif tipo == "SWEEP_MOMENTUM":
            return tape.get("sweep_detectado", False) and abs(preco - entrada) <= 20
        elif tipo == "ICEBERG_PREMIUM":
            return tape.get("iceberg_detectado", False) and abs(preco - entrada) <= 10
        return False

    async def _executar_entrada(self, estado: dict):
        preco_market = self._preco_atual()
        if preco_market is None:
            self.tg.alertar("❌ EXEC WIN: preço indisponível — abortado")
            self._desarmar(); return

        slippage  = abs(preco_market - estado["entrada"])
        contratos = estado["contratos"]

        if slippage > SLIPPAGE_MAX:
            self.tg.alertar(f"❌ Slippage WIN {slippage:.0f}pts > {SLIPPAGE_MAX:.0f}pts — abortado")
            self._desarmar(); return
        elif slippage > SLIPPAGE_MAX / 2:
            contratos = max(1, contratos // 2)
            self.tg.alertar(f"⚠️ Slippage parcial WIN {slippage:.0f}pts → {contratos} contrato(s)")

        if PAPER_MODE:
            ordem_id = f"PAPER_WIN_{uuid.uuid4().hex[:8].upper()}"
            preco_real = estado["entrada"]
        else:
            if self.profit:
                try:
                    ordem_id = self.profit.enviar_ordem_mercado(estado["direcao"], contratos)
                    preco_real = preco_market
                except Exception as e:
                    self.tg.alertar(f"🚨 Corretora rejeitou WIN: {e}")
                    self._desarmar(); return
            else:
                self.tg.alertar("🚨 ProfitDLL WIN não conectada — abortado")
                self._desarmar(); return

        posicao = {**estado,
            "status": "ABERTA", "ordem_id": ordem_id,
            "entrada_real": preco_real, "contratos_real": contratos,
            "stop_atual": estado["stop"], "breakeven_ativo": False,
            "trailing_ativo": False, "parcial_exec": False,
            "aberta_em": datetime.now(timezone.utc).isoformat(),
        }
        self._posicao = posicao
        self.redis.set("posicao_aberta", json.dumps(posicao))
        self.redis.incr("trades_dia")

        risco_r = abs(preco_real - posicao["stop"]) * VALOR_PONTO_WIN * contratos
        self.tg.alertar(
            f"✅ ORDEM WIN {'(PAPER)' if PAPER_MODE else '(REAL)'}\n"
            f"  {posicao['direcao']} {contratos}x @ {preco_real:,.0f}\n"
            f"  Stop: {posicao['stop']:,.0f} | Alvo1: {posicao['alvo1']:,.0f} | Risco: R${risco_r:.2f}"
        )
        asyncio.create_task(self._loop_posicao(posicao))

    async def _loop_posicao(self, posicao: dict):
        maximo_r = minimo_r = posicao["entrada_real"]
        breakeven_pts  = posicao.get("breakeven_pts", 60.0)
        trailing_floor = posicao.get("trailing_floor", 80.0)
        try:
            while True:
                if datetime.now().time() >= HORARIO_FECHAR:
                    await self._fechar_posicao(posicao, "ENCERRAMENTO_17H30"); return
                preco = self._preco_atual()
                if preco is None:
                    await asyncio.sleep(10); continue
                direcao = posicao["direcao"]
                entrada = posicao["entrada_real"]
                if direcao == "COMPRA":
                    maximo_r = max(maximo_r, preco)
                else:
                    minimo_r = min(minimo_r, preco)
                lucro_pts = (preco - entrada) if direcao == "COMPRA" else (entrada - preco)

                # Stop
                stop_ok = preco <= posicao["stop_atual"] if direcao == "COMPRA" else preco >= posicao["stop_atual"]
                if stop_ok:
                    self.redis.incr("violinada_pendente")
                    await self._fechar_posicao(posicao, "STOP"); return

                # Fluxo contrário
                try:
                    tape = json.loads(self.redis.get("tape_metricas") or "{}")
                    if tape.get("divergencia_cvd_preco", False):
                        await self._fechar_posicao(posicao, "FLUXO_CONTRARIO"); return
                except Exception:
                    pass

                # Break-even
                if not posicao["breakeven_ativo"] and lucro_pts >= breakeven_pts:
                    novo_stop = entrada + 5 if direcao == "COMPRA" else entrada - 5
                    posicao["stop_atual"] = novo_stop
                    posicao["breakeven_ativo"] = True
                    self.redis.set("posicao_aberta", json.dumps(posicao))
                    self.redis.incr("breakeven_ativado_n")
                    self.tg.alertar(f"✅ Break-even WIN → stop: {novo_stop:,.0f} (+{lucro_pts:.0f}pts)")

                # Trailing ATR
                if posicao["breakeven_ativo"]:
                    if not posicao["trailing_ativo"]:
                        posicao["trailing_ativo"] = True
                        self.redis.incr("trailing_ativado_n")
                    atr = self._atr_recente()
                    trail_dist = max(1.5 * atr, trailing_floor)
                    if direcao == "COMPRA":
                        novo_stop = maximo_r - trail_dist
                        if novo_stop > posicao["stop_atual"]:
                            posicao["stop_atual"] = novo_stop
                            self.redis.set("posicao_aberta", json.dumps(posicao))
                    else:
                        novo_stop = minimo_r + trail_dist
                        if novo_stop < posicao["stop_atual"]:
                            posicao["stop_atual"] = novo_stop
                            self.redis.set("posicao_aberta", json.dumps(posicao))

                # Alvos
                if not posicao["trailing_ativo"]:
                    alvo1_ok = preco >= posicao["alvo1"] if direcao == "COMPRA" else preco <= posicao["alvo1"]
                    if alvo1_ok and not posicao["parcial_exec"]:
                        posicao["parcial_exec"] = True
                        ganho = abs(posicao["alvo1"] - entrada) * VALOR_PONTO_WIN * posicao["contratos_real"]
                        self.tg.alertar(f"🎯 Alvo1 WIN: {posicao['alvo1']:,.0f} | Parcial 50% | ~R${ganho:.2f}")
                    alvo2_ok = preco >= posicao["alvo2"] if direcao == "COMPRA" else preco <= posicao["alvo2"]
                    if alvo2_ok:
                        await self._fechar_posicao(posicao, "ALVO2"); return
                await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"Loop posição WIN: {e}")
            await self._fechar_posicao(posicao, "ERRO_INTERNO")

    async def _fechar_posicao(self, posicao: dict, motivo: str):
        preco_saida = self._preco_atual() or posicao["stop_atual"]
        direcao     = posicao["direcao"]
        entrada     = posicao["entrada_real"]
        contratos   = posicao["contratos_real"]
        resultado_pts   = (preco_saida - entrada) if direcao == "COMPRA" else (entrada - preco_saida)
        # ★ CRÍTICO WIN: R$0,20/pt/contrato (não R$5,00)
        resultado_reais = resultado_pts * VALOR_PONTO_WIN * contratos
        try:
            self.db.registrar_trade({
                "data": datetime.now().isoformat(), "direcao": direcao,
                "contratos": contratos, "entrada": entrada, "saida": preco_saida,
                "resultado_pts": resultado_pts, "resultado_reais": resultado_reais,
                "motivo_saida": motivo, "stop_final": posicao["stop_atual"],
                "breakeven_ativado": posicao["breakeven_ativo"],
                "trailing_ativado": posicao["trailing_ativo"],
                "score": posicao.get("score", 0),
                "modo": "PAPER" if PAPER_MODE else "REAL",
                "ordem_id": posicao.get("ordem_id", ""),
            })
        except Exception as e:
            logger.error(f"Erro ao registrar trade WIN: {e}")
        self.redis.delete("posicao_aberta")
        if resultado_reais > 0:
            self.redis.incr("ganhos_dia")
            self.redis.set("losses_consecutivos", "0")
        else:
            self.redis.incr("losses_consecutivos")
        capital_atual = self.redis.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
        novo_capital  = capital_atual + resultado_reais
        self.redis.set_capital(novo_capital)
        emoji = "✅" if resultado_reais > 0 else "❌"
        self.tg.alertar(
            f"{emoji} TRADE WIN — {motivo}\n"
            f"  {direcao} {contratos}x | {entrada:,.0f}→{preco_saida:,.0f}\n"
            f"  {resultado_pts:+.0f}pts | R${resultado_reais:+.2f} | Capital: R${novo_capital:,.2f}\n"
            f"  BE: {'✅' if posicao['breakeven_ativo'] else '❌'} | Trail: {'✅' if posicao['trailing_ativo'] else '❌'}"
        )
        self._posicao = None

    def _validar_json_cyber(self, output: dict) -> bool:
        campos = ["decisao", "direcao", "contratos", "entrada_zona", "stop", "alvo1", "alvo2", "gatilho", "risco_financeiro_reais"]
        for c in campos:
            if c not in output or output[c] is None:
                self.tg.alertar(f"❌ EXEC WIN: campo '{c}' ausente"); return False
        d, e, s, a = output.get("direcao"), output.get("entrada_zona", 0), output.get("stop", 0), output.get("alvo1", 0)
        if d == "COMPRA" and not (s < e < a):
            self.tg.alertar("❌ EXEC WIN: incoerência COMPRA"); return False
        if d == "VENDA" and not (s > e > a):
            self.tg.alertar("❌ EXEC WIN: incoerência VENDA"); return False
        return True

    def _preco_atual(self) -> float | None:
        try:
            v = self.redis.get("preco_atual_win")
            return float(v) if v else None
        except Exception:
            return None

    def _atr_recente(self) -> float:
        try:
            return float(self.redis.get("atr_atual_win") or "300.0")
        except Exception:
            return 300.0

    def _desarmar(self):
        self.redis.delete("posicao_aberta")
        self._posicao = None
        self._loop_ativo = False
```

═══════════════════════════════════════════════════════════════
[10] agents/cyber_agent.py WIN (✅ CÓDIGO TRUNCADO CORRIGIDO)
═══════════════════════════════════════════════════════════════
```python
# agents/cyber_agent.py
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO: código que estava truncado na versão original

import json, logging, os
from datetime import datetime, timedelta, timezone
from agents.base_agent import BaseAgent

logger = logging.getLogger("cyber_agent_win")

SNIPER_SCORE_MIN     = int(os.getenv("SNIPER_SCORE_MIN", "80"))
SNIPER_SLIPPAGE_MAX  = float(os.getenv("SNIPER_SLIPPAGE_MAX", "8.0"))
RISCO_POR_TRADE_PCT  = float(os.getenv("RISCO_POR_TRADE_PCT", "1.0"))
RR_MINIMO            = float(os.getenv("RR_MINIMO", "1.5"))
LATENCIA_MAX_S       = float(os.getenv("LATENCIA_MAX_S", "5.0"))
DESLOCAMENTO_MAX_PTS = float(os.getenv("DESLOCAMENTO_MAX_PTS", "50.0"))
VALOR_PONTO_WIN      = float(os.getenv("VALOR_PONTO_WIN", "0.20"))
MAX_OPERACOES_DIA    = int(os.getenv("MAX_OPERACOES_DIA", "5"))


class CyberAgent(BaseAgent):

    def __init__(self, router, redis_state=None):
        super().__init__(
            nome="neo",  # ID no router (usa nome Skynet)
            skill_path="./skills/cyber_skill_win.md",
            router=router,
            max_tokens=1500,
            temperature=0.1,
        )
        self.redis = redis_state

    async def decidir(self, cyber_input: dict) -> dict:
        sniper_mode = self._ler_sniper_mode(cyber_input["estado_sistema"])
        score_min   = self._score_minimo_atual(sniper_mode)
        max_c       = self._max_contratos_atual(sniper_mode)
        # ✅ CORRIGIDO: linha que estava truncada
        stop_max    = self._stop_maximo_atual()

        bloqueio = self._pre_filtro_deterministico(
            cyber_input["estado_sistema"],
            cyber_input["graph"],
            cyber_input["flow"],
            cyber_input["context"],
            sniper_mode, score_min, stop_max
        )
        if bloqueio:
            return self._decisao_cancelar(bloqueio, cyber_input, sniper_mode)

        cyber_input["estado_sistema"].update({
            "sniper_mode": sniper_mode,
            "score_minimo_ativo": score_min,
            "max_contratos_nivel": max_c,
            "stop_maximo_nivel": stop_max,
        })

        user_content = json.dumps(cyber_input, ensure_ascii=False, indent=2)
        try:
            resultado = await self.invocar(user_content)
        except Exception as e:
            logger.error(f"CYBER WIN LLM falhou: {e}")
            return self._decisao_cancelar(f"Erro LLM: {e}", cyber_input, sniper_mode)

        resultado = self._pos_validar(resultado, cyber_input, sniper_mode, score_min, max_c, stop_max)
        return resultado

    def _score_minimo_atual(self, sniper_mode: bool) -> int:
        if self.redis:
            try:
                key = "score_sniper_nivel" if sniper_mode else "score_minimo_nivel"
                v = self.redis.get(key)
                return int(v) if v else (SNIPER_SCORE_MIN if sniper_mode else 72)
            except Exception:
                pass
        return SNIPER_SCORE_MIN if sniper_mode else 72

    def _max_contratos_atual(self, sniper_mode: bool) -> int:
        if self.redis:
            try:
                v = self.redis.get("max_contratos_efetivo")
                return int(v) if v else 1
            except Exception:
                pass
        return 2 if sniper_mode else 1

    def _stop_maximo_atual(self) -> float:
        """✅ Método que estava truncado na versão original."""
        if self.redis:
            try:
                v = self.redis.get("stop_maximo_pts_nivel")
                return float(v) if v else 50.0
            except Exception:
                pass
        return 50.0  # Nível 1 hard cap

    def _stop_day_pct_atual(self) -> float:
        if self.redis:
            try:
                v = self.redis.get("stop_day_pct_nivel")
                return float(v) if v else 5.0
            except Exception:
                pass
        return 5.0

    def _pre_filtro_deterministico(self, estado, graph, flow, context,
                                    sniper_mode: bool, score_min: int, stop_max: float) -> str | None:
        stop_day = self._stop_day_pct_atual()
        res_dia  = estado.get("resultado_dia_percentual", 0)

        if res_dia <= -stop_day:
            return f"Stop-day WIN: {res_dia:.2f}% (limite: -{stop_day:.1f}%)"
        if estado.get("operacoes_hoje", 0) >= MAX_OPERACOES_DIA:
            return f"Máximo de {MAX_OPERACOES_DIA} operações atingido"
        if estado.get("em_cool_down", False):
            return "Cool-down ativo (3 losses consecutivos)"
        if context.get("status_macro") == "BLOQUEADO":
            return "ORACLE: evento macro BLOQUEADO"
        if context.get("qualidade_sessao") in ("PROIBIDO",):
            return f"Sessão proibida: {context.get('sessao_atual')}"
        if context.get("ny_open_status") == "BLOQUEADO":
            return "Abertura NY: primeiros 3min bloqueados"
        if graph.get("sinal") == "NEUTRO" or graph.get("confianca", 0) == 0:
            return "ARCHITECT: sinal NEUTRO ou confiança zero"
        if graph.get("confianca", 0) < 60:
            return f"ARCHITECT: confiança {graph.get('confianca')} < 60"
        if flow.get("forca_fluxo", 0) < 40:
            return f"MORPHEUS: força {flow.get('forca_fluxo')} < 40"
        if context.get("regime_mercado") == "MORTO":
            return "Regime MORTO: ATR_WIN < 0.6× média"
        if graph.get("tendencia_master_15m") == "INDEFINIDA":
            return "ARCHITECT: tendência 15m INDEFINIDA"
        sinal   = graph.get("sinal")
        cvd_div = flow.get("divergencia_cvd_preco", False)
        if cvd_div and sinal == "COMPRA":
            return "CVD: divergência baixista — não comprar WIN"
        if cvd_div and sinal == "VENDA":
            return "CVD: divergência altista — não vender WIN"
        if flow.get("exaustao_tps", False):
            return "Exaustão TPS WIN: momentum esgotado"
        lat  = estado.get("latencia_ciclo_segundos", 0)
        desl = estado.get("deslocamento_preco_desde_analise", 0)
        if lat > LATENCIA_MAX_S and desl > DESLOCAMENTO_MAX_PTS:
            return f"Latência {lat:.1f}s + deslocamento {desl:.0f}pts WIN"
        if sniper_mode:
            score_est = self._estimar_score(graph, flow, context)
            if score_est < SNIPER_SCORE_MIN:
                return f"Sniper WIN: score est {score_est} < {SNIPER_SCORE_MIN}"
        return None

    def _estimar_score(self, graph, flow, context) -> int:
        g   = graph.get("confianca", 0) / 80 * 100 * 0.35
        f   = flow.get("forca_fluxo", 0) * 0.30
        pen = context.get("penalidade_score", 0)
        bon = context.get("sp500", {}).get("bonus_correlacao", 0)
        c   = max(0, 100 - pen + bon) * 0.30
        t   = (100 if context.get("qualidade_sessao") in ("EXCELENTE", "BOA") else 70) * 0.05
        score = g + f + c + t
        if flow.get("iceberg_detectado"): score += 10
        if flow.get("held_level", {}).get("detectado"): score += 7
        if flow.get("divergencia_cvd_preco"): score -= 10
        if graph.get("volume_relativo", 1.0) < 0.8: score -= 10
        return int(min(100, max(0, score)))

    def _pos_validar(self, resultado: dict, cyber_input: dict,
                     sniper_mode: bool, score_min: int, max_c: int, stop_max: float) -> dict:
        estado  = cyber_input["estado_sistema"]
        decisao = resultado.get("decisao", "CANCELAR")
        score   = resultado.get("score_final", 0)
        motivos = []

        if decisao == "ARMAR" and score < score_min:
            motivos.append(f"Score {score} < mínimo {score_min}")

        rr = resultado.get("rr_alvo1", 0)
        if decisao == "ARMAR" and rr < RR_MINIMO:
            motivos.append(f"R:R {rr:.2f} < {RR_MINIMO}")

        contratos = resultado.get("contratos", 1)
        if contratos > max_c:
            logger.warning(f"Contratos {contratos} > max nível {max_c} → limitado")
            resultado["contratos"] = max_c

        stop_pts = abs((resultado.get("entrada_zona") or 0) - (resultado.get("stop") or 0))
        if decisao == "ARMAR" and stop_pts > stop_max:
            motivos.append(f"Stop {stop_pts:.0f}pts > máx nível {stop_max:.0f}pts WIN")

        capital    = estado.get("capital_atual", 1000)
        risco_max  = capital * RISCO_POR_TRADE_PCT / 100
        risco_calc = stop_pts * VALOR_PONTO_WIN * resultado.get("contratos", 1)
        if risco_calc > risco_max * 1.05 and decisao == "ARMAR":
            motivos.append(f"Risco R${risco_calc:.2f} > 1% capital (R${risco_max:.2f})")

        if decisao == "ARMAR":
            d, e, s, a = resultado.get("direcao",""), resultado.get("entrada_zona",0), resultado.get("stop",0), resultado.get("alvo1",0)
            if d == "COMPRA" and not (s < e < a):
                motivos.append("Incoerência preços COMPRA WIN")
            elif d == "VENDA" and not (s > e > a):
                motivos.append("Incoerência preços VENDA WIN")

        stop_day = self._stop_day_pct_atual()
        if estado.get("resultado_dia_percentual", 0) <= -stop_day:
            motivos.append(f"Stop-day WIN pós-validação: {estado.get('resultado_dia_percentual', 0):.2f}%")

        losses = estado.get("losses_consecutivos", 0)
        if losses >= 2 and decisao == "ARMAR":
            resultado["contratos"] = 1
        if estado.get("resultado_dia_percentual", 0) < 0 and decisao == "ARMAR" and resultado.get("contratos", 1) > 1:
            resultado["contratos"] = 1

        ef = estado.get("equity_filter_10d", 1.0)
        if ef <= 0.5:  resultado["contratos"] = 1
        elif ef <= 0.75: resultado["contratos"] = min(resultado.get("contratos", 1), 2)

        if decisao == "ARMAR" and "gatilho" in resultado:
            g = resultado["gatilho"]
            if not g.get("validade_expira_em"):
                expira = datetime.now(timezone.utc) + timedelta(seconds=g.get("validade_segundos", 90))
                g["validade_expira_em"] = expira.isoformat()
                resultado["gatilho"] = g

        if motivos:
            resultado["decisao"] = "CANCELAR"
            resultado["motivo"] = f"PÓS-VALIDAÇÃO WIN: {' | '.join(motivos)}"
            logger.warning(f"CYBER WIN → CANCELAR: {motivos}")

        resultado.update({
            "sniper_mode_ativo": sniper_mode,
            "modo": "PAPER" if os.getenv("PAPER_MODE", "true").lower() == "true" else "REAL",
            "nivel_capital": self.redis.get("nome_nivel_capital") if self.redis else "N/D",
            "max_contratos_nivel": max_c,
            "stop_maximo_nivel": stop_max,
        })
        return resultado

    def _ler_sniper_mode(self, estado: dict) -> bool:
        if self.redis:
            try:
                v = self.redis.get("sniper_mode")
                if v is not None:
                    return str(v).lower() == "true"
            except Exception:
                pass
        return estado.get("sniper_mode", False)

    def _decisao_cancelar(self, motivo: str, cyber_input: dict, sniper_mode: bool) -> dict:
        return {
            "agente": "CYBER_WIN", "timestamp": datetime.now(timezone.utc).isoformat(),
            "decisao": "CANCELAR", "score_final": 0, "score_detalhado": {},
            "setup_classificacao": "NENHUM", "tipo_setup": None,
            "direcao": None, "contratos": 0, "entrada_zona": None,
            "stop": None, "alvo1": None, "alvo2": None, "rr_alvo1": 0,
            "gatilho": None, "risco_financeiro_reais": 0, "risco_percentual": 0,
            "motivo": motivo, "alertas_operador": [],
            "sniper_mode_ativo": sniper_mode, "_pre_filtro": True,
            "modo": "PAPER" if os.getenv("PAPER_MODE","true").lower()=="true" else "REAL",
        }
```

═══════════════════════════════════════════════════════════════
[11] utils/risk_manager.py WIN
═══════════════════════════════════════════════════════════════
```python
# utils/risk_manager.py WIN
# CYBER TRADE WIN v2.1

import logging, os
logger = logging.getLogger("risk_manager_win")

RISCO_PCT       = float(os.getenv("RISCO_POR_TRADE_PCT", "1.0"))
VALOR_PONTO_WIN = float(os.getenv("VALOR_PONTO_WIN", "0.20"))


class RiskManager:
    def calcular_contratos(self, capital: float, stop_pts: float,
                           max_contratos_nivel: int = 1,
                           equity_filter: float = 1.0,
                           losses_consecutivos: int = 0,
                           resultado_dia_pct: float = 0.0,
                           sniper_mode: bool = False,
                           stop_maximo_nivel: float = 50.0) -> int:
        if stop_pts <= 0: return 1
        stop_efetivo   = min(stop_pts, stop_maximo_nivel)
        risco_reais    = capital * RISCO_PCT / 100
        risco_contrato = stop_efetivo * VALOR_PONTO_WIN
        contratos      = int(risco_reais / risco_contrato) if risco_contrato > 0 else 1
        max_c = min(2 if sniper_mode else max_contratos_nivel, 5)
        if equity_filter <= 0.5:    max_c = 1
        elif equity_filter <= 0.75: max_c = min(max_c, 2)
        if resultado_dia_pct < 0:        contratos = min(contratos, 1)
        if losses_consecutivos >= 2:     contratos = 1
        return max(1, min(contratos, max_c))

    def risco_financeiro(self, capital: float, contratos: int, stop_pts: float) -> float:
        return contratos * stop_pts * VALOR_PONTO_WIN

    def calcular_equity_filter(self, trades_10d: list, capital: float) -> float:
        if not trades_10d: return 1.0
        pnl = sum(t.get("resultado_reais", 0) for t in trades_10d)
        pct = pnl / capital * 100
        if pct <= -3.0: return 0.5
        if pct <= -1.5: return 0.75
        return 1.0
```

═══════════════════════════════════════════════════════════════
[12] infrastructure/llm_router.py WIN (✅ Fallback recursivo corrigido)
═══════════════════════════════════════════════════════════════
```python
# infrastructure/llm_router.py WIN
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO: fallback sem recursão infinita

import os
from google import genai
import anthropic
from loguru import logger


class LLMRouter:
    def __init__(self, cost_monitor=None):
        self.paper_mode   = os.getenv("PAPER_MODE", "true").lower() == "true"
        self.gemma_client = genai.Client(api_key=os.getenv("GOOGLE_AI_API_KEY"))
        self.claude_client= anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.gemma_model  = os.getenv("GEMMA_MODEL", "gemma-4-31b-it")
        # ✅ Model string correto
        self.claude_model = "claude-sonnet-4-6"
        self.cost_monitor = cost_monitor
        logger.info(f"🤖 LLM Router WIN v2.1 | PAPER: {self.paper_mode}")

    async def call(self, agent_id: str, prompt: str, system: str) -> str:
        is_critical = agent_id in ["neo", "cyberdyne"]
        if self.paper_mode or not is_critical:
            provider, model = "gemma", self.gemma_model
        else:
            provider, model = "claude", self.claude_model
        try:
            return await self._call_provider(provider, model, agent_id, prompt, system)
        except Exception as e:
            logger.error(f"Router WIN falhou ({provider}): {e}")
            # ✅ CORRIGIDO: fallback direto sem recursão
            if provider == "claude":
                logger.warning(f"⚠️ Fallback WIN: Claude → Gemma para {agent_id}")
                try:
                    return await self._call_gemma(self.gemma_model, agent_id, prompt, system)
                except Exception as e2:
                    raise RuntimeError(f"Ambos provedores falharam WIN: {e} | {e2}")
            raise

    async def _call_provider(self, provider, model, agent_id, prompt, system):
        if provider == "gemma":
            return await self._call_gemma(model, agent_id, prompt, system)
        return await self._call_claude(model, agent_id, prompt, system)

    async def _call_gemma(self, model, agent_id, prompt, system):
        resp = self.gemma_client.models.generate_content(
            model=model,
            contents=f"{system}\n\n{prompt}",
            config={"response_mime_type": "application/json"},
        )
        if self.cost_monitor:
            self.cost_monitor.log_tokens(agent_id, len(prompt.split()), len(resp.text.split()), "gemma")
        return resp.text

    async def _call_claude(self, model, agent_id, prompt, system):
        resp = await self.claude_client.messages.create(
            model=model, max_tokens=1500,
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        if self.cost_monitor:
            self.cost_monitor.log_tokens(agent_id, resp.usage.input_tokens, resp.usage.output_tokens, "claude")
        return resp.content[0].text

    def status(self) -> dict:
        return {
            "paper_mode": self.paper_mode,
            "modelos": {
                "neo": self.gemma_model if self.paper_mode else self.claude_model,
                "cyberdyne": self.gemma_model if self.paper_mode else self.claude_model,
                "outros": self.gemma_model,
            },
        }
```

═══════════════════════════════════════════════════════════════
[13] infrastructure/cost_monitor.py WIN (✅ Lógica 80%/100% corrigida)
═══════════════════════════════════════════════════════════════
```python
# infrastructure/cost_monitor.py WIN
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO: alerta 80% e 100% com flags independentes

import os, json, time
from datetime import date
from loguru import logger


class CostMonitor:
    PRECO_GEMMA  = 0.0000015
    PRECO_CLAUDE = 0.003

    def __init__(self, alerta_callback=None):
        self.alerta_callback = alerta_callback
        self.budget   = float(os.getenv("DAILY_API_BUDGET_USD", "0.10"))
        self.cost_path = os.getenv("COST_LOG_PATH", "./logs/cost_today.json")
        self.tokens_in, self.tokens_out, self.calls = {}, {}, {}
        self.total_usd = 0.0
        # ✅ Flags independentes por threshold
        self._alerta_80_enviado  = False
        self._alerta_100_enviado = False
        self._throttled          = False
        self._data = str(date.today())
        self._carregar_log()

    def log_tokens(self, agent: str, input_t: int, output_t: int, provider: str = "gemma"):
        self.tokens_in[agent]  = self.tokens_in.get(agent, 0) + input_t
        self.tokens_out[agent] = self.tokens_out.get(agent, 0) + output_t
        self.calls[agent]      = self.calls.get(agent, 0) + 1
        preco_in  = self.PRECO_CLAUDE if provider == "claude" else self.PRECO_GEMMA
        preco_out = preco_in * 3
        self.total_usd += (input_t * preco_in) + (output_t * preco_out)
        pct = (self.total_usd / self.budget) * 100 if self.budget else 0

        # ✅ CORRIGIDO: verifica 80% ANTES e INDEPENDENTE de 100%
        if pct >= 80.0 and not self._alerta_80_enviado:
            self._alerta_80_enviado = True
            msg = f"⚠️ CUSTO WIN 80%: ${self.total_usd:.4f}/${self.budget:.2f} ({pct:.0f}%)"
            logger.warning(msg)
            if self.alerta_callback: self.alerta_callback(msg)

        if pct >= 100.0 and not self._alerta_100_enviado:
            self._alerta_100_enviado = True
            self._throttled = True
            msg = f"🛑 CUSTO WIN ESGOTADO: ${self.total_usd:.4f}/${self.budget:.2f} — Pausando secundários."
            logger.error(msg)
            if self.alerta_callback: self.alerta_callback(msg)

        self._salvar_log()

    @property
    def orcamento_esgotado(self) -> bool:
        return self._throttled

    @property
    def restante_usd(self) -> float:
        return max(0.0, self.budget - self.total_usd)

    def reset_daily(self):
        if str(date.today()) == self._data:
            return  # Mesmo dia — não resetar
        self.tokens_in.clear(); self.tokens_out.clear(); self.calls.clear()
        self.total_usd = 0.0
        self._alerta_80_enviado = self._alerta_100_enviado = self._throttled = False
        self._data = str(date.today())
        self._salvar_log()
        logger.info("💀 REAPER WIN: custos resetados.")

    def _salvar_log(self):
        try:
            os.makedirs(os.path.dirname(self.cost_path) or ".", exist_ok=True)
            with open(self.cost_path, "w") as f:
                json.dump({"date": self._data, "total_usd": round(self.total_usd, 6),
                           "orcamento_usd": self.budget, "agents": self.calls}, f)
        except Exception as e:
            logger.error(f"Erro log custo WIN: {e}")

    def _carregar_log(self):
        try:
            if os.path.exists(self.cost_path):
                with open(self.cost_path) as f:
                    d = json.load(f)
                if d.get("date") == self._data:
                    self.total_usd = d.get("total_usd", 0.0)
        except Exception:
            pass
```

═══════════════════════════════════════════════════════════════
[14] tape/tape_reader_polars.py WIN (✅ Chave Redis + Polars corrigidos)
═══════════════════════════════════════════════════════════════
```python
# tape/tape_reader_polars.py WIN
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO 1: chave Redis padronizada para "tape_metricas"
# ✅ CORRIGIDO 2: sintaxe Polars 0.20+ correta

import polars as pl
import redis, json, time
from loguru import logger


class PolarsTapeEngineWIN:
    def __init__(self):
        self.r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
        self.buffer: list[dict] = []

    def add_ticks(self, raw_ticks: list[dict]):
        self.buffer.extend(raw_ticks)
        if len(self.buffer) > 10000:
            self.buffer = self.buffer[-5000:]

    def compute_metrics(self) -> dict:
        if not self.buffer:
            return {}
        t0 = time.perf_counter()
        df = pl.DataFrame(self.buffer)

        # ✅ CORRIGIDO: sintaxe Polars correta para somas condicionais
        profile = (
            df.with_columns([
                pl.when(pl.col("agressor") == "COMPRA")
                  .then(pl.col("volume")).otherwise(0).alias("buy_vol_raw"),
                pl.when(pl.col("agressor") == "VENDA")
                  .then(pl.col("volume")).otherwise(0).alias("sell_vol_raw"),
            ])
            .group_by("preco")
            .agg([
                pl.col("buy_vol_raw").sum().alias("buy_vol"),
                pl.col("sell_vol_raw").sum().alias("sell_vol"),
                (pl.col("buy_vol_raw").sum() - pl.col("sell_vol_raw").sum()).alias("delta_vol"),
                pl.col("volume").sum().alias("total_vol"),
                pl.len().alias("num_prints"),
            ])
            .sort("preco")
        )

        total_buy  = int(profile["buy_vol"].sum())
        total_sell = int(profile["sell_vol"].sum())
        cvd = total_buy - total_sell

        held_vol_base   = int(self.r.get("held_vol_base") or 200)
        held_prints_min = int(self.r.get("held_prints_min") or 2)

        candidatos = profile.filter(pl.col("total_vol") >= held_vol_base)
        held_bid = held_offer = {"detectado": False, "volume": 0, "prints": 0}
        if not candidatos.is_empty():
            for side in ("buy_vol", "sell_vol"):
                nome = "held_bid" if side == "buy_vol" else "held_offer"
                melhor = candidatos.sort(side, descending=True).head(1)
                vol    = int(melhor[side][0])
                prints = int(melhor["num_prints"][0])
                det    = vol >= held_vol_base and prints >= held_prints_min
                obj    = {"detectado": det, "volume": vol, "prints": prints}
                if nome == "held_bid":   held_bid = obj
                else:                   held_offer = obj

        now_ts = self.buffer[-1].get("timestamp", 0) if self.buffer else 0
        recente  = [t for t in self.buffer if t.get("timestamp", 0) >= now_ts - 30]
        anterior = [t for t in self.buffer if now_ts - 90 <= t.get("timestamp", 0) < now_ts - 30]
        tps_rec = len(recente) / 30 if recente else 0
        tps_ant = len(anterior) / 60 if anterior else 0.001
        acel    = round(tps_rec / tps_ant, 2)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        if elapsed_ms > 20:
            logger.warning(f"⚠️ Polars WIN acima de 20ms: {elapsed_ms:.1f}ms")

        metrics = {
            "cvd_total": cvd,
            "cvd_1min": cvd,
            "buy_vol_total": total_buy,
            "sell_vol_total": total_sell,
            "divergencia_cvd_preco": False,  # calculado externamente
            "held_bid_detectado": held_bid["detectado"],
            "held_bid_volume": held_bid["volume"],
            "held_bid_prints_confirmadores": held_bid["prints"],
            "held_offer_detectado": held_offer["detectado"],
            "held_offer_volume": held_offer["volume"],
            "held_offer_prints_confirmadores": held_offer["prints"],
            "aceleracao_tape": acel,
            "burst_detectado": acel >= 2.0,
            "sweep_detectado": False,
            "iceberg_detectado": False,
            "exaustao_tps": False,
            "latencia_ms": round(elapsed_ms, 2),
        }

        # ✅ CORRIGIDO: chave padronizada "tape_metricas" (não "tape_metrics_win")
        self.r.set("tape_metricas", json.dumps(metrics))
        self.r.expire("tape_metricas", 60)
        return metrics
```

═══════════════════════════════════════════════════════════════
[15] skills/context_skill_win.md (✅ Horário alerta 17:15 corrigido)
═══════════════════════════════════════════════════════════════
```markdown
# ORACLE WIN — Macro IBOV + S&P500 + DI1F | Cyber Trade WIN v2.1

## IDENTIDADE
ORACLE do Cyber Trade WIN v2.1. Analisa contexto macro do WINFUT.
NÃO usa DXY/Ptax como drivers primários — são irrelevantes para índice.
Responda APENAS com JSON válido.

## DRIVERS MACRO WIN (prioridade)
1. S&P500: correlação diária ~75%. Alta SP → bias alta WIN.
2. VIX: >25 = aversão a risco | >35 = BLOQUEADO TOTAL
3. IBOV: composição ~20% PETR/VALE — influência commodities
4. DI1F: alta juros = pressão vendedora no índice
5. Petróleo Brent: Petrobras ~10% IBOV — Brent forte → WIN alta
6. Minério de Ferro: Vale ~8% IBOV — Minério forte → WIN alta

## PROTOCOLO (6 PASSOS)

### PASSO 1 — Status Macro (bloqueador master)
- BLOQUEADO: Decisão COPOM | PIB BR | Payroll EUA | CPI EUA em < 30min
- BLOQUEADO: VIX > 35
- ALERTA_REACAO (-25): evento alto publicado há < 15min
- MORTO: ATR_WIN < 0.6× média → BLOQUEADO

### PASSO 2 — S&P500
- SP subindo + WIN subindo: +10
- SP subindo + WIN caindo: DIVERGÊNCIA → -15
- SP caindo forte: -10 compras WIN

### PASSO 3 — VIX
- < 15: normal | 15-25: sem ajuste | 25-35: -10 | > 35: BLOQUEADO

### PASSO 4 — DI1F
- Alta surpresa COPOM: -20 compras | Alta >0.5%/h: -15 compras | Estável: sem ajuste

### PASSO 5 — Commodities
- Brent ou Minério +1%: +5 compras WIN | Ambos caindo forte: -10 compras

### PASSO 6 — Sessão e Cutoff WIN
SESSÕES:
- ABERTURA (09:00-09:15): PROIBIDO
- MANHA_INICIAL (09:15-10:30): MODERADA
- NY_TRANSICAO (10:30-10:48): CAUTELA
- MANHA_ATIVA (10:48-12:00): EXCELENTE
- ALMOCO (12:00-13:30): PROIBIDO
- TARDE_ATIVA (14:15-16:30): BOA
- TARDE_FINAL (16:30-17:15): MODERADA
- ENCERRANDO (17:15-17:30): PROIBIDO ← ✅ CORRIGIDO (era 15:45)

## CUTOFF WIN (✅ CORRIGIDO)
SE horario >= 17:15 → alerta_finalizacao = true (NEO bloqueia novos trades)
SE horario >= 17:30 → BLOQUEADO TOTAL

## OUTPUT (JSON exato)
{
  "agente": "ORACLE_WIN",
  "timestamp": "<ISO8601>",
  "status_macro": "LIBERADO",
  "penalidade_score": 0,
  "regime_mercado": "TRENDING_NORMAL",
  "fator_liquidez_horario": 1.0,
  "sp500": {
    "tendencia": "ALTA",
    "alinhamento_win": "ALINHADO",
    "bonus_correlacao": 10,
    "divergencia_detectada": false
  },
  "vix": {"nivel": 18.5, "status": "NORMAL", "penalidade": 0},
  "di1f": {"variacao_1h_pct": 0.05, "inclinacao": "ESTAVEL", "penalidade_di1f": 0},
  "commodities": {"petroleo_brent_var_pct": 0.8, "minerio_ferro_var_pct": 0.3, "bonus_commodities": 5},
  "sessao_atual": "MANHA_ATIVA",
  "qualidade_sessao": "EXCELENTE",
  "alerta_finalizacao": false,
  "alertas": [],
  "resumo": "<texto em PT-BR>"
}

## REGRAS ABSOLUTAS
❌ NUNCA liberar com VIX > 35
❌ NUNCA ignorar COPOM, PIB, Payroll, CPI iminentes (<30min)
❌ NUNCA liberar sessões PROIBIDO
❌ NUNCA mencionar DXY/Ptax como driver primário
✅ alerta_finalizacao = true quando >= 17:15 (WIN) — não 15:45!
```

═══════════════════════════════════════════════════════════════
[16] skills/graph_skill_win.md
═══════════════════════════════════════════════════════════════
```markdown
# ARCHITECT WIN — Análise Técnica WINFUT | Cyber Trade WIN v2.1

## IDENTIDADE
Análise técnica multi-timeframe WINFUT. Preços ~130.000–135.000 pts. Tick mínimo: 5pts.

## ESCALA WIN
ATR 5min: 200–800pts | Stop mínimo: 80pts | Stop máximo: 2×ATR

## PROTOCOLO (5 PASSOS)
1. Tendência 15m: EMA9>EMA21=ALTA(só C) | EMA9<EMA21=BAIXA(só V) | |Δ|<100pts=INDEFINIDA
2. Localização: vs VWAP/POC. Extremos dia (<1×ATR) → não operar contra.
3. Momentum 5m: RSI 40-65(C)/35-60(V) | Vol <0.8x(-15) | >1.2x(+10)
4. Candle: Engolfo (corpo >100pts) | Martelo | Pin Bar
5. R:R: Stop máx 2×ATR. Alvo1 R:R≥1.5. <1.5 → NEUTRO.

## OUTPUT (JSON)
{
  "agente": "ARCHITECT_WIN", "timestamp": "<ISO8601>",
  "tendencia_master_15m": "ALTA", "tendencia_5m": "ALTA",
  "alinhamento_timeframes": true, "sinal": "COMPRA", "confianca": 72,
  "entrada_sugerida": 132650, "stop_sugerido": 132350,
  "alvo1_sugerido": 133100, "alvo2_sugerido": 133500,
  "rr_alvo1": 1.5, "distancia_stop_pontos": 300, "atr_win": 380,
  "volume_relativo": 1.35, "alertas": [], "resumo": "<texto PT-BR>"
}

## REGRAS
❌ Confiança >80 | ❌ Contra tendência 15m | ❌ Stop >2×ATR | ❌ Stop <80pts | ❌ R:R <1.5
✅ Preços múltiplos de 5 | ✅ Dúvida = NEUTRO
```

═══════════════════════════════════════════════════════════════
[17] skills/cyber_skill_win.md
═══════════════════════════════════════════════════════════════
```markdown
# NEO WIN — Orquestrador e Decisão | Cyber Trade WIN v2.1

## IDENTIDADE
NEO. Único autorizado a decidir ARMAR/AGUARDAR/CANCELAR. Filosofia: dúvida = AGUARDAR.

## PARÂMETROS WIN
Valor ponto: R$0,20/pt/contrato | Risco: 1% capital
Max contratos: dinâmico (estado.max_contratos_nivel)
Score mínimo: dinâmico (estado.score_minimo_ativo)
Stop máximo: dinâmico (estado.stop_maximo_nivel)

## PROTOCOLO (7 PASSOS)
1. Filtros bloqueio: ORACLE BLOQUEADO | qualidade_sessao PROIBIDO | VIX>35 | cool_down
   | ops>=5 | pnl<=-(stop_day) | ARCHITECT NEUTRO | MORPHEUS força<40 | regime MORTO
   | divergencia CVD | exaustao_tps | latencia>5s+deslocamento>50pts
2. Alinhamento: sinal ≠ direcao_fluxo → CANCELAR
3. Dynamic Weighting (ATR WIN):
   ATR<300(Range): tape 80%/graph 20%
   300-600(Normal): 50/50
   >600(Trend): graph 70%/tape 30%
4. Score (✅ pesos somam 1.00):
   score = (confianca/80*100 * w_g * 0.60) + (forca_fluxo * w_t * 0.60) + (ctx_norm * 0.30) + (timing * 0.10)
   Ajustes: iceberg+10 | held+7 | SP500+5 | spoof-15 | VIX_alto-10 | div_cvd-10
5. Limiares: >=85 PREMIUM | >=score_min ARMAR | 55-64 AGUARDAR | <55 CANCELAR
6. Sizing WIN: contratos = floor(capital*0.01 / (stop_pts*0.20)) limitado por nivel
7. Gatilho: ROMPIMENTO(±5pts+Δ>100+burst,120s) | PULLBACK(±10pts+Held,90s)
   CONTINUAÇÃO(Δ≥80+±15pts,60s) | SWEEP(±20pts,45s) | ICEBERG(±10pts,75s)

## OUTPUT (JSON)
{
  "agente": "NEO_WIN", "timestamp": "<ISO8601>", "decisao": "ARMAR",
  "score_final": 78, "score_detalhado": {"total": 78},
  "setup_classificacao": "PADRÃO", "tipo_setup": "PULLBACK_ABSORÇÃO",
  "direcao": "COMPRA", "contratos": 1,
  "entrada_zona": 132650, "stop": 132350, "alvo1": 133100, "alvo2": 133500,
  "rr_alvo1": 1.5,
  "gatilho": {"tipo": "PULLBACK_ABSORÇÃO", "descricao": "Held Bid @ 132600", "validade_segundos": 90, "validade_expira_em": "<ISO8601>"},
  "risco_financeiro_reais": 60.0, "risco_percentual": 1.0,
  "nivel_capital": "INICIANTE", "max_contratos_nivel": 1, "stop_maximo_nivel": 50,
  "modo": "PAPER", "motivo": "<explicação>", "alertas_operador": []
}
```

═══════════════════════════════════════════════════════════════
[18] guard.py WIN (✅ Bug de data do final do mês corrigido)
═══════════════════════════════════════════════════════════════
```python
# guard.py WIN
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO: bug day+1 no final do mês

import asyncio, json, logging, os
from datetime import datetime, timedelta, time as dtime
import redis as redis_lib
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("guard_win")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"


class Guard:
    def __init__(self):
        self.r = redis_lib.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD") or None,
            decode_responses=True,
        )
        try:
            from infrastructure.telegram_bot import TelegramBot
            self.tg = TelegramBot()
        except Exception as e:
            logger.warning(f"Telegram indisponível: {e}"); self.tg = None

        self._sniper_mode = False
        self._custo_alerta_80_enviado = False
        self._capital_level_mgr = None

    async def iniciar(self):
        try:
            from utils.capital_levels import CapitalLevelManager, get_nivel
            from infrastructure.redis_state import RedisState
            from infrastructure.database import Database
            rs = RedisState()
            db = Database()
            self._capital_level_mgr = CapitalLevelManager(rs, self.tg, db)
            capital = rs.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
            nivel   = get_nivel(capital)
            self._capital_level_mgr.aplicar_nivel_ao_redis(nivel)
        except Exception as e:
            logger.error(f"CapitalLevelManager: {e}")

        modo = "🟡 PAPER" if PAPER_MODE else "🔴 PRODUÇÃO"
        cap  = float(os.getenv("CAPITAL_INICIAL", "1000"))
        self._alertar(
            f"🛡️ GUARD WIN v2.1 | {modo}\n"
            f"💰 Capital: R${cap:,.2f} | WINFUT | Máx 5 contratos\n"
            f"🎯 Meta: R$5.000 | Cutoff: 17:30 BRT"
        )

        await self._checar_posicoes_abertas()
        if not self.r.exists("sniper_mode"):
            self.r.set("sniper_mode", "false")

        await asyncio.gather(
            self._loop_health_check(),
            self._loop_monitoramento_custo(),
            self._loop_telegram_handler(),
            self._loop_relatorio_diario(),
            self._loop_monitoramento_capital(),
        )

    async def _loop_health_check(self):
        while True:
            await asyncio.sleep(60)
            await self._health_check()

    async def _health_check(self):
        falhas = []
        try:
            self.r.ping()
        except Exception as e:
            falhas.append(f"Redis offline: {e}")
        if not os.getenv("GOOGLE_AI_API_KEY"):
            falhas.append("GOOGLE_AI_API_KEY ausente")
        if not PAPER_MODE and not os.getenv("ANTHROPIC_API_KEY"):
            falhas.append("ANTHROPIC_API_KEY ausente")
        await self._checar_metricas_operacao()
        if len(falhas) >= 2:
            self._alertar(f"🚨 GUARD WIN: {len(falhas)} FALHAS\n" +
                          "\n".join(f"  • {f}" for f in falhas))
            self.r.set("sistema_pausado", "true")
        elif falhas:
            for f in falhas:
                self._alertar(f"⚠️ GUARD WIN: {f}")

    async def _loop_monitoramento_capital(self):
        while True:
            await asyncio.sleep(300)
            if self._capital_level_mgr:
                try:
                    await self._capital_level_mgr.verificar_nivel()
                except Exception as e:
                    logger.error(f"Verificar nível capital: {e}")

    async def _loop_monitoramento_custo(self):
        while True:
            await asyncio.sleep(60)
            await self._checar_custo()

    async def _checar_custo(self):
        try:
            cost_path = os.getenv("COST_LOG_PATH", "./logs/cost_today.json")
            with open(cost_path) as f:
                dados = json.load(f)
            total     = dados.get("total_usd", 0.0)
            orcamento = dados.get("orcamento_usd", float(os.getenv("DAILY_API_BUDGET_USD", "0.10")))
            pct       = total / orcamento * 100 if orcamento > 0 else 0
            self.r.set("custo_api_hoje", f"{total:.4f}")
            self.r.set("custo_pct", f"{pct:.1f}")
            # ✅ Verificar 80% independentemente
            if pct >= 80 and not self._custo_alerta_80_enviado:
                self._custo_alerta_80_enviado = True
                self._alertar(f"⚠️ CUSTO WIN {pct:.0f}%: ${total:.4f}/${orcamento:.2f}")
            if pct >= 100:
                self._alertar(f"🛑 CUSTO WIN ESGOTADO: ${total:.4f}/${orcamento:.2f}")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        except Exception as e:
            logger.error(f"Checar custo WIN: {e}")

    async def _checar_posicoes_abertas(self):
        try:
            pos_str = self.r.get("posicao_aberta")
            if pos_str:
                pos = json.loads(pos_str)
                if pos.get("status") == "ABERTA":
                    self._alertar(
                        f"⚠️ REINÍCIO WIN COM POSIÇÃO ABERTA!\n"
                        f"  Direção: {pos.get('direcao')} | Contratos: {pos.get('contratos')}\n"
                        f"  Entrada: {pos.get('entrada_real'):,.0f} | Stop: {pos.get('stop_atual'):,.0f}\n"
                        f"  Verificar manualmente no Profit Pro!"
                    )
        except Exception as e:
            logger.error(f"Checar posições abertas: {e}")

    async def _checar_metricas_operacao(self):
        try:
            losses   = int(self.r.get("losses_consecutivos") or 0)
            res_dia  = float(self.r.get("resultado_dia_pct") or 0)
            stop_day = float(self.r.get("stop_day_pct_nivel") or 5.0)
            if losses >= 3:
                self._alertar(f"⛔ {losses} losses WIN consecutivos → cool-down")
            if res_dia <= -(stop_day * 0.8) and res_dia > -stop_day:
                self._alertar(f"⚠️ Resultado WIN {res_dia:.2f}% — próximo stop-day (-{stop_day:.1f}%)")
            if res_dia <= -stop_day:
                self._alertar(f"🛑 STOP-DAY WIN: {res_dia:.2f}%")
        except Exception as e:
            logger.error(f"Checar métricas WIN: {e}")

    async def _loop_telegram_handler(self):
        while True:
            await asyncio.sleep(5)
            try:
                msg = self.r.lpop("telegram_inbox")
                if msg:
                    await self._processar_comando(msg)
            except Exception as e:
                logger.error(f"Telegram handler WIN: {e}")

    async def _processar_comando(self, msg: str):
        msg_upper = msg.strip().upper()

        if msg_upper == "SNIPER ON":
            self.r.set("sniper_mode", "true")
            if self._capital_level_mgr:
                await self._capital_level_mgr.verificar_nivel()
            self._alertar("🎯 SNIPER MODE WIN ATIVADO\n  Score: 80 | Slippage: 8pts")

        elif msg_upper == "SNIPER OFF":
            self.r.set("sniper_mode", "false")
            if self._capital_level_mgr:
                await self._capital_level_mgr.verificar_nivel()
            self._alertar("📊 SNIPER MODE WIN DESATIVADO — parâmetros do nível restaurados.")

        elif msg_upper == "/STATUS":
            sniper  = self.r.get("sniper_mode") == "true"
            custo   = self.r.get("custo_api_hoje") or "0.0000"
            pct     = self.r.get("custo_pct") or "0.0"
            pausado = self.r.get("sistema_pausado") == "true"
            nivel   = self.r.get("nome_nivel_capital") or "N/D"
            max_c   = self.r.get("max_contratos_efetivo") or "1"
            modo    = "🟡 PAPER" if PAPER_MODE else "🔴 REAL"
            self._alertar(
                f"📊 CYBER TRADE WIN v2.1\n"
                f"Modo: {modo} | Nível: {nivel}\n"
                f"Contratos: {max_c} | Sniper: {'🎯 ON' if sniper else '📊 OFF'}\n"
                f"Custo: ${custo} ({pct}%) | {'⛔ PAUSADO' if pausado else '✅ ATIVO'}"
            )

        elif msg_upper in ("/NIVEL", "/CAPITAL"):
            try:
                from infrastructure.redis_state import RedisState
                from utils.capital_levels import CapitalLevelManager
                rs = RedisState()
                cap = rs.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
                mgr = CapitalLevelManager(rs, None, None)
                self._alertar(mgr.relatorio_capital(cap))
            except Exception as e:
                self._alertar(f"Erro /nivel: {e}")

        elif msg_upper == "/PAUSAR":
            self.r.set("sistema_pausado", "true")
            self._alertar("⛔ Sistema WIN PAUSADO via Telegram.")

        elif msg_upper == "/OPERAR":
            self.r.delete("sistema_pausado")
            self._alertar("✅ Sistema WIN RETOMADO via Telegram.")

    async def _loop_relatorio_diario(self):
        while True:
            agora = datetime.now()
            # ✅ CORRIGIDO: usa timedelta em vez de day+1 (evita erro no dia 31)
            alvo = agora.replace(hour=18, minute=0, second=0, microsecond=0)
            if agora >= alvo:
                alvo = alvo + timedelta(days=1)
            await asyncio.sleep((alvo - agora).total_seconds())
            await self._relatorio_diario()

    async def _relatorio_diario(self):
        try:
            trades    = int(self.r.get("trades_dia") or 0)
            ganhos    = int(self.r.get("ganhos_dia") or 0)
            perdas    = trades - ganhos
            res_dia   = float(self.r.get("resultado_dia_reais") or 0)
            custo     = float(self.r.get("custo_api_hoje") or 0)
            orcamento = float(os.getenv("DAILY_API_BUDGET_USD", "0.10"))
            sniper    = self.r.get("sniper_mode") == "true"
            nivel     = self.r.get("nome_nivel_capital") or "N/D"
            acerto    = ganhos / trades * 100 if trades > 0 else 0
            modo      = "🟡 PAPER" if PAPER_MODE else "🔴 REAL"

            try:
                from infrastructure.redis_state import RedisState
                from utils.capital_levels import get_nivel, progresso_para_proximo_marco
                rs = RedisState()
                cap = rs.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
                cap_ini = float(os.getenv("CAPITAL_INICIAL", "1000"))
                prog    = progresso_para_proximo_marco(cap)
                capital_info = f"💰 Capital: R${cap:,.2f} (+R${cap-cap_ini:,.2f})\n📈 Nível: {nivel}\n"
                if prog["proximo"]:
                    capital_info += f"🎯 Próximo: R${prog['proximo']:,.0f} (faltam R${prog['faltam']:,.2f})"
            except Exception:
                capital_info = f"Nível: {nivel}"

            self._alertar(
                f"📊 CYBER TRADE WIN v2.1 — {datetime.now().strftime('%d/%m/%Y')}\n"
                f"Modo: {modo} | Sniper: {'🎯 ON' if sniper else '📊 OFF'}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{capital_info}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Trades: {trades} | ✅ {ganhos} | ❌ {perdas}\n"
                f"Acerto: {acerto:.1f}% | Resultado: R${res_dia:+.2f}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 Custo: ${custo:.4f}/${orcamento:.2f} ({custo/orcamento*100:.0f}%)"
            )

            # Reset contadores diários
            for key in ["trades_dia", "ganhos_dia", "resultado_dia_reais",
                        "losses_consecutivos", "breakeven_ativado_n",
                        "trailing_ativado_n", "violinada_pendente"]:
                self.r.delete(key)
            self._custo_alerta_80_enviado = False

        except Exception as e:
            logger.error(f"Relatório diário WIN: {e}")

    def _alertar(self, msg: str):
        logger.info(f"[GUARD_WIN] {msg}")
        if self.tg:
            try:
                self.tg.alertar(msg)
            except Exception as e:
                logger.error(f"Telegram erro: {e}")


if __name__ == "__main__":
    guard = Guard()
    asyncio.run(guard.iniciar())
```

═══════════════════════════════════════════════════════════════
[19] main.py WIN (✅ Ciclo LEARN com controle de tempo corrigido)
═══════════════════════════════════════════════════════════════
```python
# main.py WIN
# CYBER TRADE WIN v2.1
# ✅ CORRIGIDO: ciclo LEARN com timestamp de controle (evita pular dias)

import asyncio, logging, os
from datetime import datetime, date, time as dtime
from dotenv import load_dotenv
load_dotenv()

from infrastructure.llm_router    import LLMRouter
from infrastructure.cost_monitor  import CostMonitor
from infrastructure.redis_state   import RedisState
from infrastructure.database      import Database
from infrastructure.telegram_bot  import TelegramBot
from infrastructure.profit_bridge import ProfitBridge
from agents.cyber_agent  import CyberAgent
from agents.exec_agent   import ExecAgent
from tape.tape_reader    import TapeReader
from utils.indicators    import calcular_todos
from utils.risk_manager  import RiskManager
from utils.cool_down     import CoolDown
from utils.capital_levels import CapitalLevelManager, get_nivel

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(name)-16s %(levelname)s %(message)s")
logger = logging.getLogger("main_win")

PAPER_MODE  = os.getenv("PAPER_MODE", "true").lower() == "true"
ATR_MIN_WIN = float(os.getenv("ATR_MINIMO", "200.0"))
HORARIO_FIM = dtime(17, 30)


class CyberTradeWIN:
    def __init__(self):
        self.tg           = TelegramBot()
        self.redis        = RedisState()
        self.db           = Database()
        self.profit       = ProfitBridge()
        self.tape         = TapeReader()
        self.risk         = RiskManager()
        self.cost_monitor = CostMonitor(alerta_callback=self.tg.alertar)
        self.router       = LLMRouter(cost_monitor=self.cost_monitor)
        self.cyber        = CyberAgent(router=self.router, redis_state=self.redis)
        self.exec         = ExecAgent(redis_state=self.redis, db=self.db,
                                      tg=self.tg, profit_bridge=self.profit)
        self.cool_down    = CoolDown(self.redis)
        self.capital_mgr  = CapitalLevelManager(self.redis, self.tg, self.db)
        # ✅ Controle de último ciclo LEARN
        self._learn_ultimo_dia: date | None = None

    async def iniciar(self):
        capital = self.redis.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
        nivel   = get_nivel(capital)
        self.capital_mgr.aplicar_nivel_ao_redis(nivel)

        modo   = "🟡 PAPER" if PAPER_MODE else "🔴 REAL"
        self.tg.alertar(
            f"✅ Cyber Trade WIN v2.1 | {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"Modo: {modo} | Capital: R${capital:,.2f}\n"
            f"Nível: {nivel['nome']} | Max contratos: {nivel['max_contratos']}\n"
            f"Símbolo: WINFUT | R$0,20/pt | Cutoff: 17:30 BRT"
        )

        await asyncio.gather(
            self._ciclo_trading(),
            self._ciclo_learn(),
            self._ciclo_telegram(),
        )

    async def _ciclo_trading(self):
        while True:
            hora = datetime.now().time()
            if hora < dtime(9, 15) or hora >= HORARIO_FIM:
                await asyncio.sleep(30); continue
            if dtime(12, 0) <= hora < dtime(13, 30):
                await asyncio.sleep(60); continue
            if self.redis.get_sistema_pausado():
                await asyncio.sleep(10); continue
            try:
                await self._candle()
            except RuntimeError as e:
                logger.error(str(e)); self.tg.alertar(f"⛔ {e}")
            except Exception as e:
                logger.exception(str(e))
            await asyncio.sleep(300)

    async def _candle(self):
        agora = datetime.now()
        t0    = asyncio.get_event_loop().time()

        if not self._pre_filtro():
            return

        dados = await self._coletar(agora)

        from agents.graph_agent   import GraphAgent
        from agents.flow_agent    import FlowAgent
        from agents.context_agent import ContextAgent
        graph_a   = GraphAgent(router=self.router)
        flow_a    = FlowAgent(router=self.router)
        context_a = ContextAgent(router=self.router)

        resultados = await asyncio.gather(
            graph_a.analisar(dados),
            flow_a.analisar(dados),
            context_a.analisar(dados),
            return_exceptions=True,
        )
        graph_r, flow_r, context_r = resultados
        for nome, res in [("ARCHITECT", graph_r), ("MORPHEUS", flow_r), ("ORACLE", context_r)]:
            if isinstance(res, Exception):
                logger.error(f"{nome} WIN erro: {res}"); return

        latencia = asyncio.get_event_loop().time() - t0
        preco    = float(self.redis.get("preco_atual_win") or 0)
        estado   = self._estado(agora, latencia, preco)

        decisao = await self.cyber.decidir(
            {"estado_sistema": estado, "graph": graph_r, "flow": flow_r, "context": context_r}
        )

        self.db.registrar_ciclo({
            "timestamp": agora.isoformat(), "decisao": decisao.get("decisao"),
            "score": decisao.get("score_final", 0), "motivo": decisao.get("motivo", "")[:300],
            "custo_api_usd": self.cost_monitor.total_usd,
            "graph_sinal": graph_r.get("sinal"),
            "flow_forca": flow_r.get("forca_fluxo", 0),
            "context_regime": context_r.get("regime_mercado"),
            "sniper_mode": estado.get("sniper_mode", False),
        })

        if decisao.get("decisao") == "ARMAR":
            await self.exec.armar(decisao)
            await self.capital_mgr.verificar_nivel()

        self.cool_down.verificar_e_ativar()
        logger.info(
            f"[WIN {agora.strftime('%H:%M')}] score={decisao.get('score_final', 0)} "
            f"| {decisao.get('decisao')} | R${self.redis.get_capital() or 0:,.2f}"
        )

    def _pre_filtro(self) -> bool:
        atr = float(self.redis.get("atr_atual_win") or ATR_MIN_WIN + 1)
        if atr < ATR_MIN_WIN: return False
        if self.cost_monitor.orcamento_esgotado: return False
        stop_day = float(self.redis.get("stop_day_pct_nivel") or 5.0)
        if self.redis.get_resultado_dia_pct() <= -stop_day: return False
        if self.redis.get_operacoes_hoje() >= int(os.getenv("MAX_OPERACOES_DIA", "5")): return False
        if self.redis.get_cool_down(): return False
        return True

    async def _coletar(self, agora: datetime) -> dict:
        loop = asyncio.get_event_loop()
        c5m  = await loop.run_in_executor(None, lambda: self.profit.get_candles("WINFUT", 5, 20))
        c15m = await loop.run_in_executor(None, lambda: self.profit.get_candles_15m("WINFUT", 10))
        book = await loop.run_in_executor(None, lambda: self.profit.get_book("WINFUT"))
        tape = await loop.run_in_executor(None, lambda: self.profit.get_tape("WINFUT", 50))
        preco = await loop.run_in_executor(None, self.profit.get_preco_atual)

        self.redis.set("preco_atual_win", str(preco))
        ind = calcular_todos(c5m, c15m)
        self.redis.set("atr_atual_win", str(ind.get("atr14_5m", 300.0)))

        from tape.tape_reader_polars import PolarsTapeEngineWIN
        engine = PolarsTapeEngineWIN()
        engine.add_ticks(tape)
        tm = engine.compute_metrics()  # ← grava em "tape_metricas"

        return {
            "symbol": "WINFUT", "timestamp": agora.isoformat(),
            "candles_5min": c5m, "candles_15min": c15m,
            "indicadores": ind,
            "estrutura": {
                "maxima_dia": max((c["high"] for c in c5m), default=0),
                "minima_dia": min((c["low"] for c in c5m), default=0),
                "suportes": [], "resistencias": [],
            },
            "book_atual": book,
            "tape_candle_completo": tape,
            "tape_metricas": tm,
            "sessao_americana": agora.hour >= 10,
            "minutos_desde_ny_open": max(0, (agora.hour * 60 + agora.minute) - (10 * 60 + 30)),
            "nivel_capital": self.redis.get("nome_nivel_capital") or "INICIANTE",
        }

    def _estado(self, agora, latencia, preco) -> dict:
        capital = self.redis.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
        return {
            "capital_atual": capital,
            "operacoes_hoje": self.redis.get_operacoes_hoje(),
            "losses_consecutivos": self.redis.get_losses_consecutivos(),
            "resultado_dia_percentual": self.redis.get_resultado_dia_pct(),
            "em_cool_down": self.redis.get_cool_down(),
            "equity_filter_10d": self.redis.get_equity_filter(),
            "modo": "PAPER" if PAPER_MODE else "REAL",
            "latencia_ciclo_segundos": round(latencia, 2),
            "deslocamento_preco_desde_analise": 0.0,
            "sniper_mode": self.redis.get_sniper_mode(),
            "score_minimo_ativo": int(self.redis.get("score_minimo_nivel") or 72),
            "stop_day_pct": float(self.redis.get("stop_day_pct_nivel") or 5.0),
            "max_contratos_nivel": int(self.redis.get("max_contratos_nivel") or 1),
            "stop_maximo_nivel": float(self.redis.get("stop_maximo_pts_nivel") or 50.0),
            "nome_nivel_capital": self.redis.get("nome_nivel_capital") or "INICIANTE",
            "custo_api_hoje_usd": self.cost_monitor.total_usd,
            "orcamento_restante_usd": self.cost_monitor.restante_usd,
        }

    async def _ciclo_learn(self):
        """
        ✅ CORRIGIDO: controle via timestamp para evitar pular dias ou executar múltiplas vezes.
        """
        from learn.learn_agent import LearnAgent
        learn = LearnAgent(router=self.router, db=self.db, tg=self.tg)
        while True:
            agora = datetime.now()
            hoje  = agora.date()
            # Executa uma vez por dia, entre 12:05 e 12:15
            if (agora.hour == 12 and 5 <= agora.minute <= 15
                    and self._learn_ultimo_dia != hoje):
                try:
                    logger.info("🏭 CYBERDYNE WIN: iniciando ciclo almoço")
                    await learn.ciclo_almoco()
                    self._learn_ultimo_dia = hoje
                    logger.info("🏭 CYBERDYNE WIN: ciclo almoço concluído")
                except Exception as e:
                    logger.error(f"CYBERDYNE WIN ciclo: {e}")
            await asyncio.sleep(30)

    async def _ciclo_telegram(self):
        """Loop de polling Telegram — apenas repassa para guard via Redis inbox."""
        while True:
            await asyncio.sleep(5)
            try:
                for msg in self.tg.obter_mensagens():
                    # Repassa para guard processar (evita duplicação)
                    self.redis.rpush("telegram_inbox", msg)
            except Exception as e:
                logger.error(f"Telegram WIN polling: {e}")


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())
```

═══════════════════════════════════════════════════════════════
[20] CHECKLIST_WIN.md
═══════════════════════════════════════════════════════════════
```markdown
# CYBER TRADE WIN v2.1 — CHECKLIST DE DEPLOY

# ── CORREÇÕES v2.1 — VERIFICAR OBRIGATÓRIO ───────────────────────────
[ ] cyber_agent.py: linha _stop_maximo_atual() presente e completa
[ ] tape_reader_polars.py: chave "tape_metricas" (não "tape_metrics_win")
[ ] openclaw_win.json: score_pesos somam 1.00 (graph 0.35+flow 0.30+context 0.30+timing 0.05)
[ ] oracle_skill.md: alerta_finalizacao >= 17:15 (não >= 15:45)
[ ] guard.py: usa timedelta(days=1) para relatorio_diario (não day+1)
[ ] llm_router.py: model "claude-sonnet-4-6" (não claude-sonnet-4-20250514)
[ ] cost_monitor.py: flag _alerta_80_enviado separada de _alerta_100_enviado

# ── BLOCO 1: INFRAESTRUTURA ──────────────────────────────────────────
[ ] Python 3.11+ instalado
[ ] pip install -r requirements.txt sem erros
[ ] .env criado do .env.template e preenchido
[ ] GOOGLE_AI_API_KEY válida e com quota disponível
[ ] Redis: redis-cli ping → PONG
[ ] Telegram Bot testado: /start responde
[ ] OpenClaw Gateway rodando: curl localhost:3000/health
[ ] guard.py iniciado ANTES do main.py
[ ] /status no Telegram → Nível INICIANTE, contratos=1

# ── BLOCO 2: SISTEMA DE NÍVEIS ───────────────────────────────────────
[ ] capital_levels.py importa sem erros
[ ] aplicar_nivel_ao_redis() gravando no Redis
[ ] Simular capital=2500 → Nível 2 (max 2 contratos)
[ ] Simular capital=5500 → Nível 4 (max 4 contratos)
[ ] Alerta de marco Telegram disparando
[ ] Stop-day adaptativo lido do Redis por CyberAgent

# ── BLOCO 3: CÁLCULOS WIN ────────────────────────────────────────────
[ ] VALOR_PONTO_WIN=0.20 em TODOS os módulos
[ ] resultado_reais = pts * 0.20 * contratos (NÃO pts * 5.0)
[ ] Exemplo: +200pts × 0.20 × 1 contrato = +R$40,00 ✓
[ ] sizing: R$10 risco ÷ (50pts × 0.20) = 1 contrato ✓ (Nível 1)
[ ] Nível 1: stop máximo 50pts hard cap funcionando

# ── BLOCO 4: TAPE E REDIS ────────────────────────────────────────────
[ ] tape_reader_polars.py grava em "tape_metricas"
[ ] exec_agent.py lê de "tape_metricas" ← CHAVE IDÊNTICA
[ ] Polars compute_metrics: sintaxe when/then/otherwise
[ ] tape_metricas expira em 60s (stale data protection)

# ── BLOCO 5: PAPER TRADING (mín 50 trades) ───────────────────────────
[ ] Símbolo: WINFUT (não WDOFUT)
[ ] ATR mínimo 200pts respeitado
[ ] ORACLE analisa SP500/VIX (não DXY como driver primário)
[ ] ORACLE alerta_finalizacao ativado às 17:15 (não 15:45)
[ ] Fechamento forçado às 17:30 BRT (não 16:00)
[ ] Capital sendo atualizado após cada trade
[ ] Projeções de nível atualizando

# ── BLOCO 6: TRANSIÇÃO PARA PRODUÇÃO ────────────────────────────────
[ ] PAPER_MODE=false
[ ] ANTHROPIC_API_KEY válida e com crédito
[ ] Confirmar CYBER usa claude-sonnet-4-6
[ ] Capital real: R$1.000 exato
[ ] Contratos = 1 (Nível 1 hard lock)
[ ] Kill switch manual no Profit Pro testado
[ ] Margem mínima conta: ~R$150-200 (margem WIN + buffer)

# ── MARCOS E METAS ────────────────────────────────────────────────────
R$1.000 → R$2.000 (+100%): max 2 contratos | stop-day 4%
R$2.000 → R$3.000 (+50%): max 3 contratos | stop-day 3.5%
R$3.000 → R$5.000 (+67%): max 4 contratos | ★ META INICIAL
R$5.000 → R$7.000 (+40%): max 5 contratos
R$7.000 → R$10.000 (+43%): ★ MATURIDADE plena
```

---
> **"O tape é a verdade. O gráfico é o resumo. O nível de capital é a disciplina."**
> **"R$0,20 por ponto. Não R$5,00. Nunca esquecer isso."**
> **"Risco 1%. Stop-day adaptativo. Sizing WIN. Paper primeiro. Mercado decide depois do cutoff."**

**FIM — Cyber Trade WIN v2.1 | Deploy-ready com 11 bugs corrigidos | Abril 2026**
