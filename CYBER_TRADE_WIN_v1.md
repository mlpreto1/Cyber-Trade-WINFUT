# CYBER TRADE WIN v1.0 — BUNDLE COMPLETO PARA DEPLOY
> Adaptado do CYBER TRADE v5.2 (WDO) para **Mini Índice Futuro (WIN/WINFUT)**
> Capital Inicial: R$1.000 | Meta: R$5.000 | Máx: 5 contratos
> Gatilhos automáticos em: R$1K → R$2K → R$3K → R$5K → R$7K → R$10K

---

## ⚠️ DIFERENÇAS CRÍTICAS WIN vs WDO (LER ANTES DE TUDO)

| Item | WDO (Mini Dólar) | WIN (Mini Índice) |
|------|-----------------|-------------------|
| Símbolo | WDOFUT | WINFUT |
| Valor do ponto | R$5,00/pt/contrato | **R$0,20/pt/contrato** |
| Tick mínimo | 0,5 ponto | **5 pontos** |
| Preço típico | ~5.800 pts | **~130.000–135.000 pts** |
| ATR 5min típico | 5–30 pts | **200–800 pts** |
| ATR diário típico | 20–80 pts | **1.500–5.000 pts** |
| Driver macro principal | DXY / Ptax | **S&P500 / IBOV / Vale / Petro** |
| Margem intraday (~) | R$200/contrato | **R$80–150/contrato** |
| Stop mínimo razoável | 5–15 pts | **80–300 pts** |
| Horário | 09:00–16:55 | **09:00–17:55 BRT** |

---

## SISTEMA DE NÍVEIS DE CAPITAL (GATILHOS AUTOMÁTICOS)

```
NÍVEL 1 │ R$1.000 – R$1.999 │ Máx 1 contrato │ Score ≥ 72 │ Stop-day -5%
NÍVEL 2 │ R$2.000 – R$2.999 │ Máx 2 contratos │ Score ≥ 70 │ Stop-day -4%
NÍVEL 3 │ R$3.000 – R$4.999 │ Máx 3 contratos │ Score ≥ 68 │ Stop-day -3.5%
NÍVEL 4 │ R$5.000 – R$6.999 │ Máx 4 contratos │ Score ≥ 65 │ Stop-day -2.5%  ★ META
NÍVEL 5 │ R$7.000 – R$9.999 │ Máx 5 contratos │ Score ≥ 65 │ Stop-day -2.5%
NÍVEL 6 │ R$10.000+          │ Máx 5 contratos │ Score ≥ 65 │ Stop-day -2.5%  ★ MATURIDADE
```

**Regra de reinvestimento:** 100% dos lucros reinvestidos até atingir R$5.000.
Após R$5.000, o operador decide sobre saques. O sistema continua compoundando.

---

## INSTRUÇÕES DE DEPLOY

```bash
# 1. Criar estrutura
mkdir cyber_trade_win && cd cyber_trade_win

# 2. Copiar cada arquivo da seção correspondente abaixo

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
cp .env.template .env
# Editar .env com suas chaves de API

# 5. Iniciar Redis
redis-server &

# 6. Iniciar sistema (dois terminais)
python guard.py    # Terminal 1 — PRIMEIRO
python main.py     # Terminal 2
```

---

---
## `CLAUDE.md`

```markdown
# CYBER TRADE WIN v1.0 — CLAUDE CODE PROJECT

## CONTEXTO DO PROJETO

Sistema de trading algorítmico para WIN (Mini Índice Futuro B3), operando scalping
em candles de 5 minutos com 7 agentes de IA. Mercado: B3, contrato WINFUT, horário 09:15–17:30 BRT.

**ATENÇÃO: Valor do ponto WIN = R$0,20 por contrato (NÃO R$5,00 como o WDO)**

**Stack:**
- Python 3.11+, asyncio, Redis, SQLite, Telegram Bot
- LLMs: Gemma 4 (Google AI Studio) + Claude Sonnet 4.6 (Anthropic)
- Dados: ProfitDLL (Nelogica Profit Pro) via bridge Python

**Capital inicial: R$1.000 | Meta: R$5.000 | Limite: 5 contratos**
**Regra de ouro: PAPER_MODE=true sempre, até validação completa.**

---

## SISTEMA DE NÍVEIS — GATILHOS AUTOMÁTICOS

| Nível | Capital | Max Contratos | Score Min | Stop-Day |
|-------|---------|---------------|-----------|----------|
| 1 | R$1.000 | 1 | 72 | -5% |
| 2 | R$2.000 | 2 | 70 | -4% |
| 3 | R$3.000 | 3 | 68 | -3.5% |
| 4 | R$5.000 | 4 | 65 | -2.5% ★ |
| 5 | R$7.000 | 5 | 65 | -2.5% |
| 6 | R$10.000 | 5 | 65 | -2.5% |

Gatilho automático: ao cruzar R$2K, R$3K, R$5K, R$7K e R$10K, o sistema:
1. Notifica via Telegram
2. Atualiza max_contratos no Redis
3. Ajusta score_minimo dinamicamente
4. Registra marco no SQLite

---

## ARQUITETURA — 7 AGENTES + LEARN

| Agente | Função | Paper | Produção |
|--------|---------|-------|----------|
| GRAPH | Análise técnica 5m+15m WIN | Gemma 4 31B | Gemma 4 31B |
| FLOW | Fluxo + Tape + CVD + Iceberg | Gemma 4 31B | Gemma 4 31B |
| CONTEXT | Macro S&P500 + IBOV + DI1F | Gemma 4 E4B | Gemma 4 E4B |
| CYBER | Orquestrador + Decisão final | Gemma 4 31B | Claude Sonnet 4.6 |
| EXEC | Execução de ordens | Python puro | Python puro |
| GUARD | Watchdog + Níveis de Capital | Python puro | Python puro |
| LEARN | Otimizador + Pesquisador | Gemma 4 26B | Claude Sonnet 4.6 |

---

## FLUXO POR CANDLE (5min) — WIN

FASE 1: Pré-filtro local (ATR_WIN, horário, cool-down, stop-day, nível capital)
FASE 2: Coleta → ProfitDLL (candles WIN, book, tape)
FASE 3: asyncio.gather → GRAPH + FLOW + CONTEXT em paralelo (~3-4s)
FASE 4: CYBER recebe os 3 JSONs → 7 passos → CANCELAR | AGUARDAR | ARMAR
FASE 5: Se ARMAR → EXEC monitora gatilho via tape_reader
FASE 6: Gatilho ativado → ordem → monitoramento (break-even + trailing ATR_WIN)
FASE 7: GUARD verifica níveis de capital a cada trade fechado

---

## GESTÃO DE RISCO — PARÂMETROS WIN

```
Valor do ponto WIN   : R$0,20/pt/contrato (IMUTÁVEL)
Risco por trade      : 1,0% do capital (NUNCA alterável pelo LEARN)
Stop-day adaptativo  : ver tabela de níveis (NUNCA alterável)
Max contratos        : 5 (limite absoluto, aumenta por nível)
Max trades/dia       : 5
Cool-down            : 3 losses → 30 min pausa
Stop > 2×ATR_WIN     : NUNCA permitido
R:R < 1,5            : NUNCA autorizar
ATR mínimo WIN       : 200 pontos (mercado morto = ignorar)
Posição às 17:30     : FECHAR (EXEC fecha automaticamente)
```

---

## CÁLCULO DE RESULTADO WIN

```python
# CORRETO para WIN:
resultado_pts   = preco_saida - preco_entrada  # em pontos do índice
resultado_reais = resultado_pts * 0.20 * contratos

# Exemplos:
# +200 pts × 0.20 × 1 contrato = +R$40,00
# +200 pts × 0.20 × 3 contratos = +R$120,00
# -150 pts × 0.20 × 1 contrato = -R$30,00
```

---

## DIFERENÇAS PRINCIPAIS vs WDO

1. **Context Agent**: Analisa S&P500, IBOV, Vale, Petrobras, VIX — NÃO mais DXY/Ptax
2. **Point value**: 0.20 (não 5.00) — afeta TODOS os cálculos financeiros
3. **ATR scale**: Mínimo 200 pts (vs 3 pts no WDO)
4. **Preço base simulado**: 132.500 (vs 5.860 WDO)
5. **Horário**: até 17:30 BRT (WIN fecha mais tarde)
6. **Níveis de capital**: Auto-trigger a cada marco de capital
7. **Ptax**: REMOVIDA (não relevante para índice)

---

## COMANDOS TELEGRAM (WIN)

```
SNIPER ON          → ativa Sniper Mode (score mínimo 80)
SNIPER OFF         → desativa Sniper Mode
/status            → status + nível de capital atual
/nivel             → detalhes do nível de capital e progresso
/capital           → extrato do capital com PnL acumulado
/pausar            → pausa ciclos manualmente
/operar            → retoma ciclos
LEARN, analise ... → comando manual para LEARN
APROVO #N          → aprova proposta N do LEARN
REJEITO #N         → rejeita proposta N do LEARN
```
```

---
## `.env.template`

```text
# ══════════════════════════════════════════════════════════════
# CYBER TRADE WIN v1.0 — CONFIGURAÇÃO DE AMBIENTE
# ══════════════════════════════════════════════════════════════
# ⚠️  NUNCA versionar este arquivo.
# ⚠️  Capital inicial: R$1.000. Não alterar PAPER_MODE sem checklist.

# ──────────────────────────────────────────────────────────────
# 🔑 APIS
# ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-api03-SUBSTITUA_AQUI
GOOGLE_AI_API_KEY=AI_SUBSTITUA_AQUI

# ──────────────────────────────────────────────────────────────
# 🤖 MODO DE OPERAÇÃO
# ──────────────────────────────────────────────────────────────
PAPER_MODE=true

# ──────────────────────────────────────────────────────────────
# 💰 CONTROLE DE CUSTOS
# ──────────────────────────────────────────────────────────────
DAILY_API_BUDGET_USD=0.10
COST_ALERT_THRESHOLD_PCT=80
COST_LOG_PATH=./logs/cost_today.json

# ──────────────────────────────────────────────────────────────
# 📡 TELEGRAM
# ──────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=123456789:AAH_SUBSTITUA_AQUI
TELEGRAM_CHAT_ID=-1001234567890

# ──────────────────────────────────────────────────────────────
# 📊 GOOGLE SHEETS (opcional)
# ──────────────────────────────────────────────────────────────
GOOGLE_SHEETS_CREDENTIALS=./credentials.json
GOOGLE_SHEETS_ID=SUBSTITUA_ID_DA_PLANILHA

# ──────────────────────────────────────────────────────────────
# 🗄️ BANCO DE DADOS / REDIS
# ──────────────────────────────────────────────────────────────
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

DB_PATH=./cyber_trade_win.db
MEMORY_DB_PATH=./learn_memory_win.db
OPENCLAW_JSON_PATH=./openclaw_win.json

# ──────────────────────────────────────────────────────────────
# 💼 CAPITAL E RISCO — WIN
# ──────────────────────────────────────────────────────────────

# Capital inicial — R$1.000 para WIN
CAPITAL_INICIAL=1000.00

# Valor do ponto WIN — NÃO ALTERAR
VALOR_PONTO_WIN=0.20

# Preço base para simulação (WIN ≈ 132.500 pontos em 2025/26)
PRECO_BASE_SIMULADO=132500.0

# ──────────────────────────────────────────────────────────────
# 📊 PARÂMETROS WIN — RISCO
# ──────────────────────────────────────────────────────────────

# RISCO POR TRADE (% do capital) — NUNCA alterar pelo LEARN
RISCO_POR_TRADE_PCT=1.0

# Stop-day é ADAPTATIVO por nível — gerenciado pelo capital_levels.py
# Não editar estas variáveis manualmente — o sistema as atualiza via Redis
STOP_DAY_PCT=5.0         # Nível 1 (será atualizado dinamicamente)

# Máximo de operações por dia
MAX_OPERACOES_DIA=5

# ATR mínimo WIN em pontos (mercado morto = não operar)
ATR_MINIMO=200.0

# Contratos — gerenciado por capital_levels.py (começa em 1, max 5)
MAX_CONTRATOS_NORMAL=1   # Será atualizado dinamicamente pelo nível

# Sniper Mode
SNIPER_SCORE_MIN=80
SNIPER_MAX_CONTRATOS=2   # No Sniper, máx 2 (conservador)
SNIPER_SLIPPAGE_MAX=10.0 # Em pontos WIN

# Score e R:R
SCORE_MIN_NORMAL=72      # Nível 1 (atualizado dinamicamente)
SLIPPAGE_MAX_PTS=10.0    # Em pontos WIN
RR_MINIMO=1.5
LATENCIA_MAX_S=5.0
DESLOCAMENTO_MAX_PTS=50.0 # Em pontos WIN (equivalente a 1.5 pts WDO)

# Break-even e trailing — em pontos WIN
BREAKEVEN_PTS=80.0       # ≈ R$16 por contrato
TRAILING_FLOOR_PTS=100.0 # ≈ R$20 por contrato
TRAILING_ATR_MIN=3

# Cool-down
COOL_DOWN_LOSSES=3
COOL_DOWN_MINUTOS=30

# ──────────────────────────────────────────────────────────────
# 🔧 SISTEMA
# ──────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
```

---
## `openclaw_win.json`

