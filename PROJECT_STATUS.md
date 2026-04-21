# CYBER TRADE WIN — MASTER PROJECT STATUS
**Data:** 21/04/2026  
**Versão:** v2.1  
**Ambiente:** Windows + Python + Redis (Docker)

---

## 1. ARQUITETURA GERAL

```
┌─────────────────────────────────────────────────────────────┐
│                    CYBER TRADE WIN v2.1                    │
│                    8 Agentes Skynet                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ARCHITECT│  │MORPHEUS │  │ ORACLE   │  │  NEO    │   │
│  │Gemma 4  │  │Gemma 4  │  │Gemma 4   │  │Gemma 4  │   │
│  │ (GRÁFICO)│  │ (TAPE)  │  │ (CONTEXTO)│ │(DECISÃO)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └─────────────┴─────────────┴──────────────┘          │
│                           │                                 │
│                    ┌──────▼──────┐                         │
│                    │   EXEC      │                         │
│                    │  Execução   │                         │
│                    └──────┬──────┘                         │
│                           │                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ SENTINEL │  │  REAPER   │  │ CYBERDYNE│                │
│  │ (Guard)  │  │  (Custo)  │  │ (Learn)  │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  INFRA: Redis + SQLite + Telegram + DataProvider           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. STATUS COMPONENTES

| Componente | Status | Observação |
|------------|--------|------------|
| **Gemma 4 31B** | ✅ OK | FREE (TPM Ilimitado) |
| **Redis (Docker)** | ✅ OK | localhost:6379 |
| **Telegram Bot** | ✅ OK | @Cyber_winfut_bot |
| **Yahoo Finance** | ✅ OK | IBOV dados reais |
| **Dados WIN** | ⚠️ Simulado | Estimado do IBOV |
| **LLM Router** | ✅ OK | Fallback Gemma |
| **Database** | ✅ OK | SQLite |
| **Guard (Watchdog)** | ✅ OK | Cutoff 17:30 |
| **NTSL Relay** | ⏳ Pendente | Aguardando Profit Pro |
| **Conta Real** | ⏳ Pendente | Aguardando Santander |

---

## 3. FONTES DE DADOS

| Fonte | Tipo | Status | Custo |
|-------|------|--------|-------|
| Yahoo Finance (IBOV) | 5min | ✅ FREE | R$0 |
| WIN (estimado) | Calculado | ✅ Simulado | R$0 |
| Profit Pro | Tick | ⏳ Pendente | Grátis c/ 4 minis |
| B3 API | - | ❌ B2B only | - |

---

## 4. CONFIGURAÇÃO ATUAL

```env
PAPER_MODE=true
DATA_SOURCE=yahoo
VALOR_PONTO_WIN=0.20
CAPITAL_INICIAL=1000.00
RISCO_POR_TRADE_PCT=1.0
STOP_DAY_PCT=5.0
MAX_OPERACOES_DIA=5
ATR_MINIMO=200.0
SCORE_MIN_NORMAL=72
RR_MINIMO=1.5
```

---

## 5. SISTEMA DE NÍVEIS

| Nível | Capital | Max Contratos | Score Min | Stop-Day |
|-------|---------|----------------|-----------|----------|
| 1 🌱 | R$1.000–1.999 | 1 | 72 | -5% |
| 2 📈 | R$2.000–2.999 | 2 | 70 | -4% |
| 3 🚀 | R$3.000–4.999 | 3 | 68 | -3,5% |
| 4 💰 | R$5.000–6.999 | 4 | 65 | -2,5% |
| 5 🏆 | R$7.000–9.999 | 5 | 65 | -2,5% |
| 6 ⭐ | R$10.000+ | 5 | 65 | -2,5% |

---

## 6. PRÓXIMOS PASSOS

| # | Passo | Status |
|---|-------|--------|
| 1 | Setup ambiente | ✅ Concluído |
| 2 | Redis + Docker | ✅ Concluído |
| 3 | Telegram Bot | ✅ Concluído |
| 4 | Yahoo Finance | ✅ Concluído |
| 5 | **Teste completo LLM** | ⏭️ **AGORA** |
| 6 | Integração Profit Pro | ⏳ Pendente |
| 7 | Validação 8 semanas | ⏳ Pendente |
| 8 | Conta real Santander | ⏳ Pendente |

---

## 7. CUSTOS

| Item | Custo |
|------|-------|
| Gemma 4 (Google AI) | R$0 (TPM Ilimitado) |
| Redis (Docker) | R$0 |
| Yahoo Finance | R$0 |
| Telegram | R$0 |
| **Total Paper** | **R$0** |

**Produção (após 8 semanas):**
- Santander Corretora: Grátis com 4 minis/mês
- Profit Pro: Grátis com 4 minis/mês
- **Total Produção:** **R$0**

---

## 8. REGRAS IMUTÁVEIS

```
1. PAPER_MODE=true SEMPRE como padrão
2. Nunca operar capital real sem ≥ 8 semanas de validação
3. VALOR_PONTO_WIN = 0.20 em TODOS os módulos
4. RISCO_POR_TRADE = 1% — nunca alterável
5. R:R mínimo = 1.5 — nunca autorizar abaixo
6. WIN fecha às 17:30 BRT
7. Stop > 2×ATR — NUNCA permitido
```

---

## 9. REPOSITÓRIO

**GitHub:** https://github.com/mlpreto1/Cyber-Trade-WINFUT

**Arquivos principais:**
- `main.py` — Loop principal
- `guard.py` — Watchdog
- `agents/` — 8 agentes
- `infrastructure/` — Redis, LLM, DB, Telegram
- `skills/` — Prompts dos agentes
- `.env` — Configuração

---

*Documento gerado em 21/04/2026 — Cyber Trade WIN v2.1*