```json
{
  "version": "WIN-1.0",
  "description": "Cyber Trade WIN v1.0 — Mini Índice Futuro B3 | Capital R$1.000 → R$5.000",
  "gateway": "localhost:3000",
  "contrato": "WINFUT",
  "valor_ponto": 0.20,
  "tick_minimo": 5,

  "llm_routing": {
    "paper_mode_env": "PAPER_MODE",
    "modelos": {
      "paper": {
        "graph":   "gemma-4-31b-it",
        "flow":    "gemma-4-31b-it",
        "context": "gemma-4-e4b-it",
        "cyber":   "gemma-4-31b-it",
        "learn":   "gemma-4-26b-a4b-it"
      },
      "producao": {
        "graph":   "gemma-4-31b-it",
        "flow":    "gemma-4-31b-it",
        "context": "gemma-4-e4b-it",
        "cyber":   "claude-sonnet-4-6",
        "learn":   "claude-sonnet-4-6"
      }
    }
  },

  "cost_monitor": {
    "orcamento_diario_usd_paper": 0.10,
    "orcamento_diario_usd_producao": 2.00,
    "alert_threshold_pct": 80,
    "throttle_agentes_secundarios": ["graph", "flow", "context"],
    "custo_maximo_por_chamada_usd": 0.50,
    "tokens_input_alerta": 5000
  },

  "capital_levels": {
    "descricao": "Gatilhos automáticos de evolução de capital",
    "reinvestir_ate": 5000.0,
    "niveis": [
      {
        "nivel": 1,
        "nome": "INICIANTE",
        "emoji": "🌱",
        "capital_min": 1000.0,
        "capital_max": 1999.99,
        "max_contratos": 1,
        "max_contratos_sniper": 1,
        "score_minimo": 72,
        "score_sniper": 85,
        "stop_day_pct": 5.0,
        "nota": "Ultra-conservador. 1 contrato fixo. Foco em aprender o sistema."
      },
      {
        "nivel": 2,
        "nome": "CRESCIMENTO_1",
        "emoji": "📈",
        "capital_min": 2000.0,
        "capital_max": 2999.99,
        "max_contratos": 2,
        "max_contratos_sniper": 1,
        "score_minimo": 70,
        "score_sniper": 83,
        "stop_day_pct": 4.0,
        "nota": "Primeiro aumento. Sniper ainda limitado a 1 contrato."
      },
      {
        "nivel": 3,
        "nome": "CRESCIMENTO_2",
        "emoji": "🚀",
        "capital_min": 3000.0,
        "capital_max": 4999.99,
        "max_contratos": 3,
        "max_contratos_sniper": 2,
        "score_minimo": 68,
        "score_sniper": 81,
        "stop_day_pct": 3.5,
        "nota": "Progressão consolidada. Score um pouco mais relaxado."
      },
      {
        "nivel": 4,
        "nome": "META_INICIAL",
        "emoji": "💰",
        "capital_min": 5000.0,
        "capital_max": 6999.99,
        "max_contratos": 4,
        "max_contratos_sniper": 2,
        "score_minimo": 65,
        "score_sniper": 80,
        "stop_day_pct": 2.5,
        "nota": "META ATINGIDA! Modo padrão ativado. Stop-day normalizado."
      },
      {
        "nivel": 5,
        "nome": "ESCALA_PLENA",
        "emoji": "🏆",
        "capital_min": 7000.0,
        "capital_max": 9999.99,
        "max_contratos": 5,
        "max_contratos_sniper": 3,
        "score_minimo": 65,
        "score_sniper": 80,
        "stop_day_pct": 2.5,
        "nota": "Escala máxima atingida. Todos os 5 contratos disponíveis."
      },
      {
        "nivel": 6,
        "nome": "MATURIDADE",
        "emoji": "⭐",
        "capital_min": 10000.0,
        "capital_max": 999999.0,
        "max_contratos": 5,
        "max_contratos_sniper": 3,
        "score_minimo": 65,
        "score_sniper": 80,
        "stop_day_pct": 2.5,
        "nota": "Plena maturidade. LEARN foca em otimização fina."
      }
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
    "breakeven_pts": 80.0,
    "trailing_floor_pts": 100.0
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
    "tps_exaustao_mult": 4.0,
    "tps_colapso_thresh": 1.0,
    "sweep_niveis_min": 3,
    "sweep_vol_base": 50,
    "sweep_ms_max": 3000,
    "spoof_vol_min": 100,
    "spoof_ms_max": 2000,
    "cvd_limiar_divergencia": 200,
    "nota_win": "Volumes menores que WDO, mas padrões similares"
  },

  "horarios": {
    "inicio": "09:00",
    "fim": "17:55",
    "operacao_fim": "17:30",
    "proibidos": [
      {"nome": "Abertura",          "inicio": "09:00", "fim": "09:15"},
      {"nome": "Almoço",            "inicio": "12:00", "fim": "13:30"},
      {"nome": "Pré-fechamento",    "inicio": "17:30", "fim": "17:55"}
    ],
    "ny_open_pausa_min": 3,
    "ny_open_limite_min": 15,
    "ptax_relevante": false,
    "nota": "WIN fecha às 17:55 mas operamos até 17:30. Sem Ptax relevante."
  },

  "sessoes": {
    "ABERTURA":      {"inicio": "09:00", "fim": "09:15", "qualidade": "PROIBIDO",  "fator": 0.0},
    "MANHA_INICIAL": {"inicio": "09:15", "fim": "10:30", "qualidade": "MODERADA",  "fator": 0.85},
    "NY_TRANSICAO":  {"inicio": "10:30", "fim": "10:48", "qualidade": "CAUTELA",   "fator": 0.75},
    "MANHA_ATIVA":   {"inicio": "10:48", "fim": "12:00", "qualidade": "EXCELENTE", "fator": 1.00},
    "ALMOCO":        {"inicio": "12:00", "fim": "13:30", "qualidade": "PROIBIDO",  "fator": 0.0},
    "TARDE_INICIAL": {"inicio": "13:30", "fim": "14:15", "qualidade": "MODERADA",  "fator": 0.80},
    "TARDE_ATIVA":   {"inicio": "14:15", "fim": "16:30", "qualidade": "BOA",       "fator": 0.90},
    "TARDE_FINAL":   {"inicio": "16:30", "fim": "17:30", "qualidade": "MODERADA",  "fator": 0.60},
    "PRE_FECHAMENTO":{"inicio": "17:30", "fim": "17:55", "qualidade": "PROIBIDO",  "fator": 0.0}
  },

  "score_pesos": {
    "graph":   0.35,
    "flow":    0.30,
    "context": 0.20,
    "timing":  0.05
  },

  "score_ajustes": {
    "iceberg_detectado":          +10,
    "held_confirmacao_dupla":     +7,
    "absorcao":                   +5,
    "delta_candle_alto":          +5,
    "sweep_massivo":              +5,
    "regime_coerente":            +5,
    "sp500_alinhado":             +5,
    "ibov_alinhado":              +5,
    "rompimento_fraco":           -5,
    "divergencia_delta_preco":    -10,
    "volume_relativo_baixo":      -10,
    "divergencia_win_sp500":      -10,
    "desalinhamento_timeframes":  -10,
    "sp500_contra":               -10,
    "vix_alto":                   -10,
    "spoof_detectado":            -15
  },

  "learn_changes": []
}
```

---
## `utils/capital_levels.py`

```python
"""
CYBER TRADE WIN v1.0 — CAPITAL LEVELS
========================================
Gerencia os gatilhos automáticos de evolução de capital.

Ao cruzar os marcos: R$1K, R$2K, R$3K, R$5K, R$7K, R$10K
o sistema automaticamente:
  1. Ajusta max_contratos no Redis
  2. Ajusta score_minimo no Redis
  3. Ajusta stop_day_pct no Redis
  4. Envia alerta comemorativo via Telegram
  5. Registra o marco no SQLite

Integração:
  - guard.py chama verificar_nivel() após cada trade fechado
  - cyber_agent.py lê max_contratos do Redis (via redis_state)
  - exec_agent.py usa max_contratos atual para sizing
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("capital_levels")

# ─── Tabela de Níveis ────────────────────────────────────────────────────────

NIVEIS = [
    {
        "nivel": 1, "nome": "INICIANTE", "emoji": "🌱",
        "capital_min": 1000.0, "capital_max": 1999.99,
        "max_contratos": 1, "max_contratos_sniper": 1,
        "score_minimo": 72, "score_sniper": 85,
        "stop_day_pct": 5.0,
        "nota": "Ultra-conservador. 1 contrato. Aprenda o sistema."
    },
    {
        "nivel": 2, "nome": "CRESCIMENTO_1", "emoji": "📈",
        "capital_min": 2000.0, "capital_max": 2999.99,
        "max_contratos": 2, "max_contratos_sniper": 1,
        "score_minimo": 70, "score_sniper": 83,
        "stop_day_pct": 4.0,
        "nota": "Primeiro upgrade. Adicione rigor na seleção."
    },
    {
        "nivel": 3, "nome": "CRESCIMENTO_2", "emoji": "🚀",
        "capital_min": 3000.0, "capital_max": 4999.99,
        "max_contratos": 3, "max_contratos_sniper": 2,
        "score_minimo": 68, "score_sniper": 81,
        "stop_day_pct": 3.5,
        "nota": "Consistência comprovada. Ajuste fino."
    },
    {
        "nivel": 4, "nome": "META_INICIAL", "emoji": "💰",
        "capital_min": 5000.0, "capital_max": 6999.99,
        "max_contratos": 4, "max_contratos_sniper": 2,
        "score_minimo": 65, "score_sniper": 80,
        "stop_day_pct": 2.5,
        "nota": "META R$5.000 ATINGIDA! Modo produção pleno."
    },
    {
        "nivel": 5, "nome": "ESCALA_PLENA", "emoji": "🏆",
        "capital_min": 7000.0, "capital_max": 9999.99,
        "max_contratos": 5, "max_contratos_sniper": 3,
        "score_minimo": 65, "score_sniper": 80,
        "stop_day_pct": 2.5,
        "nota": "Escala máxima. Todos os 5 contratos disponíveis."
    },
    {
        "nivel": 6, "nome": "MATURIDADE", "emoji": "⭐",
        "capital_min": 10000.0, "capital_max": float("inf"),
        "max_contratos": 5, "max_contratos_sniper": 3,
        "score_minimo": 65, "score_sniper": 80,
        "stop_day_pct": 2.5,
        "nota": "R$10.000 conquistados. LEARN foca em otimização fina."
    },
]

MARCOS_TELEGRAM = [1000, 2000, 3000, 5000, 7000, 10000]


def get_nivel(capital: float) -> dict:
    """Retorna o nível atual baseado no capital."""
    for n in reversed(NIVEIS):
        if capital >= n["capital_min"]:
            return n
    return NIVEIS[0]  # fallback para nível 1


def proximo_marco(capital: float) -> Optional[float]:
    """Retorna o próximo marco de capital."""
    for marco in MARCOS_TELEGRAM:
        if capital < marco:
            return float(marco)
    return None


def progresso_para_proximo_marco(capital: float) -> dict:
    """Calcula progresso percentual para o próximo marco."""
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


class CapitalLevelManager:
    """
    Gerencia transições de nível de capital.
    
    Uso no guard.py:
        mgr = CapitalLevelManager(redis_state, tg, db)
        await mgr.verificar_nivel()
    """

    def __init__(self, redis_state, tg, db):
        self.redis = redis_state
        self.tg    = tg
        self.db    = db
        self._nivel_anterior = None

    def _nivel_salvo(self) -> int:
        try:
            v = self.redis.get("nivel_capital_atual")
            return int(v) if v else 0
        except Exception:
            return 0

    def _salvar_nivel(self, nivel: int):
        self.redis.set("nivel_capital_atual", str(nivel))

    def aplicar_nivel_ao_redis(self, nivel_dict: dict):
        """Escreve os parâmetros do nível no Redis para leitura pelos agentes."""
        sniper = self.redis.get_sniper_mode()
        max_c  = nivel_dict["max_contratos_sniper"] if sniper else nivel_dict["max_contratos"]
        self.redis.set("max_contratos_nivel",    str(nivel_dict["max_contratos"]))
        self.redis.set("max_contratos_efetivo",  str(max_c))
        self.redis.set("score_minimo_nivel",     str(nivel_dict["score_minimo"]))
        self.redis.set("stop_day_pct_nivel",     str(nivel_dict["stop_day_pct"]))
        self.redis.set("nome_nivel_capital",     nivel_dict["nome"])

    async def verificar_nivel(self):
        """
        Chamado após cada trade fechado.
        Verifica se houve mudança de nível e notifica.
        """
        capital = self.redis.get_capital()
        if capital is None:
            capital = float(os.getenv("CAPITAL_INICIAL", "1000"))

        nivel_atual = get_nivel(capital)
        nivel_salvo = self._nivel_salvo()

        # Sempre aplicar (garante consistência após restart)
        self.aplicar_nivel_ao_redis(nivel_atual)

        if nivel_atual["nivel"] != nivel_salvo:
            # TRANSIÇÃO DE NÍVEL DETECTADA
            subiu = nivel_atual["nivel"] > nivel_salvo
            self._salvar_nivel(nivel_atual["nivel"])
            await self._alertar_transicao(capital, nivel_atual, subiu)
        
        # Verificar marcos especiais
        await self._checar_marcos(capital)

    async def _alertar_transicao(self, capital: float, nivel: dict, subiu: bool):
        """Envia alerta comemorativo (ou de alerta) no Telegram."""
        prog = progresso_para_proximo_marco(capital)
        seta = "🆙" if subiu else "🔽"

        if subiu:
            msg = (
                f"{nivel['emoji']} NOVO NÍVEL ATINGIDO! {seta}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Nível {nivel['nivel']}: {nivel['nome']}\n"
                f"Capital: R${capital:,.2f}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ Max contratos: {nivel['max_contratos']}\n"
                f"✅ Score mínimo: {nivel['score_minimo']}\n"
                f"✅ Stop-day: {nivel['stop_day_pct']:.1f}%\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 {nivel['nota']}\n"
            )
            if prog["proximo"]:
                msg += f"\nPróximo marco: R${prog['proximo']:,.0f} (faltam R${prog['faltam']:,.2f})"
        else:
            msg = (
                f"⚠️ CAPITAL CAIU DE NÍVEL\n"
                f"Nível {nivel['nivel']}: {nivel['nome']}\n"
                f"Capital: R${capital:,.2f}\n"
                f"Max contratos reduzido para: {nivel['max_contratos']}\n"
                f"Stop-day ajustado para: {nivel['stop_day_pct']:.1f}%\n"
                f"💡 Mantenha disciplina. O LEARN vai analisar."
            )

        logger.info(f"[CAPITAL_LEVELS] Transição → {nivel['nome']}")
        if self.tg:
            self.tg.alertar(msg)

        # Registrar no banco
        if self.db:
            try:
                self.db.registrar_ciclo({
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                    "decisao": f"NIVEL_{nivel['nivel']}_{nivel['nome']}",
                    "score": nivel["nivel"],
                    "motivo": f"Capital R${capital:.2f} → Nível {nivel['nivel']}",
                    "custo_api_usd": 0,
                    "graph_sinal": None,
                    "flow_forca": 0,
                    "context_regime": None,
                    "sniper_mode": False,
                })
            except Exception as e:
                logger.error(f"Erro ao registrar transição: {e}")

    async def _checar_marcos(self, capital: float):
        """Alerta quando capital cruza um marco pela primeira vez."""
        marcos_atingidos_str = self.redis.get("marcos_capital_atingidos") or "[]"
        try:
            atingidos = json.loads(marcos_atingidos_str)
        except Exception:
            atingidos = []

        for marco in MARCOS_TELEGRAM:
            if capital >= marco and marco not in atingidos:
                atingidos.append(marco)
                self.redis.set("marcos_capital_atingidos", json.dumps(atingidos))
                
                # Marco especial — R$5.000 é o mais importante
                if marco == 5000:
                    msg = (
                        f"🎉🎉🎉 META R$5.000 ATINGIDA! 🎉🎉🎉\n"
                        f"Capital atual: R${capital:,.2f}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Parabéns! Você quintuplicou o capital inicial.\n"
                        f"A partir de agora você pode:\n"
                        f"  ✅ Continuar reinvestindo (recomendado)\n"
                        f"  ✅ Sacar parte dos lucros\n"
                        f"  ✅ Ativar modo Sniper para setups premium\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Max contratos agora: 4 | Stop-day: 2.5%"
                    )
                elif marco == 10000:
                    msg = (
                        f"⭐ R$10.000 CONQUISTADOS! ⭐\n"
                        f"Capital: R${capital:,.2f}\n"
                        f"Nível MATURIDADE ativo — 5 contratos disponíveis.\n"
                        f"O LEARN vai sugerir otimizações avançadas."
                    )
                else:
                    msg = (
                        f"✨ Marco R${marco:,} atingido!\n"
                        f"Capital atual: R${capital:,.2f}\n"
                        f"Continue assim!"
                    )
                
                logger.info(f"[CAPITAL_LEVELS] Marco R${marco:,} atingido!")
                if self.tg:
                    self.tg.alertar(msg)

    def relatorio_capital(self, capital: float) -> str:
        """Relatório formatado do nível de capital para /capital ou /nivel."""
        nivel = get_nivel(capital)
        prog  = progresso_para_proximo_marco(capital)
        capital_inicial = float(os.getenv("CAPITAL_INICIAL", "1000"))
        ganho_total = capital - capital_inicial
        pct_ganho   = ganho_total / capital_inicial * 100

        barra_n = int(prog["pct"] / 5)  # barra de 20 blocos
        barra   = "█" * barra_n + "░" * (20 - barra_n)

        msg = (
            f"{nivel['emoji']} NÍVEL {nivel['nivel']}: {nivel['nome']}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Capital:    R${capital:>10,.2f}\n"
            f"Início:     R${capital_inicial:>10,.2f}\n"
            f"Ganho:      R${ganho_total:>+10,.2f} ({pct_ganho:+.1f}%)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Contratos:  {nivel['max_contratos']} (Sniper: {nivel['max_contratos_sniper']})\n"
            f"Score mín:  {nivel['score_minimo']} (Sniper: {nivel['score_sniper']})\n"
            f"Stop-day:   {nivel['stop_day_pct']:.1f}%\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        if prog["proximo"]:
            msg += (
                f"Próximo marco: R${prog['proximo']:,.0f}\n"
                f"Faltam:   R${prog['faltam']:,.2f}\n"
                f"Progresso: [{barra}] {prog['pct']:.0f}%"
            )
        else:
            msg += "✅ Todos os marcos atingidos! Modo máximo ativo."

        return msg
```

---
## `infrastructure/profit_bridge.py` (WIN)

```python
"""
CYBER TRADE WIN v1.0 — PROFIT BRIDGE (WIN)
=============================================
Interface com ProfitDLL para WINFUT (Mini Índice).

Diferenças vs WDO:
  - Símbolo: WINFUT (não WDOFUT)
  - Preço base: ~132.500 pontos (não ~5.860)
  - Tick mínimo: 5 pontos
  - ATR típico 5min: 200–800 pontos
  - Valor do ponto: R$0,20 (calculado no exec_agent, não aqui)
"""

import logging, os, random, time
from datetime import datetime

logger = logging.getLogger("profit_bridge")
PAPER_MODE = os.getenv("PAPER_MODE", "true").lower() == "true"
PRECO_BASE  = float(os.getenv("PRECO_BASE_SIMULADO", "132500.0"))
TICK        = 5  # Tick mínimo WIN em pontos


class ProfitBridge:

    def __init__(self):
        self._conectado = False
        self._dll       = None
        if PAPER_MODE:
            self._conectado = True
            logger.info("ProfitBridge WIN: modo PAPER — dados simulados (WINFUT)")
        else:
            self._conectar_dll()

    def is_connected(self) -> bool:
        return self._conectado

    def reconnect(self):
        if PAPER_MODE:
            self._conectado = True; return True
        return self._conectar_dll()

    def _conectar_dll(self) -> bool:
        try:
            # import ctypes
            # self._dll = ctypes.windll.LoadLibrary("C:\\Profit\\DLLProfitXI.dll")
            self._conectado = True
            logger.info("ProfitDLL WIN conectada")
            return True
        except Exception as e:
            logger.error(f"ProfitDLL WIN falhou: {e}")
            self._conectado = False
            return False

    def get_candles(self, symbol: str = "WINFUT", timeframe: int = 5,
                    n: int = 20) -> list[dict]:
        if PAPER_MODE:
            return self._simular_candles(n, timeframe)
        return []

    def get_candles_15m(self, symbol: str = "WINFUT", n: int = 10) -> list[dict]:
        return self.get_candles(symbol, 15, n)

    def get_book(self, symbol: str = "WINFUT") -> dict:
        if PAPER_MODE:
            return self._simular_book()
        return {"bids": [], "asks": []}

    def get_tape(self, symbol: str = "WINFUT", ultimos_n: int = 50) -> list[dict]:
        if PAPER_MODE:
            return self._simular_tape(ultimos_n)
        return []

    def get_preco_atual(self, symbol: str = "WINFUT") -> float:
        if PAPER_MODE:
            base = PRECO_BASE
            # WIN move em ticks de 5 pontos
            delta = random.randint(-10, 10) * TICK
            return base + delta
        return 0.0

    def melhor_ask(self) -> float:
        book = self.get_book()
        asks = book.get("asks", [])
        return asks[0]["preco"] if asks else 0.0

    def melhor_bid(self) -> float:
        book = self.get_book()
        bids = book.get("bids", [])
        return bids[0]["preco"] if bids else 0.0

    def enviar_ordem_mercado(self, direcao: str, contratos: int) -> str:
        if PAPER_MODE:
            raise RuntimeError("enviar_ordem_mercado chamada em PAPER_MODE — bug!")
        raise NotImplementedError("Implementar integração real com ProfitDLL para WINFUT")

    # ── Simuladores WIN ───────────────────────────────────────────────────

    def _simular_candles(self, n: int, tf: int) -> list[dict]:
        """Simula candles WIN com ATR realista (~300-600 pts em 5min)."""
        base = PRECO_BASE
        candles = []
        now = int(time.time())
        preco_atual = base

        for i in range(n, 0, -1):
            # Movimento aleatório em ticks (5 pts) — ATR ~400 pts por candle
            variacao = random.randint(-80, 80) * TICK  # ±400 pts max
            o = preco_atual
            h = o + random.randint(0, 50) * TICK       # até +250 pts
            l = o - random.randint(0, 50) * TICK       # até -250 pts
            c = l + random.randint(0, (h - l) // TICK) * TICK
            c = round(c / TICK) * TICK  # garante múltiplo de 5
            preco_atual = c

            candles.append({
                "time": datetime.fromtimestamp(now - i * tf * 60).strftime("%H:%M"),
                "open": o, "high": max(o, h, c), "low": min(o, l, c),
                "close": c,
                "volume": random.randint(100, 800),  # WIN tem volume menor por contrato
            })
        return candles

    def _simular_book(self) -> dict:
        base = self.get_preco_atual()
        # Book em ticks de 5 pontos
        bids = [{"preco": base - i * TICK, "volume": random.randint(5, 80)}
                for i in range(10)]
        asks = [{"preco": base + i * TICK, "volume": random.randint(5, 80)}
                for i in range(10)]
        return {"bids": bids, "asks": asks}

    def _simular_tape(self, n: int) -> list[dict]:
        base = self.get_preco_atual()
        agora_ms = int(time.time() * 1000)
        return [{
            "ms": agora_ms - i * 200,
            "preco": base + random.randint(-6, 6) * TICK,
            "volume": random.randint(1, 30),
            "agressor": random.choice(["COMPRA", "VENDA"])
        } for i in range(n)]
```

---
## `agents/exec_agent.py` (WIN — trecho crítico alterado)

```python
"""
CYBER TRADE WIN v1.0 — EXEC AGENT (WIN)
==========================================
ATENÇÃO: Valor do ponto WIN = R$0,20 por contrato.
         resultado_reais = resultado_pts * 0.20 * contratos

Todo o resto da lógica é idêntico ao v5.2 WDO,
com exceção de:
  - Símbolo: WINFUT
  - VALOR_PONTO: 0.20 (não 5.00)
  - BREAKEVEN_PTS: 80 (não 3.5)
  - TRAILING_FLOOR_PTS: 100 (não 5.0)
  - SLIPPAGE_MAX: 10.0 pts (não 3.0)
  - DESLOCAMENTO_MAX: 50 pts (não 1.5)
  - Posição fecha às 17:30 BRT (não 16:00)
  - Contrato fecha às 17:55 BRT (operacional até 17:30)
"""

import asyncio, json, logging, os, uuid
from datetime import datetime, time as dtime, timezone

logger = logging.getLogger("exec_agent")

PAPER_MODE       = os.getenv("PAPER_MODE", "true").lower() == "true"
VALOR_PONTO_WIN  = float(os.getenv("VALOR_PONTO_WIN", "0.20"))   # ← CRÍTICO
BREAKEVEN_PTS    = float(os.getenv("BREAKEVEN_PTS", "80.0"))
TRAILING_ATR_MIN = int(os.getenv("TRAILING_ATR_MIN", "3"))
TRAILING_FLOOR   = float(os.getenv("TRAILING_FLOOR_PTS", "100.0"))
SLIPPAGE_MAX     = float(os.getenv("SLIPPAGE_MAX_PTS", "10.0"))
HORARIO_FECHAR   = dtime(17, 30)  # WIN — fecha às 17:30


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

        # Lê contratos efetivos do nível de capital atual
        max_c_nivel = int(self.redis.get("max_contratos_efetivo") or 1)
        contratos_proposto = cyber_output.get("contratos", 1)
        contratos = min(contratos_proposto, max_c_nivel)

        if contratos < contratos_proposto:
            logger.info(
                f"EXEC WIN: contratos limitados pelo nível de capital: "
                f"{contratos_proposto} → {contratos}"
            )

        estado = {
            "decisao":    cyber_output["decisao"],
            "direcao":    cyber_output["direcao"],
            "contratos":  contratos,
            "entrada":    cyber_output["entrada_zona"],
            "stop":       cyber_output["stop"],
            "alvo1":      cyber_output["alvo1"],
            "alvo2":      cyber_output["alvo2"],
            "rr_alvo1":   cyber_output["rr_alvo1"],
            "gatilho":    cyber_output["gatilho"],
            "risco_reais":cyber_output["risco_financeiro_reais"],
            "score":      cyber_output["score_final"],
            "status":     "ARMADO",
            "armado_em":  datetime.now(timezone.utc).isoformat(),
        }

        self.redis.set("posicao_aberta", json.dumps(estado))
        score = cyber_output["score_final"]
        classificacao = cyber_output.get("setup_classificacao", "PADRÃO")

        # Calcula risco em R$ para exibição
        stop_pts   = abs(estado["entrada"] - estado["stop"])
        risco_reais = stop_pts * VALOR_PONTO_WIN * contratos

        self.tg.alertar(
            f"🎯 {'PREMIUM' if classificacao == 'PREMIUM' else 'SETUP'} ARMADO WIN "
            f"[Score {score}]\n"
            f"  {estado['direcao']} | {contratos}x | "
            f"Entrada: {estado['entrada']:,.0f}\n"
            f"  Stop: {estado['stop']:,.0f} ({stop_pts:.0f}pts) | "
            f"Alvo1: {estado['alvo1']:,.0f} | R:R {estado['rr_alvo1']:.2f}\n"
            f"  Risco: R${risco_reais:.2f} | "
            f"Gatilho: {estado['gatilho']['tipo']} | "
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
                    logger.info("EXEC WIN: 17:30 atingido — desarmar")
                    self._desarmar(); return

                if self._gatilho_ativado(estado):
                    await self._executar_entrada(estado); return

                await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"EXEC WIN loop_gatilho erro: {e}")
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
            tape = json.loads(self.redis.get("tape_metricas") or "{}")
        except Exception:
            tape = {}

        delta_1min = tape.get("cvd_1min", 0)
        burst      = tape.get("burst_detectado", False)
        held       = tape.get("held_bid_detectado" if direcao == "COMPRA"
                               else "held_offer_detectado", False)
        prints     = tape.get("held_bid_prints_confirmadores"
                              if direcao == "COMPRA"
                              else "held_offer_prints_confirmadores", 0)

        # WIN: tolerâncias maiores por ATR maior
        if tipo == "ROMPIMENTO":
            # Win: rompimento = 5 pontos além da zona
            trigger = entrada + 5 if direcao == "COMPRA" else entrada - 5
            cond_preco = preco >= trigger if direcao == "COMPRA" else preco <= trigger
            return cond_preco and abs(delta_1min) > 100 and burst

        elif tipo == "PULLBACK_ABSORÇÃO":
            distancia = abs(preco - entrada)
            return distancia <= 10 and held and prints >= 2

        elif tipo == "CONTINUAÇÃO":
            dist = abs(preco - entrada)
            return abs(delta_1min) >= 80 and dist <= 15

        elif tipo == "SWEEP_MOMENTUM":
            sweep = tape.get("sweep_detectado", False)
            dist  = abs(preco - entrada)
            return sweep and dist <= 20

        elif tipo == "ICEBERG_PREMIUM":
            iceberg = tape.get("iceberg_detectado", False)
            dist    = abs(preco - entrada)
            return iceberg and dist <= 10

        return False

    async def _executar_entrada(self, estado: dict):
        preco_market = self._preco_atual()
        if preco_market is None:
            self.tg.alertar("❌ EXEC WIN: preço indisponível — abortado")
            self._desarmar(); return

        slippage  = abs(preco_market - estado["entrada"])
        contratos = estado["contratos"]

        if slippage > SLIPPAGE_MAX:
            self.tg.alertar(
                f"❌ Slippage WIN {slippage:.0f}pts > {SLIPPAGE_MAX:.0f}pts — abortado"
            )
            self._desarmar(); return
        elif slippage > SLIPPAGE_MAX / 2:
            contratos = max(1, contratos // 2)
            self.tg.alertar(
                f"⚠️ Slippage WIN {slippage:.0f}pts → reduzindo para {contratos} contrato(s)"
            )

        if PAPER_MODE:
            ordem_id = f"PAPER_WIN_{uuid.uuid4().hex[:8].upper()}"
            preco_entrada_real = estado["entrada"]
            logger.info(f"PAPER WIN ORDER: {estado['direcao']} {contratos}x @ {preco_entrada_real:,.0f}")
        else:
            if self.profit:
                try:
                    ordem_id = self.profit.enviar_ordem_mercado(estado["direcao"], contratos)
                    preco_entrada_real = preco_market
                except Exception as e:
                    self.tg.alertar(f"🚨 Corretora rejeitou ordem WIN: {e}")
                    self._desarmar(); return
            else:
                self.tg.alertar("🚨 ProfitDLL WIN não conectada — abortado")
                self._desarmar(); return

        posicao = {**estado,
                   "status":          "ABERTA",
                   "ordem_id":        ordem_id,
                   "entrada_real":    preco_entrada_real,
                   "contratos_real":  contratos,
                   "stop_atual":      estado["stop"],
                   "breakeven_ativo": False,
                   "trailing_ativo":  False,
                   "parcial_exec":    False,
                   "aberta_em":       datetime.now(timezone.utc).isoformat()}

        self._posicao = posicao
        self.redis.set("posicao_aberta", json.dumps(posicao))
        self.redis.incr("trades_dia")

        risco_r = abs(preco_entrada_real - posicao["stop"]) * VALOR_PONTO_WIN * contratos

        self.tg.alertar(
            f"✅ ORDEM WIN {'(PAPER)' if PAPER_MODE else '(REAL)'}\n"
            f"  {posicao['direcao']} {contratos}x @ {preco_entrada_real:,.0f}\n"
            f"  Stop: {posicao['stop']:,.0f} | Alvo1: {posicao['alvo1']:,.0f}\n"
            f"  Risco: R${risco_r:.2f}"
        )

        asyncio.create_task(self._loop_posicao(posicao))

    async def _loop_posicao(self, posicao: dict):
        maximo_recente = posicao["entrada_real"]
        minimo_recente = posicao["entrada_real"]

        try:
            while True:
                if datetime.now().time() >= HORARIO_FECHAR:
                    await self._fechar_posicao(posicao, "ENCERRAMENTO_17H30"); return

                preco = self._preco_atual()
                if preco is None:
                    await asyncio.sleep(10); continue

                direcao = posicao["direcao"]
                stop    = posicao["stop_atual"]
                entrada = posicao["entrada_real"]

                if direcao == "COMPRA":
                    maximo_recente = max(maximo_recente, preco)
                else:
                    minimo_recente = min(minimo_recente, preco)

                lucro_pts = (preco - entrada) if direcao == "COMPRA" else (entrada - preco)

                # STOP
                stop_atingido = (preco <= stop if direcao == "COMPRA" else preco >= stop)
                if stop_atingido:
                    self.redis.incr("violinada_pendente")
                    await self._fechar_posicao(posicao, "STOP"); return

                # Fluxo contrário
                try:
                    tape = json.loads(self.redis.get("tape_metricas") or "{}")
                    if tape.get("divergencia_cvd_preco", False):
                        await self._fechar_posicao(posicao, "FLUXO_CONTRARIO"); return
                    if tape.get("exaustao_tps", False):
                        await self._fechar_posicao(posicao, "EXAUSTAO_TPS"); return
                except Exception:
                    pass

                # BREAK-EVEN
                if not posicao["breakeven_ativo"] and lucro_pts >= BREAKEVEN_PTS:
                    novo_stop = entrada + 5 if direcao == "COMPRA" else entrada - 5
                    posicao["stop_atual"]      = novo_stop
                    posicao["breakeven_ativo"] = True
                    self.redis.set("posicao_aberta", json.dumps(posicao))
                    self.redis.incr("breakeven_ativado_n")
                    self.tg.alertar(
                        f"✅ Break-even WIN ativado: stop → {novo_stop:,.0f} "
                        f"(+{lucro_pts:.0f}pts de lucro)"
                    )

                # TRAILING ATR
                if posicao["breakeven_ativo"]:
                    if not posicao["trailing_ativo"]:
                        posicao["trailing_ativo"] = True
                        self.redis.incr("trailing_ativado_n")

                    atr = self._atr_recente()
                    trail_dist = max(1.5 * atr, TRAILING_FLOOR)

                    if direcao == "COMPRA":
                        novo_stop = maximo_recente - trail_dist
                        if novo_stop > posicao["stop_atual"]:
                            posicao["stop_atual"] = novo_stop
                            self.redis.set("posicao_aberta", json.dumps(posicao))
                            self.tg.alertar(f"📈 Trailing WIN → stop: {novo_stop:,.0f}")
                    else:
                        novo_stop = minimo_recente + trail_dist
                        if novo_stop < posicao["stop_atual"]:
                            posicao["stop_atual"] = novo_stop
                            self.redis.set("posicao_aberta", json.dumps(posicao))
                            self.tg.alertar(f"📉 Trailing WIN → stop: {novo_stop:,.0f}")

                # ALVOS
                if not posicao["trailing_ativo"]:
                    alvo1_ok = (preco >= posicao["alvo1"] if direcao == "COMPRA"
                                else preco <= posicao["alvo1"])
                    if alvo1_ok and not posicao["parcial_exec"]:
                        posicao["parcial_exec"] = True
                        ganho_alvo1 = abs(posicao["alvo1"] - entrada) * VALOR_PONTO_WIN * posicao["contratos_real"]
                        self.tg.alertar(
                            f"🎯 Alvo1 WIN atingido: {posicao['alvo1']:,.0f}\n"
                            f"  Parcial 50% | Ganho est: R${ganho_alvo1:.2f}"
                        )

                    alvo2_ok = (preco >= posicao["alvo2"] if direcao == "COMPRA"
                                else preco <= posicao["alvo2"])
                    if alvo2_ok:
                        await self._fechar_posicao(posicao, "ALVO2"); return

                await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"EXEC WIN loop_posicao erro: {e}")
            await self._fechar_posicao(posicao, "ERRO_INTERNO")

    async def _fechar_posicao(self, posicao: dict, motivo: str):
        preco_saida = self._preco_atual() or posicao["stop_atual"]
        direcao     = posicao["direcao"]
        entrada     = posicao["entrada_real"]
        contratos   = posicao["contratos_real"]

        resultado_pts   = ((preco_saida - entrada) if direcao == "COMPRA"
                           else (entrada - preco_saida))
        # ★ CRÍTICO WIN: 1 ponto = R$0,20 por contrato
        resultado_reais = resultado_pts * VALOR_PONTO_WIN * contratos

        try:
            self.db.registrar_trade({
                "data":              datetime.now().isoformat(),
                "direcao":           direcao,
                "contratos":         contratos,
                "entrada":           entrada,
                "saida":             preco_saida,
                "resultado_pts":     resultado_pts,
                "resultado_reais":   resultado_reais,
                "motivo_saida":      motivo,
                "stop_final":        posicao["stop_atual"],
                "breakeven_ativado": posicao["breakeven_ativo"],
                "trailing_ativado":  posicao["trailing_ativo"],
                "score":             posicao.get("score", 0),
                "modo":              "PAPER" if PAPER_MODE else "REAL",
                "ordem_id":          posicao.get("ordem_id", ""),
            })
        except Exception as e:
            logger.error(f"Erro ao registrar trade WIN: {e}")

        self.redis.delete("posicao_aberta")
        if resultado_reais > 0:
            self.redis.incr("ganhos_dia")
            self.redis.set("losses_consecutivos", "0")
        else:
            self.redis.incr("losses_consecutivos")

        acum = float(self.redis.get("resultado_dia_reais") or 0)
        self.redis.set("resultado_dia_reais", str(acum + resultado_reais))

        # Atualiza capital e verifica nível
        capital_atual = self.redis.get_capital() or float(os.getenv("CAPITAL_INICIAL", "1000"))
        novo_capital  = capital_atual + resultado_reais
        self.redis.set_capital(novo_capital)

        emoji = "✅" if resultado_reais > 0 else "❌"
        self.tg.alertar(
            f"{emoji} TRADE WIN ENCERRADO — {motivo}\n"
            f"  {direcao} {contratos}x | "
            f"Entrada: {entrada:,.0f} → Saída: {preco_saida:,.0f}\n"
            f"  {resultado_pts:+.0f} pts | R$ {resultado_reais:+.2f}\n"
            f"  Capital: R${novo_capital:,.2f}\n"
            f"  Break-even: {'✅' if posicao['breakeven_ativo'] else '❌'} | "
            f"Trailing: {'✅' if posicao['trailing_ativo'] else '❌'}"
        )

        self._posicao = None

    def _validar_json_cyber(self, output: dict) -> bool:
        obrigatorios = ["decisao", "direcao", "contratos", "entrada_zona",
                        "stop", "alvo1", "alvo2", "gatilho", "risco_financeiro_reais"]
        for campo in obrigatorios:
            if campo not in output or output[campo] is None:
                logger.error(f"EXEC WIN: campo obrigatório ausente: {campo}")
                self.tg.alertar(f"❌ EXEC WIN: JSON inválido — '{campo}' ausente")
                return False

        direcao = output.get("direcao")
        entrada = output.get("entrada_zona", 0)
        stop    = output.get("stop", 0)
        alvo1   = output.get("alvo1", 0)

        if direcao == "COMPRA" and not (stop < entrada < alvo1):
            self.tg.alertar("❌ EXEC WIN: incoerência de preços COMPRA")
            return False
        if direcao == "VENDA" and not (stop > entrada > alvo1):
            self.tg.alertar("❌ EXEC WIN: incoerência de preços VENDA")
            return False
        return True

    def _preco_atual(self) -> float | None:
        try:
            val = self.redis.get("preco_atual_win")
            return float(val) if val else None
        except Exception:
            return None

    def _atr_recente(self) -> float:
        try:
            return float(self.redis.get("atr_atual_win") or "300.0")
        except Exception:
            return 300.0

    def _desarmar(self):
        self.redis.delete("posicao_aberta")
        self._posicao    = None
        self._loop_ativo = False
```

---
## `agents/cyber_agent.py` (WIN — parâmetros adaptados)

```python
"""
CYBER TRADE WIN v1.0 — CYBER AGENT (WIN)
==========================================
Adaptações vs WDO:
  - MAX_CONTRATOS: 5 (dinâmico por nível de capital)
  - SLIPPAGE_MAX: 10 pts (não 3.0)
  - DESLOCAMENTO_MAX: 50 pts (não 1.5)
  - Cálculo de risco usa VALOR_PONTO_WIN = 0.20
  - Score mínimo adaptativo por nível (lido do Redis)
"""

import json, logging, os
from datetime import datetime, timedelta, timezone
from agents.base_agent import BaseAgent

logger = logging.getLogger("cyber_agent")

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
            nome="cyber",
            skill_path="./skills/cyber_skill_win.md",
            router=router,
            max_tokens=1500,
            temperature=0.1,
        )
        self.redis = redis_state

    async def decidir(self, cyber_input: dict) -> dict:
        sniper_mode = self._ler_sniper_mode(cyber_input["estado_sistema"])

        # Score mínimo e max contratos vêm do nível de capital (Redis)
        score_min = self._score_minimo_atual(sniper_mode)
        max_c     = self._max_contratos_atual(sniper_mode)

        bloqueio = self._pre_filtro_deterministico(
            cyber_input["estado_sistema"],
            cyber_input["graph"],
            cyber_input["flow"],
            cyber_input["context"],
            sniper_mode, score_min
        )
        if bloqueio:
            return self._decisao_cancelar(bloqueio, cyber_input, sniper_mode)

        cyber_input["estado_sistema"]["sniper_mode"]        = sniper_mode
        cyber_input["estado_sistema"]["score_minimo_ativo"] = score_min
        cyber_input["estado_sistema"]["max_contratos_nivel"] = max_c

        user_content = json.dumps(cyber_input, ensure_ascii=False, indent=2)

        try:
            resultado = await self.invocar(user_content)
        except Exception as e:
            logger.error(f"CYBER WIN LLM falhou: {e}")
            return self._decisao_cancelar(f"Erro LLM: {e}", cyber_input, sniper_mode)

        resultado = self._pos_validar(resultado, cyber_input, sniper_mode, score_min, max_c)
        return resultado

    def _score_minimo_atual(self, sniper_mode: bool) -> int:
        """Lê score mínimo do nível de capital atual no Redis."""
        if self.redis:
            try:
                if sniper_mode:
                    # Score sniper: pega do redis ou default 80
                    return int(self.redis.get("score_sniper_nivel") or
                               os.getenv("SNIPER_SCORE_MIN", "80"))
                return int(self.redis.get("score_minimo_nivel") or
                           os.getenv("SCORE_MIN_NORMAL", "72"))
            except Exception:
                pass
        return SNIPER_SCORE_MIN if sniper_mode else 72

    def _max_contratos_atual(self, sniper_mode: bool) -> int:
        """Lê max_contratos do nível de capital atual no Redis."""
        if self.redis:
            try:
                return int(self.redis.get("max_contratos_efetivo") or 1)
            except Exception:
                pass
        return 2 if sniper_mode else 1

    def _stop_day_pct_atual(self) -> float:
        """Lê stop-day adaptativo do nível atual."""
        if self.redis:
            try:
                return float(self.redis.get("stop_day_pct_nivel") or 5.0)
            except Exception:
                pass
        return 5.0

    def _pre_filtro_deterministico(self, estado, graph, flow, context,
                                   sniper_mode: bool, score_min: int) -> str | None:
        stop_day = self._stop_day_pct_atual()
        res_dia  = estado.get("resultado_dia_percentual", 0)

        if res_dia <= -stop_day:
            return f"Stop-day atingido: {res_dia:.2f}% (limite: -{stop_day:.1f}%)"
        if estado.get("operacoes_hoje", 0) >= MAX_OPERACOES_DIA:
            return f"Máximo de {MAX_OPERACOES_DIA} operações atingido"
        if estado.get("em_cool_down", False):
            return "Cool-down ativo (3 losses consecutivos)"
        if context.get("status_macro") == "BLOQUEADO":
            return "CONTEXT: evento macro BLOQUEADO"
        if context.get("qualidade_sessao") == "PROIBIDO":
            return f"Sessão proibida: {context.get('sessao_atual')}"
        if context.get("ny_open_status") == "BLOQUEADO":
            return "Abertura NY: primeiros 3min bloqueados"
        if graph.get("sinal") == "NEUTRO" or graph.get("confianca", 0) == 0:
            return "GRAPH: sinal NEUTRO ou confiança zero"
        if graph.get("confianca", 0) < 60:
            return f"GRAPH: confiança {graph.get('confianca')} < 60"
        if flow.get("forca_fluxo", 0) < 40:
            return f"FLOW: força {flow.get('forca_fluxo')} < 40"
        if context.get("regime_mercado") == "MORTO":
            return "Regime MORTO: ATR_WIN < 0.6× média"
        if graph.get("tendencia_master_15m") == "INDEFINIDA":
            return "GRAPH: tendência 15m INDEFINIDA"

        sinal   = graph.get("sinal")
        cvd_div = flow.get("divergencia_cvd_preco", False)
        if cvd_div and sinal == "COMPRA":
            return "CVD: divergência baixista — não comprar"
        if cvd_div and sinal == "VENDA":
            return "CVD: divergência altista — não vender"
        if flow.get("exaustao_tps", False):
            return "Exaustão TPS: momentum esgotado"

        lat  = estado.get("latencia_ciclo_segundos", 0)
        desl = estado.get("deslocamento_preco_desde_analise", 0)
        if lat > LATENCIA_MAX_S and desl > DESLOCAMENTO_MAX_PTS:
            return f"Latência {lat:.1f}s + deslocamento {desl:.0f}pts WIN"

        if sniper_mode:
            score_est = self._estimar_score(graph, flow, context)
            if score_est < SNIPER_SCORE_MIN:
                return f"Sniper WIN: score estimado {score_est} < {SNIPER_SCORE_MIN}"

        return None

    def _estimar_score(self, graph, flow, context) -> int:
        g = graph.get("confianca", 0) * 0.35
        f = flow.get("forca_fluxo", 0) * 0.30
        pen = context.get("penalidade_score", 0)
        bon = context.get("sp500", {}).get("bonus_correlacao", 0)
        c   = max(0, 100 - pen + bon) * 0.20
        t   = (100 if context.get("qualidade_sessao") in ("EXCELENTE", "BOA") else 70) * 0.05
        score = g + f + c + t
        if flow.get("iceberg_detectado"): score += 10
        if flow.get("tape_held_level", {}).get("confirmacao_dupla_ok"): score += 7
        if flow.get("divergencia_delta_preco"): score -= 10
        if graph.get("volume_relativo", 1.0) < 0.8: score -= 10
        return int(min(100, max(0, score)))

    def _pos_validar(self, resultado: dict, cyber_input: dict,
                     sniper_mode: bool, score_min: int, max_c: int) -> dict:
        estado  = cyber_input["estado_sistema"]
        decisao = resultado.get("decisao", "CANCELAR")
        score   = resultado.get("score_final", 0)
        motivos_cancelamento = []

        if decisao == "ARMAR" and score < score_min:
            motivos_cancelamento.append(f"Score {score} < mínimo {score_min}")

        rr = resultado.get("rr_alvo1", 0)
        if decisao == "ARMAR" and rr < RR_MINIMO:
            motivos_cancelamento.append(f"R:R {rr:.2f} < {RR_MINIMO}")

        contratos = resultado.get("contratos", 1)
        if contratos > max_c:
            logger.warning(f"CYBER WIN: contratos {contratos} > máx nível {max_c} → limitado")
            resultado["contratos"] = max_c

        # Validar risco financeiro usando VALOR_PONTO_WIN
        capital     = estado.get("capital_atual", 1000)
        risco_max   = capital * RISCO_POR_TRADE_PCT / 100
        stop_pts    = abs((resultado.get("entrada_zona", 0) or 0) -
                          (resultado.get("stop", 0) or 0))
        risco_calc  = stop_pts * VALOR_PONTO_WIN * resultado.get("contratos", 1)
        if risco_calc > risco_max * 1.05 and decisao == "ARMAR":
            motivos_cancelamento.append(
                f"Risco R${risco_calc:.2f} excede 1% capital (R${risco_max:.2f})"
            )

        if decisao == "ARMAR":
            direcao = resultado.get("direcao", "")
            entrada = resultado.get("entrada_zona", 0)
            stop    = resultado.get("stop", 0)
            alvo1   = resultado.get("alvo1", 0)
            if direcao == "COMPRA" and not (stop < entrada < alvo1):
                motivos_cancelamento.append("Incoerência preços COMPRA WIN")
            elif direcao == "VENDA" and not (stop > entrada > alvo1):
                motivos_cancelamento.append("Incoerência preços VENDA WIN")

        # Stop-day adaptativo
        stop_day_atual = self._stop_day_pct_atual()
        res_dia = estado.get("resultado_dia_percentual", 0)
        if res_dia <= -stop_day_atual:
            motivos_cancelamento.append(f"Stop-day WIN: {res_dia:.2f}%")

        losses = estado.get("losses_consecutivos", 0)
        if losses >= 2 and decisao == "ARMAR":
            resultado["contratos"] = 1
        if res_dia < 0 and decisao == "ARMAR" and resultado.get("contratos", 1) > 1:
            resultado["contratos"] = 1

        equity_filter = estado.get("equity_filter_10d", 1.0)
        if equity_filter <= 0.5:   resultado["contratos"] = 1
        elif equity_filter <= 0.75: resultado["contratos"] = min(resultado.get("contratos", 1), 2)

        if decisao == "ARMAR" and "gatilho" in resultado:
            gatilho = resultado["gatilho"]
            if "validade_expira_em" not in gatilho or not gatilho["validade_expira_em"]:
                segundos = gatilho.get("validade_segundos", 90)
                expira   = datetime.now(timezone.utc) + timedelta(seconds=segundos)
                gatilho["validade_expira_em"] = expira.isoformat()
                resultado["gatilho"] = gatilho

        if motivos_cancelamento:
            resultado["decisao"] = "CANCELAR"
            resultado["motivo"]  = (
                f"PÓS-VALIDAÇÃO WIN: {' | '.join(motivos_cancelamento)}. "
                f"LLM disse: {resultado.get('motivo','')[:200]}"
            )
            logger.warning(f"CYBER WIN → CANCELAR: {motivos_cancelamento}")

        resultado["sniper_mode_ativo"]  = sniper_mode
        resultado["modo"]               = "PAPER" if os.getenv("PAPER_MODE","true").lower()=="true" else "REAL"
        resultado["nivel_capital"]       = self.redis.get("nome_nivel_capital") if self.redis else "N/D"
        resultado["max_contratos_nivel"] = max_c

        return resultado

    def _ler_sniper_mode(self, estado: dict) -> bool:
        if self.redis:
            try:
                val = self.redis.get("sniper_mode")
                if val is not None:
                    return str(val).lower() == "true"
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

---
## `utils/risk_manager.py` (WIN)

```python
"""CYBER TRADE WIN v1.0 — RISK MANAGER (WIN) — Sizing e equity filter."""
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
                           sniper_mode: bool = False) -> int:
        if stop_pts <= 0:
            return 1

        risco_reais     = capital * RISCO_PCT / 100
        risco_contrato  = stop_pts * VALOR_PONTO_WIN  # WIN: R$0,20/pt
        contratos_ideais = int(risco_reais / risco_contrato)

        # Respeitar limite do nível de capital
        max_c = 2 if sniper_mode else max_contratos_nivel
        max_c = min(max_c, 5)  # Hard cap absoluto = 5

        # Equity filter
        if equity_filter <= 0.5:    max_c = 1
        elif equity_filter <= 0.75: max_c = min(max_c, 2)

        # Proteções adicionais
        if resultado_dia_pct < 0:          contratos_ideais = min(contratos_ideais, 1)
        if losses_consecutivos >= 2:       contratos_ideais = 1

        return max(1, min(contratos_ideais, max_c))

    def risco_financeiro(self, capital: float, contratos: int, stop_pts: float) -> float:
        """Risco em R$ para WIN."""
        return contratos * stop_pts * VALOR_PONTO_WIN

    def calcular_equity_filter(self, trades_10d: list, capital: float) -> float:
        if not trades_10d: return 1.0
        pnl_10d = sum(t.get("resultado_reais", 0) for t in trades_10d)
        pct     = pnl_10d / capital * 100
        if pct <= -3.0: return 0.5
        if pct <= -1.5: return 0.75
        return 1.0

    def relatorio_sizing(self, capital: float, stop_pts: float,
                         nivel: int = 1) -> str:
        """Relatório didático de sizing para WIN."""
        risco_r = capital * RISCO_PCT / 100
        risco_c = stop_pts * VALOR_PONTO_WIN
        contratos = max(1, int(risco_r / risco_c)) if risco_c > 0 else 1
        return (
            f"📊 SIZING WIN | Capital: R${capital:,.2f}\n"
            f"  Risco 1%: R${risco_r:.2f}\n"
            f"  Stop: {stop_pts:.0f} pts = R${risco_c:.2f}/contrato\n"
            f"  Contratos calculados: {contratos}\n"
            f"  Limite do nível {nivel}: ver openclw_win.json"
        )
```

---
## `skills/context_skill_win.md`

```markdown
# CONTEXT WIN — Macro IBOVESPA + S&P500 + DI1F | Cyber Trade WIN v1.0

## IDENTIDADE
Agente CONTEXT do Cyber Trade WIN v1.0. Analisa contexto macro para WINFUT
(Mini Índice Futuro B3). Você NÃO usa DXY nem Ptax como drivers primários.
Responda APENAS com JSON válido.

## DRIVERS MACRO DO WIN (prioridade)
1. **S&P500**: Principal correlação diária. Alta SP → bias alta WIN
2. **IBOVESPA**: Composição: ~20% Petrobras/Vale → afetado por commodities
3. **VIX**: >25 = aversão a risco → penalidade -20. >35 = BLOQUEADO
4. **DI1F (juros)**: Alta nos juros = pressão vendedora no índice
5. **Petróleo (Brent)**: Petrobras ~10% do IBOV — Brent forte → WIN alta
6. **Minério de Ferro**: Vale ~8% do IBOV — Minério forte → WIN alta
7. **Câmbio USD/BRL**: BRL desvaloriza → exportadoras sobem, financeiros caem
8. **Cenário político BR**: ALTO RISCO — eventos inesperados causam spikes

## PROTOCOLO — 6 PASSOS

### PASSO 1 — Status MACRO (bloqueador master)
- BLOQUEADO: Decisão COPOM | PIB BR | Payroll EUA | CPI EUA em < 30min
- BLOQUEADO: VIX > 35 (pânico global)
- ALERTA_REACAO (-25): evento impactante publicado há < 15min
- ALERTA_MODERADO (-15): evento médio em < 15min
- ALERTA_FUTURO (-5): evento alto nas próximas 4h
- MORTO: ATR_WIN < 0.6× média (índice parado = não operar)

### PASSO 2 — S&P500 e Correlação
- SP500 subindo forte + WIN subindo → bônus +10 (confirmação)
- SP500 subindo + WIN caindo → DIVERGÊNCIA → penalidade -15
- SP500 caindo forte → penalidade -10 para compras WIN
- SP500 neutro/flat → sem bônus nem penalidade

### PASSO 3 — VIX (Fear Index)
- VIX < 15: baixa volatilidade → fator de liquidez normal
- VIX 15–25: normal → sem ajuste
- VIX 25–35: elevado → penalidade -10, reduzir tamanho
- VIX > 35: BLOQUEADO (pânico = spreads explosivos)

### PASSO 4 — DI1F (Juros Brasileiros)
- COPOM hawkish (alta surpresa) → penalidade -20 para compras
- DI1F subindo forte (>0.5% em 1h) → penalidade -15 compras, bônus +8 vendas
- DI1F estável → sem ajuste
- Pré-COPOM (semana de decisão) → alerta preventivo

### PASSO 5 — Commodities (IBOV composition)
- Petróleo Brent +1% ou mais → bônus +5 para compras WIN (Petrobras)
- Minério de Ferro +1% ou mais → bônus +5 para compras WIN (Vale)
- Ambos caindo forte → penalidade -10 para compras

### PASSO 6 — Regime e Sessão WIN
Sessões e fator_liquidez:
- ABERTURA (09:00-09:15): PROIBIDO | 0.0
- MANHA_INICIAL (09:15-10:30): MODERADA | 0.85
- NY_TRANSICAO (10:30-10:48): CAUTELA | 0.75 (abertura NY influencia WIN)
- MANHA_ATIVA (10:48-12:00): EXCELENTE | 1.00
- ALMOCO (12:00-13:30): PROIBIDO | 0.0
- TARDE_INICIAL (13:30-14:15): MODERADA | 0.80
- TARDE_ATIVA (14:15-16:30): BOA | 0.90
- TARDE_FINAL (16:30-17:30): MODERADA | 0.60
- PRE_FECHAMENTO (17:30+): PROIBIDO | 0.0

## OUTPUT (JSON exato)
```json
{
  "agente": "CONTEXT_WIN",
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
  "vix": {
    "nivel": 18.5,
    "status": "NORMAL",
    "penalidade": 0,
    "alerta": null
  },
  "di1f": {
    "variacao_1h_pct": 0.05,
    "inclinacao": "ESTAVEL",
    "distorcao_detectada": false,
    "penalidade_di1f": 0,
    "bonus_di1f": 0,
    "alerta": null
  },
  "commodities": {
    "petroleo_brent_var_pct": 0.8,
    "minerio_ferro_var_pct": 0.3,
    "bonus_commodities": 5,
    "alerta": null
  },
  "sessao_atual": "MANHA_ATIVA",
  "qualidade_sessao": "EXCELENTE",
  "ny_open_status": "ESTABILIZADO",
  "custo_status": "NORMAL",
  "alertas": [],
  "resumo": "<texto legível dos fatores principais>"
}
```

## REGRAS ABSOLUTAS
❌ NUNCA liberar com VIX > 35
❌ NUNCA ignorar COPOM, PIB, Payroll, CPI iminentes (<30min)
❌ NUNCA liberar sessões PROIBIDO
❌ NUNCA mencionar DXY/Ptax como driver primário — é índice, não câmbio
❌ NUNCA campos faltantes
✅ SEMPRE incluir sp500, vix, di1f, commodities no JSON
✅ SEMPRE alertar divergência WIN vs SP500
```

---
## `skills/graph_skill_win.md`

```markdown
# GRAPH WIN — Análise Técnica WINFUT | Cyber Trade WIN v1.0

## IDENTIDADE
Agente GRAPH do Cyber Trade WIN v1.0. Análise técnica multi-timeframe do
WINFUT (Mini Índice Futuro B3). Preços em pontos de índice (~130.000-135.000).
Responda APENAS com JSON válido.

## ATENÇÃO — ESCALA WIN
- Preços típicos: 130.000–135.000 pontos
- ATR 5min típico: 200–800 pontos
- Tick mínimo: 5 pontos
- Stop mínimo razoável: 80–300 pontos
- Todos os valores de preço em pontos inteiros (ex: 132500, não 132.500,0)

## PROTOCOLO — 5 PASSOS

### PASSO 1 — Tendência 15min (FILTRO MASTER)
- EMA9_15m > EMA21_15m → ALTA → só COMPRA
- EMA9_15m < EMA21_15m → BAIXA → só VENDA
- |EMA9_15m - EMA21_15m| < 100 pontos → INDEFINIDA → NEUTRO

### PASSO 2 — Localização de Preço
- Números redondos (ex: 130.000, 131.000, 132.500): fortes S/R
- VWAP: acima + tendência ALTA = contexto ideal compra
- POC: ±(0.5×ATR_WIN) do POC → zona equilíbrio → não operar

### PASSO 3 — Momentum 5min
- RSI: 40-65 (compra) | 35-60 (venda) | >70 bloquear compra | <30 bloquear venda
- MACD: histograma crescendo = momentum válido
- Volume: <0.8× média → -15 | >1.2× → +10

### PASSO 4 — Padrão de Candle (em pontos WIN)
- COMPRA: Engolfo Alta (corpo >100pts) | Martelo | Pin Bar sombra inf > 2×corpo
- VENDA: Engolfo Baixa (corpo >100pts) | Estrela Cadente | Pin Bar sombra sup
- NEUTRO: Doji | sombras longas ambos os lados | corpo < 50pts

### PASSO 5 — R:R (obrigatório, em pontos WIN)
- Stop: último swing relevante, MÁXIMO 2×ATR_WIN (ex: se ATR=400, stop máx=800)
- Alvo1: próxima S/R → R:R MÍNIMO 1.5
- SE R:R < 1.5 → sinal = "NEUTRO"

## OUTPUT (JSON exato)
```json
{
  "agente": "GRAPH_WIN",
  "timestamp": "<ISO8601>",
  "tendencia_master_15m": "ALTA",
  "tendencia_5m": "ALTA",
  "alinhamento_timeframes": true,
  "regime_favorece": "ROMPIMENTO",
  "sinal": "COMPRA",
  "confianca": 72,
  "localizacao": {
    "vs_vwap": "ACIMA",
    "vs_poc": "ACIMA",
    "vs_maxima_dia": "DISTANTE",
    "vs_minima_dia": "DISTANTE",
    "numero_redondo_proximo": 132500
  },
  "entrada_sugerida": 132650,
  "stop_sugerido": 132350,
  "alvo1_sugerido": 133100,
  "alvo2_sugerido": 133500,
  "rr_alvo1": 1.5,
  "rr_alvo2": 2.8,
  "distancia_stop_pontos": 300,
  "padrao_candle": "Engolfo de Alta",
  "rsi": 58.5,
  "volume_relativo": 1.35,
  "atr_win": 380,
  "macd_favoravel": true,
  "alertas": [],
  "resumo": "<fatores principais>"
}
```

## REGRAS ABSOLUTAS WIN
❌ NUNCA confiança > 80
❌ NUNCA sinal contra tendência 15min
❌ NUNCA stop > 2×ATR_WIN
❌ NUNCA R:R < 1.5
❌ NUNCA stop < 80 pontos (risco de violinada)
❌ NUNCA na zona do POC (±0.5×ATR)
✅ Em dúvida → NEUTRO, confianca=0
✅ Preços SEMPRE em pontos inteiros múltiplos de 5
```

---
## `skills/cyber_skill_win.md`

```markdown
# CYBER WIN — Orquestrador e Decisão Final | Cyber Trade WIN v1.0

## IDENTIDADE
Orquestrador CYBER do Cyber Trade WIN v1.0. Recebe GRAPH_WIN + FLOW + CONTEXT_WIN
e decide. Única autoridade para autorizar trade. Responda APENAS com JSON válido.

## PARÂMETROS WIN CRÍTICOS
- Valor ponto: R$0,20/pt/contrato
- Risco por trade: 1% do capital
- Max contratos: DINÂMICO (lido do estado_sistema.max_contratos_nivel)
- Score mínimo: DINÂMICO (lido do estado_sistema.score_minimo_ativo)
- Preços em pontos inteiros WIN (ex: 132500, não 132.5)

## PROTOCOLO — 7 PASSOS

### PASSO 1 — Filtros de Bloqueio (qualquer = CANCELAR)
- context.status_macro = "BLOQUEADO"
- context.qualidade_sessao = "PROIBIDO"
- context.vix.nivel > 35
- estado.em_cool_down = true
- estado.operacoes_hoje >= 5
- estado.resultado_dia_percentual <= -(estado.stop_day_pct)
- graph.sinal = "NEUTRO" ou confianca < 60
- flow.forca_fluxo < 40
- context.regime_mercado = "MORTO"
- graph.tendencia_master_15m = "INDEFINIDA"
- flow.divergencia_cvd_preco = true E direção conflitante
- flow.exaustao_tps = true
- latencia > 5s E deslocamento > 50pts WIN

### PASSO 2 — Alinhamento
- graph.sinal ≠ flow.direcao_fluxo → CANCELAR

### PASSO 3 — Coerência de Regime
- RANGE + ROMPIMENTO: -15
- TRENDING + ROMPIMENTO: +5

### PASSO 4 — Score Composto
PESOS: GRAPH 35% | FLOW 30% | CONTEXT 20% | TIMING 5%

AJUSTES WIN:
+10 iceberg | +7 held duplo | +5 delta candle alto
+5 sweep | +5 SP500 alinhado | +5 commodities alinhadas
-5 rompimento fraco | -10 divergência delta/preço
-10 SP500 divergente | -10 VIX alto | -15 spoof

### PASSO 5 — Limiares (adaptativos pelo nível)
- score >= 85: ARMAR PREMIUM
- score >= estado.score_minimo_ativo: ARMAR
- score 55-64: AGUARDAR
- score < 55: CANCELAR

### PASSO 6 — Sizing WIN
```
risco_financeiro = capital_atual × 0.01
stop_pts = abs(entrada - stop)
risco_contrato = stop_pts × 0.20    ← WIN: R$0,20/pt
contratos_ideais = floor(risco_financeiro / risco_contrato)
contratos_final = min(contratos_ideais, estado.max_contratos_nivel)
```

### PASSO 7 — Gatilho (tolerâncias WIN)
- ROMPIMENTO: preco ± 5pts + delta >100 + burst | 120s
- PULLBACK_ABSORÇÃO: retorno a zona ± 10pts + Held Level | 90s
- CONTINUAÇÃO: agressão >80c após retração ± 15pts | 60s
- SWEEP_MOMENTUM: pullback pós-sweep ± 20pts | 45s
- ICEBERG_PREMIUM: iceberg ativo ± 10pts | 75s

## OUTPUT (JSON exato)
```json
{
  "agente": "CYBER_WIN",
  "timestamp": "<ISO8601>",
  "decisao": "ARMAR",
  "score_final": 78,
  "score_detalhado": {
    "componente_graph": 25.2,
    "componente_flow": 24.0,
    "componente_context": 14.0,
    "componente_timing": 5.0,
    "ajustes_especiais": 10.0,
    "penalidades": 0.0,
    "total": 78.2,
    "arredondado": 78
  },
  "setup_classificacao": "PADRÃO",
  "tipo_setup": "PULLBACK_ABSORÇÃO",
  "direcao": "COMPRA",
  "contratos": 1,
  "entrada_zona": 132650,
  "stop": 132350,
  "alvo1": 133100,
  "alvo2": 133500,
  "rr_alvo1": 1.5,
  "gatilho": {
    "tipo": "PULLBACK_ABSORÇÃO",
    "descricao": "Preço retorna a 132650 com Held Bid @ 132600",
    "validade_segundos": 90,
    "validade_expira_em": "<ISO8601>"
  },
  "risco_financeiro_reais": 60.0,
  "risco_percentual": 1.0,
  "nivel_capital": "INICIANTE",
  "max_contratos_nivel": 1,
  "modo": "PAPER",
  "motivo": "<explicação legível>",
  "alertas_operador": []
}
```
```

---
## `guard.py` (WIN — com monitoramento de nível de capital)

```python
"""
CYBER TRADE WIN v1.0 — GUARD (WIN)
=====================================
Watchdog do sistema. Iniciar ANTES do main.py.

Adições vs WDO v5.2:
  - Monitoramento de nível de capital (CapitalLevelManager)
  - Alerta de marcos (R$1K, R$2K, R$3K, R$5K, R$7K, R$10K)
  - Relatório diário inclui progresso de capital
  - /nivel e /capital como novos comandos Telegram
  - Horário de fechamento: 17:30 BRT (WIN)
  - Relatório diário: 18:00 BRT
"""

import asyncio, json, logging, os
from datetime import datetime, time as dtime
import redis as redis_lib
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("guard_win")
logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"),
                    format="%(asctime)s %(name)s %(levelname)s %(message)s")

PAPER_MODE = os.getenv("PAPER_MODE","true").lower() == "true"


class Guard:

    def __init__(self):
        self.r = redis_lib.Redis(
            host=os.getenv("REDIS_HOST","localhost"),
            port=int(os.getenv("REDIS_PORT","6379")),
            password=os.getenv("REDIS_PASSWORD") or None,
            decode_responses=True,
        )
        try:
            from infrastructure.telegram_bot import TelegramBot
            self.tg = TelegramBot()
        except Exception as e:
            logger.warning(f"Telegram não disponível: {e}"); self.tg = None

        self._sniper_mode = False
        self._custo_alerta_enviado = False
        self._capital_level_mgr = None

    async def iniciar(self):
        # Inicializar CapitalLevelManager
        try:
            from utils.capital_levels import CapitalLevelManager
            from infrastructure.redis_state import RedisState
            from infrastructure.database import Database
            redis_state = RedisState()
            db = Database()
            self._capital_level_mgr = CapitalLevelManager(redis_state, self.tg, db)
            # Aplicar nível inicial ao Redis
            capital = redis_state.get_capital() or float(os.getenv("CAPITAL_INICIAL","1000"))
            from utils.capital_levels import get_nivel
            nivel = get_nivel(capital)
            self._capital_level_mgr.aplicar_nivel_ao_redis(nivel)
        except Exception as e:
            logger.error(f"CapitalLevelManager falhou: {e}")

        modo = "🟡 PAPER" if PAPER_MODE else "🔴 PRODUÇÃO"
        capital_ini = float(os.getenv("CAPITAL_INICIAL","1000"))
        self._alertar(
            f"🛡️ GUARD WIN v1.0 iniciado | {modo}\n"
            f"💰 Capital inicial: R${capital_ini:,.2f}\n"
            f"📊 Mini Índice WINFUT | Máx 5 contratos\n"
            f"🎯 Meta: R$5.000 (5× inicial)"
        )

        await self._checar_posicoes_abertas()
        if not self.r.exists("sniper_mode"):
            self.r.set("sniper_mode","false")

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
        try: self.r.ping()
        except Exception as e: falhas.append(f"Redis offline: {e}")

        try:
            import google.generativeai as genai
            if not os.getenv("GOOGLE_AI_API_KEY"): falhas.append("GOOGLE_AI_API_KEY ausente")
        except Exception as e: falhas.append(f"Google AI indisponível: {e}")

        if not PAPER_MODE:
            if not os.getenv("ANTHROPIC_API_KEY"): falhas.append("ANTHROPIC_API_KEY ausente")

        await self._checar_custo()
        await self._checar_metricas_operacao()

        if len(falhas) >= 2:
            self._alertar(f"🚨 GUARD WIN: {len(falhas)} FALHAS\n" +
                          "\n".join(f"  • {f}" for f in falhas) +
                          "\n⛔ Ciclos pausados.")
            self.r.set("sistema_pausado","true")
        elif falhas:
            for f in falhas: self._alertar(f"⚠️ GUARD WIN: {f}")

    async def _loop_monitoramento_capital(self):
        """Verifica nível de capital a cada 5 minutos durante operação."""
        while True:
            await asyncio.sleep(300)
            if self._capital_level_mgr:
                try:
                    await self._capital_level_mgr.verificar_nivel()
                except Exception as e:
                    logger.error(f"Erro ao verificar nível de capital: {e}")

    async def _loop_monitoramento_custo(self):
        while True:
            await asyncio.sleep(60)
            await self._checar_custo()

    async def _checar_custo(self):
        try:
            cost_path = os.getenv("COST_LOG_PATH","./logs/cost_today.json")
            with open(cost_path) as f: dados = json.load(f)
            total    = dados.get("total_usd", 0.0)
            orcamento = dados.get("orcamento_usd", float(os.getenv("DAILY_API_BUDGET_USD","2.00")))
            pct = total / orcamento * 100 if orcamento > 0 else 0
            self.r.set("custo_api_hoje", f"{total:.4f}")
            self.r.set("custo_pct", f"{pct:.1f}")
            if pct >= 80 and not self._custo_alerta_enviado:
                self._custo_alerta_enviado = True
                self._alertar(f"⚠️ COST MONITOR WIN: {pct:.0f}% do orçamento\n"
                              f"   ${total:.3f} / ${orcamento:.2f}")
            if pct >= 100:
                self._alertar(f"🛑 COST MONITOR WIN: ORÇAMENTO ESGOTADO!\n"
                              f"   ${total:.3f} / ${orcamento:.2f}")
        except (FileNotFoundError, json.JSONDecodeError): pass
        except Exception as e: logger.error(f"Erro ao checar custo: {e}")

    async def _checar_posicoes_abertas(self):
        try:
            posicao_str = self.r.get("posicao_aberta")
            if posicao_str:
                posicao = json.loads(posicao_str)
                if posicao.get("status") == "ABERTA":
                    self._alertar(
                        f"⚠️ REINÍCIO WIN COM POSIÇÃO ABERTA!\n"
                        f"   Direção: {posicao.get('direcao')}\n"
                        f"   Contratos: {posicao.get('contratos')}\n"
                        f"   Entrada: {posicao.get('entrada_real'):,.0f}\n"
                        f"   Stop: {posicao.get('stop_atual'):,.0f}\n"
                        f"   Verificar manualmente no Profit Pro!"
                    )
        except Exception as e: logger.error(f"Erro checar posições: {e}")

    async def _checar_metricas_operacao(self):
        try:
            losses  = int(self.r.get("losses_consecutivos") or 0)
            res_dia = float(self.r.get("resultado_dia_pct") or 0)
            stop_day = float(self.r.get("stop_day_pct_nivel") or 5.0)
            if losses >= 3: self._alertar(f"⛔ {losses} losses WIN → cool-down")
            if res_dia <= -(stop_day * 0.8) and res_dia > -stop_day:
                self._alertar(f"⚠️ Resultado WIN {res_dia:.2f}% — próximo stop-day (-{stop_day:.1f}%)")
            if res_dia <= -stop_day:
                self._alertar(f"🛑 STOP-DAY WIN atingido: {res_dia:.2f}%")
        except Exception as e: logger.error(f"Erro checar métricas: {e}")

    async def _loop_telegram_handler(self):
        while True:
            await asyncio.sleep(5)
            try:
                msg = self.r.lpop("telegram_inbox")
                if msg: await self._processar_comando(msg)
            except Exception as e: logger.error(f"Telegram handler WIN: {e}")

    async def _processar_comando(self, msg: str):
        msg_upper = msg.strip().upper()

        if msg_upper == "SNIPER ON":
            self.r.set("sniper_mode","true"); self._sniper_mode = True
            # Atualizar contratos com sniper
            if self._capital_level_mgr:
                await self._capital_level_mgr.verificar_nivel()
            self._alertar("🎯 SNIPER MODE WIN ATIVADO\n"
                         "   Score mínimo: 80\n"
                         "   Contratos: reduzido pelo nível atual\n"
                         "   Slippage máx: 8pts")

        elif msg_upper == "SNIPER OFF":
            self.r.set("sniper_mode","false"); self._sniper_mode = False
            if self._capital_level_mgr:
                await self._capital_level_mgr.verificar_nivel()
            self._alertar("📊 SNIPER MODE WIN DESATIVADO\n"
                         "   Parâmetros do nível atual restaurados.")

        elif msg_upper == "/STATUS":
            sniper  = self.r.get("sniper_mode") == "true"
            custo   = self.r.get("custo_api_hoje") or "0.0000"
            pct     = self.r.get("custo_pct") or "0.0"
            pausado = self.r.get("sistema_pausado") == "true"
            modo    = "🟡 PAPER" if PAPER_MODE else "🔴 REAL"
            nivel   = self.r.get("nome_nivel_capital") or "N/D"
            max_c   = self.r.get("max_contratos_efetivo") or "1"
            self._alertar(
                f"📊 STATUS Cyber Trade WIN v1.0\n"
                f"Modo: {modo} | Nível: {nivel}\n"
                f"Contratos disponíveis: {max_c}\n"
                f"Sniper: {'🎯 ON' if sniper else '📊 OFF'}\n"
                f"Custo hoje: ${custo} ({pct}%)\n"
                f"Sistema: {'⛔ PAUSADO' if pausado else '✅ ATIVO'}"
            )

        elif msg_upper == "/NIVEL" or msg_upper == "/CAPITAL":
            try:
                from infrastructure.redis_state import RedisState
                from utils.capital_levels import CapitalLevelManager
                rs = RedisState()
                capital = rs.get_capital() or float(os.getenv("CAPITAL_INICIAL","1000"))
                mgr = CapitalLevelManager(rs, None, None)
                self._alertar(mgr.relatorio_capital(capital))
            except Exception as e:
                self._alertar(f"Erro ao obter nível: {e}")

        elif msg_upper == "/CUSTO":
            try:
                cost_path = os.getenv("COST_LOG_PATH","./logs/cost_today.json")
                with open(cost_path) as f: dados = json.load(f)
                total    = dados.get("total_usd", 0)
                orcamento = dados.get("orcamento_usd", 2.0)
                agents   = dados.get("agents", {})
                linhas   = [f"💰 CUSTO API WIN — {dados.get('date','hoje')}\n"
                            f"Total: ${total:.4f}/${orcamento:.2f} ({total/orcamento*100:.0f}%)"]
                for nome, u in agents.items():
                    linhas.append(f"  {nome.upper():8s}: ${u['custo_usd']:.4f} | "
                                 f"{u['calls']} calls")
                self._alertar("\n".join(linhas))
            except Exception as e: self._alertar(f"Erro custo: {e}")

        elif msg_upper == "/PAUSAR":
            self.r.set("sistema_pausado","true")
            self._alertar("⛔ Sistema WIN PAUSADO via Telegram")

        elif msg_upper == "/OPERAR":
            self.r.delete("sistema_pausado")
            self._alertar("✅ Sistema WIN RETOMADO via Telegram")

    async def _loop_relatorio_diario(self):
        while True:
            agora = datetime.now()
            alvo  = agora.replace(hour=18, minute=0, second=0, microsecond=0)
            if agora >= alvo:
                alvo = alvo.replace(day=alvo.day + 1)
            await asyncio.sleep((alvo - agora).total_seconds())
            await self._relatorio_diario()

    async def _relatorio_diario(self):
        try:
            trades    = int(self.r.get("trades_dia") or 0)
            ganhos    = int(self.r.get("ganhos_dia") or 0)
            perdas    = trades - ganhos
            res_dia   = float(self.r.get("resultado_dia_reais") or 0)
            custo_hoje = float(self.r.get("custo_api_hoje") or 0)
            orcamento  = float(os.getenv("DAILY_API_BUDGET_USD","2.00"))
            sniper    = self.r.get("sniper_mode") == "true"
            modo      = "🟡 PAPER" if PAPER_MODE else "🔴 REAL"
            nivel     = self.r.get("nome_nivel_capital") or "N/D"
            acerto    = ganhos / trades * 100 if trades > 0 else 0

            # Capital atual
            try:
                from infrastructure.redis_state import RedisState
                from utils.capital_levels import get_nivel, progresso_para_proximo_marco
                rs = RedisState()
                capital = rs.get_capital() or float(os.getenv("CAPITAL_INICIAL","1000"))
                prog    = progresso_para_proximo_marco(capital)
                capital_ini = float(os.getenv("CAPITAL_INICIAL","1000"))
                ganho_total = capital - capital_ini
                capital_info = (
                    f"💰 Capital: R${capital:,.2f} (+R${ganho_total:,.2f})\n"
                    f"📈 Nível: {nivel}\n"
                )
                if prog["proximo"]:
                    capital_info += f"🎯 Próximo marco: R${prog['proximo']:,.0f} (faltam R${prog['faltam']:,.2f})\n"
            except Exception:
                capital_info = f"Nível: {nivel}\n"

            self._alertar(
                f"📊 CYBER TRADE WIN v1.0 — {datetime.now().strftime('%d/%m/%Y')}\n"
                f"Modo: {modo} | Sniper: {'🎯 ON' if sniper else '📊 OFF'}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{capital_info}"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Trades: {trades} | ✅ {ganhos} | ❌ {perdas}\n"
                f"Acerto: {acerto:.1f}% (meta >55%)\n"
                f"Resultado dia: R$ {res_dia:+.2f}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💰 Custo API: ${custo_hoje:.4f}/${orcamento:.2f} "
                f"({custo_hoje/orcamento*100:.0f}%)"
            )

            for key in ["trades_dia","ganhos_dia","resultado_dia_reais",
                        "score_medio_dia","violinada_count",
                        "breakeven_ativado_n","trailing_ativado_n",
                        "losses_consecutivos","custo_api_hoje","custo_pct"]:
                self.r.delete(key)
            self._custo_alerta_enviado = False

        except Exception as e: logger.error(f"Erro relatório diário WIN: {e}")

    def _alertar(self, msg: str):
        logger.info(f"[GUARD_WIN] {msg}")
        if self.tg:
            try: self.tg.alertar(msg)
            except Exception as e: logger.error(f"Telegram erro: {e}")


if __name__ == "__main__":
    guard = Guard()
    asyncio.run(guard.iniciar())
```

---
## `main.py` (WIN — adaptado)

```python
"""
CYBER TRADE WIN v1.0 — MAIN
==============================
Ponto de entrada para WINFUT (Mini Índice Futuro B3).

Diferenças vs WDO v5.2:
  - Símbolo: WINFUT (não WDOFUT)
  - Horário operacional: 09:15–17:30 BRT
  - CapitalLevelManager integrado
  - redis_state.set_preco_atual → "preco_atual_win"
  - ATR mínimo: 200 pts (não 3.0)
"""

import asyncio, logging, os
from datetime import datetime, time as dtime
from dotenv import load_dotenv
load_dotenv()

from infrastructure.llm_router    import LLMRouter, CostMonitor
from infrastructure.redis_state   import RedisState
from infrastructure.database      import Database
from infrastructure.telegram_bot  import TelegramBot
from infrastructure.profit_bridge import ProfitBridge
from agents.graph_agent   import GraphAgent
from agents.flow_agent    import FlowAgent
from agents.context_agent import ContextAgent
from agents.cyber_agent   import CyberAgent
from agents.exec_agent    import ExecAgent
from tape.tape_reader     import TapeReader
from utils.indicators     import calcular_todos
from utils.risk_manager   import RiskManager
from utils.cool_down      import CoolDown
from utils.capital_levels import CapitalLevelManager, get_nivel

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"),
                    format="%(asctime)s %(name)-16s %(levelname)s %(message)s")
logger = logging.getLogger("main_win")
PAPER_MODE   = os.getenv("PAPER_MODE","true").lower() == "true"
ATR_MIN_WIN  = float(os.getenv("ATR_MINIMO","200.0"))
HORARIO_FIM  = dtime(17, 30)  # WIN fecha às 17:30


class CyberTradeWIN:
    def __init__(self):
        self.tg      = TelegramBot()
        self.redis   = RedisState()
        self.db      = Database()
        self.profit  = ProfitBridge()
        self.tape    = TapeReader()
        self.risk    = RiskManager()
        self.cost_monitor = CostMonitor(alerta_callback=self.tg.alertar)
        self.router  = LLMRouter(self.cost_monitor)

        # Skill paths WIN
        from agents.graph_agent    import GraphAgent    as GA
        from agents.flow_agent     import FlowAgent     as FA
        from agents.context_agent  import ContextAgent  as CA

        self.graph   = GraphAgent(router=self.router)
        self.flow    = FlowAgent(router=self.router)
        self.context = ContextAgent(router=self.router)
        self.cyber   = CyberAgent(router=self.router, redis_state=self.redis)
        self.exec    = ExecAgent(redis_state=self.redis, db=self.db,
                                 tg=self.tg, profit_bridge=self.profit)
        self.cool_down = CoolDown(self.redis)
        self.capital_mgr = CapitalLevelManager(self.redis, self.tg, self.db)

    async def iniciar(self):
        # Aplicar nível inicial
        capital = self.redis.get_capital() or float(os.getenv("CAPITAL_INICIAL","1000"))
        nivel   = get_nivel(capital)
        self.capital_mgr.aplicar_nivel_ao_redis(nivel)

        modo   = "🟡 PAPER (Gemma 4)" if PAPER_MODE else "🔴 REAL (Claude)"
        budget = float(os.getenv("DAILY_API_BUDGET_USD","0.10"))
        m      = self.router.status()["modelos"]
        self.tg.alertar(
            f"✅ Cyber Trade WIN v1.0 | {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"Modo: {modo} | Budget: ${budget:.2f}/dia\n"
            f"Capital: R${capital:,.2f} | Nível: {nivel['nome']}\n"
            f"Max contratos: {nivel['max_contratos']} | Score mín: {nivel['score_minimo']}\n"
            f"Símbolo: WINFUT | Ponto: R$0,20/pt\n"
            f"CYBER:{m['cyber']} | Aguardando /operar"
        )

        await asyncio.gather(
            self._ciclo_trading(),
            self._ciclo_learn(),
            self._ciclo_telegram(),
        )

    async def _ciclo_trading(self):
        while True:
            hora = datetime.now().time()
            if hora < dtime(9,15) or hora >= HORARIO_FIM:
                await asyncio.sleep(30); continue
            if dtime(12,0) <= hora < dtime(13,30):
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

        if not self._pre_filtro(): return

        dados = await self._coletar(agora)

        resultados = await asyncio.gather(
            self.graph.analisar(dados),
            self.flow.analisar(dados),
            self.context.analisar(dados),
            return_exceptions=True,
        )
        graph_r, flow_r, context_r = resultados
        for nome, res in [("GRAPH",graph_r),("FLOW",flow_r),("CONTEXT",context_r)]:
            if isinstance(res, Exception):
                logger.error(f"{nome} WIN erro: {res}"); return

        latencia = asyncio.get_event_loop().time() - t0
        preco    = float(self.redis.get("preco_atual_win") or 0)
        estado   = self._estado(agora, latencia, preco)

        decisao = await self.cyber.decidir(
            {"estado_sistema": estado, "graph": graph_r,
             "flow": flow_r, "context": context_r}
        )

        self.db.registrar_ciclo({
            "timestamp": agora.isoformat(), "decisao": decisao.get("decisao"),
            "score": decisao.get("score_final",0),
            "motivo": decisao.get("motivo","")[:300],
            "custo_api_usd": self.cost_monitor.total_usd,
            "graph_sinal": graph_r.get("sinal"),
            "flow_forca": flow_r.get("forca_fluxo",0),
            "context_regime": context_r.get("regime_mercado"),
            "sniper_mode": estado.get("sniper_mode",False),
        })

        if decisao.get("decisao") == "ARMAR":
            await self.exec.armar(decisao)
            # Verificar nível após trade
            await self.capital_mgr.verificar_nivel()

        self.cool_down.verificar_e_ativar()
        logger.info(
            f"[WIN {agora.strftime('%H:%M')}] score={decisao.get('score_final',0)} "
            f"| {decisao.get('decisao')} | R${self.redis.get_capital() or 0:,.2f}"
        )

    def _pre_filtro(self) -> bool:
        atr_atual = float(self.redis.get("atr_atual_win") or ATR_MIN_WIN + 1)
        if atr_atual < ATR_MIN_WIN: return False
        if self.cost_monitor.orcamento_esgotado: return False
        stop_day = float(self.redis.get("stop_day_pct_nivel") or 5.0)
        if self.redis.get_resultado_dia_pct() <= -stop_day: return False
        if self.redis.get_operacoes_hoje() >= int(os.getenv("MAX_OPERACOES_DIA","5")): return False
        if self.redis.get_cool_down(): return False
        return True

    async def _coletar(self, agora: datetime) -> dict:
        loop = asyncio.get_event_loop()
        c5m  = await loop.run_in_executor(None, lambda: self.profit.get_candles("WINFUT",5,20))
        c15m = await loop.run_in_executor(None, lambda: self.profit.get_candles_15m("WINFUT",10))
        book = await loop.run_in_executor(None, lambda: self.profit.get_book("WINFUT"))
        tape = await loop.run_in_executor(None, lambda: self.profit.get_tape("WINFUT",50))
        preco = await loop.run_in_executor(None, self.profit.get_preco_atual)

        self.redis.set("preco_atual_win", str(preco))  # ← WIN usa chave diferente
        ind = calcular_todos(c5m, c15m)
        self.redis.set("atr_atual_win", str(ind.get("atr14_5m", 300.0)))
        tm  = self.tape.processar(novos_prints=tape, book_atual=book)
        self.redis.set_tape_metricas(tm)

        return {
            "symbol": "WINFUT", "timestamp": agora.isoformat(),
            "regime_mercado": "TRENDING_NORMAL",
            "candles_5min": c5m, "candles_15min": c15m,
            "indicadores": ind,
            "estrutura": {
                "maxima_dia": max((c["high"] for c in c5m), default=0),
                "minima_dia":  min((c["low"]  for c in c5m), default=0),
                "suportes": [], "resistencias": [], "range_dia_pct_usado": 0.5,
            },
            "candle_atual": c5m[-1] if c5m else {},
            "book_atual": book, "book_historico_3s": [],
            "tape_candle_completo": tape, "tape_ultimos_10s": tape[-10:],
            "tape_ultimos_3s": tape[-3:], "tape_metricas": tm,
            "delta": {"candle_atual": tm.get("delta_candle",0),
                      "acumulado_dia": 0, "candle_anterior": 0, "sequencia_positiva": 0},
            "sessao_americana": agora.hour >= 10,
            "minutos_desde_ny_open": max(0,(agora.hour*60+agora.minute)-(10*60+30)),
            "nivel_capital": self.redis.get("nome_nivel_capital") or "INICIANTE",
        }

    def _estado(self, agora, latencia, preco) -> dict:
        capital = self.redis.get_capital() or float(os.getenv("CAPITAL_INICIAL","1000"))
        return {
            "capital_atual": capital,
            "operacoes_hoje": self.redis.get_operacoes_hoje(),
            "losses_consecutivos": self.redis.get_losses_consecutivos(),
            "resultado_dia_percentual": self.redis.get_resultado_dia_pct(),
            "em_cool_down": self.redis.get_cool_down(),
            "equity_filter_10d": self.redis.get_equity_filter(),
            "modo": "PAPER" if PAPER_MODE else "REAL",
            "latencia_ciclo_segundos": round(latencia,2),
            "deslocamento_preco_desde_analise": 0.0,
            "sniper_mode": self.redis.get_sniper_mode(),
            "score_minimo_ativo": int(self.redis.get("score_minimo_nivel") or 72),
            "stop_day_pct": float(self.redis.get("stop_day_pct_nivel") or 5.0),
            "max_contratos_nivel": int(self.redis.get("max_contratos_nivel") or 1),
            "nome_nivel_capital": self.redis.get("nome_nivel_capital") or "INICIANTE",
            "custo_api_hoje_usd": self.cost_monitor.total_usd,
            "orcamento_restante_usd": self.cost_monitor.restante_usd,
        }

    async def _ciclo_learn(self):
        from learn.learn_agent import LearnAgent
        learn = LearnAgent(router=self.router, db=self.db, tg=self.tg)
        while True:
            agora = datetime.now()
            if agora.hour == 12 and agora.minute == 5:
                await learn.ciclo_almoco()
                await asyncio.sleep(90*60)
            await asyncio.sleep(30)

    async def _ciclo_telegram(self):
        from learn.learn_agent import LearnAgent
        learn = LearnAgent(router=self.router, db=self.db, tg=self.tg)
        while True:
            await asyncio.sleep(5)
            try:
                for msg in self.tg.obter_mensagens():
                    self.redis.rpush("telegram_inbox", msg)
                    mu = msg.upper()
                    if mu.startswith("LEARN,"):
                        await learn.comando_manual(msg)
                    elif any(mu.startswith(x) for x in ("APROVO","REJEITO","DADOS")):
                        await learn.tg_handler.processar_resposta(msg)
            except Exception as e:
                logger.error(f"Telegram WIN polling: {e}")


if __name__ == "__main__":
    ct = CyberTradeWIN()
    asyncio.run(ct.iniciar())
```

---
## `CHECKLIST_WIN.md`

```markdown
# CYBER TRADE WIN v1.0 — CHECKLIST DE DEPLOY
# =============================================

# ── DIFERENÇAS CRÍTICAS PARA VERIFICAR ────────────────────────────────
# [ ] VALOR_PONTO_WIN=0.20 no .env (NÃO alterar)
# [ ] PRECO_BASE_SIMULADO=132500 no .env
# [ ] ATR_MINIMO=200 no .env
# [ ] CAPITAL_INICIAL=1000 no .env
# [ ] BREAKEVEN_PTS=80 no .env
# [ ] TRAILING_FLOOR_PTS=100 no .env

# ── BLOCO 1: INFRAESTRUTURA ───────────────────────────────────────────
# [ ] Python 3.11+ instalado
# [ ] pip install -r requirements.txt sem erros
# [ ] .env criado do .env.template
# [ ] GOOGLE_AI_API_KEY válida
# [ ] Redis rodando: redis-cli ping → PONG
# [ ] Telegram Bot funcionando
# [ ] guard.py iniciado ANTES do main.py
# [ ] Verificar /status no Telegram → mostra Nível INICIANTE
# [ ] Verificar /nivel → mostra R$1.000 e progresso para R$2.000

# ── BLOCO 2: VALIDAR SISTEMA DE NÍVEIS ───────────────────────────────
# [ ] capital_levels.py importa sem erros
# [ ] CapitalLevelManager inicializa sem erros
# [ ] Simular capital=2500 → confirmar Nível 2 (2 contratos)
# [ ] Simular capital=5500 → confirmar Nível 4 (4 contratos)
# [ ] Alerta de marco configurado e disparando no Telegram
# [ ] Stop-day adaptativo sendo lido do Redis por CyberAgent

# ── BLOCO 3: VALIDAR CÁLCULOS WIN ─────────────────────────────────────
# [ ] resultado_reais = pts * 0.20 * contratos (NÃO pts * 5.0)
# [ ] Exemplo: +200 pts × 0.20 × 1 contrato = +R$40,00 ✓
# [ ] Exemplo: -100 pts × 0.20 × 2 contratos = -R$40,00 ✓
# [ ] risco_contrato = stop_pts * 0.20 (não * 5.0)
# [ ] sizing: R$10 risco ÷ (150 pts × 0.20) = 0.33 → 1 contrato ✓

# ── BLOCO 4: PAPER TRADING WIN (min 50 trades) ────────────────────────
# [ ] Sistema opera somente em WINFUT (não WDOFUT)
# [ ] ATR mínimo de 200 pts sendo respeitado (filtrar mercado morto)
# [ ] Context agent analisa SP500/VIX (não DXY)
# [ ] Preços em pontos WIN (~130.000+)
# [ ] Fechamento forçado às 17:30 BRT (não 16:00)
# [ ] Nível de capital atualizado corretamente após trades
# [ ] Alerta de marco quando capital cruza R$2.000, R$3.000 etc.
# [ ] Capital sendo reinvestido (nenhum saque no paper)

# ── BLOCO 5: TRANSIÇÃO PARA PRODUÇÃO ─────────────────────────────────
# [ ] PAPER_MODE=false
# [ ] Confirmar CYBER usa claude-sonnet-4-6
# [ ] Capital real: R$1.000 (não simular com mais)
# [ ] Contratos = 1 hard lock (nível 1)
# [ ] Kill switch manual no Profit Pro testado
# [ ] Confirmar saldo mínimo na corretora para margem:
#     - WIN margem intraday: ~R$80-150/contrato (verificar sua corretora)
#     - R$1.000 suporta 6-12 contratos de margem (mas risco limita a 1)

# ── MARCOS E METAS ────────────────────────────────────────────────────
# R$1.000 → R$2.000 = +100% (dobrar) → max 2 contratos desbloqueado
# R$2.000 → R$3.000 = +50%  → max 3 contratos
# R$3.000 → R$5.000 = +67%  → META: max 4 contratos (stop-day normaliza)
# R$5.000 → R$7.000 = +40%  → max 5 contratos desbloqueado
# R$7.000 → R$10.000 = +43% → MATURIDADE: modo pleno
#
# Estimativa conservadora:
#   5 trades/dia × 55% acerto × +80pts ganho médio (+3%/win) 
#   × R$16/trade com 1 contrato
#   ≈ R$22/dia líquido → R$5.000 em ~180 dias (~9 meses)
#   (Cresce com compounding — mais rápido conforme sobe de nível)
```

---

## ✅ RESUMO DAS ALTERAÇÕES (WDO → WIN)

| Arquivo | Alteração Principal |
|---------|---------------------|
| `.env.template` | Capital=1K, VALOR_PONTO=0.20, ATR_MIN=200 |
| `openclaw_win.json` | Símbolo WIN, capital_levels completo, 5 marcos |
| `utils/capital_levels.py` | **NOVO** — Gatilhos automáticos R$1K→R$10K |
| `profit_bridge.py` | WINFUT, preço 132.500, tick=5, ATR real |
| `exec_agent.py` | `resultado_reais = pts * 0.20 * contratos` |
| `cyber_agent.py` | Score/contratos dinâmicos por nível, max=5 |
| `risk_manager.py` | `risco_contrato = pts * 0.20` |
| `guard.py` | CapitalLevelManager, /nivel, /capital, 18h relatório |
| `main.py` | WINFUT, 17:30 fechamento, CapitalLevelManager |
| `context_skill_win.md` | **NOVO** — SP500/VIX/DI1F (sem DXY/Ptax) |
| `graph_skill_win.md` | **NOVO** — Escala WIN (~130.000 pts) |
| `cyber_skill_win.md` | **NOVO** — Score adaptativo, sizing WIN |

> **Atenção:** Os arquivos `tape_reader.py`, `indicators.py`, `database.py`, 
> `redis_state.py`, `telegram_bot.py`, `llm_router.py`, `base_agent.py`, 
> `cool_down.py` e todos os módulos do `learn/` são **reutilizados sem alteração**
> do CYBER TRADE v5.2 original.
