# 🚀 Cyber Trade — Conversa Completa: Corretoras, ProfitDLL & Deploy WIN v2.1
**Data:** 19/04/2026  
**Projeto:** Cyber Trade WIN v2.1 + WDO v7.1 — Scalping B3  
**Ambiente:** Windows 11 + WSL2

---

## PARTE 1 — CORRETORAS & PLATAFORMA

### 1.1 Pergunta Central
Qual a corretora mais indicada para o projeto, gratuita de preferência? O Profit Pro tem que ser o Pro?

### 1.2 Análise Inicial — Clear Corretora
- Primeira corretora do Brasil com corretagem zero
- Profit Pro gratuito com RLP ativo + 5 minicontratos em dias distintos/mês
- **Alerta:** A partir de maio/2026, Profit Pro custa R$160/mês se não atingir condição

### 1.3 Profit Pro — É Obrigatório?

| Situação | Necessário? |
|---|---|
| Paper trading (simulação) | ❌ NÃO — Python puro + Redis simula |
| Automação via NTSL | ✅ SIM — obrigatório |
| Automação via ProfitDLL Python | ❌ NÃO — produto separado |

**Regra:** O módulo de Automação da Nelogica usa **NTSL**, não Python. Gratuito em simulação, pago em conta real.

---

## PARTE 2 — COMPARATIVO DE CORRETORAS

### 2.1 Condições de Gratuidade do Profit Pro

| Corretora | Minis/mês | RLP obrigatório? | Custo sem condição |
|---|---|---|---|
| **Santander (ex-Toro)** | 4 minis/30 dias | ❌ Não | Plataforma pausada, sem cobrança |
| Clear | 5 minis em dias distintos | ✅ Sim | R$ 160/mês (mai/2026) |
| Rico | 10 minis/mês | ✅ Sim | ~R$ 160/mês |
| CM Capital | 50 minis/30 dias | ✅ Sim | R$ 189,90/mês |
| Modalmais | 1 mini/mês + RLP | ✅ Sim | R$ 139,90/mês |

### 2.2 Corretagem WDO/WIN

| Corretora | Corretagem | Observação |
|---|---|---|
| **Santander** | Zero | Com **ou sem** RLP — única do mercado |
| Clear | Zero | Com RLP ativo |
| Rico | Zero | Com RLP ativo |
| CM Capital | Zero | Com RLP ativo |

### 2.3 Infraestrutura

| Corretora | DMA | Relevância para Scalping |
|---|---|---|
| **Santander** | **DMA4 — co-location dentro da B3** | **Alta — latência mínima do Brasil** |
| Clear | DMA2 | OK para scalping normal |
| Rico | DMA2/3 | OK para scalping normal |
| CM Capital | DMA2 | OK para scalping normal |

### 2.4 Módulo de Automação (conta real)

- **CM Capital:** tem isenção própria — Automação Basic R$99,50/mês, isento com 200 minis/mês
- Demais corretoras: via Nelogica Store, preço padrão

---

## PARTE 3 — ALERTA CRÍTICO: TORO NÃO EXISTE MAIS

A Toro Investimentos foi incorporada ao Santander e deixou de existir como corretora independente a partir de dezembro/2025. A migração de clientes foi automática até fevereiro/2026.

**O Profit Pro está confirmado na Santander Corretora:**
- Gratuito com 4 minis/30 dias
- Sem cobrança por inatividade (plataforma pausada)
- DMA4 mantido
- Sem RLP obrigatório

---

## PARTE 4 — O PROBLEMA DO PAPER TRADING

Durante paper trading, zero minis reais são executados. Análise por corretora:

| Corretora | Situação durante paper trading |
|---|---|
| Clear | ❌ Cobra R$160/mês |
| Rico | ❌ Cobra ~R$160/mês |
| CM Capital | ❌ Cobra R$189,90/mês |
| **Santander** | ✅ Plataforma pausada, **sem cobrança** |

**Mas a solução real é melhor ainda:** o Cyber Trade v5.2/WIN v2.1 **não precisa do Profit Pro durante paper trading**. O EXEC agent é Python puro e simula execuções internamente via Redis.

```
Paper Trading — Custo: R$ 0,00
─────────────────────────────────
GRAPH / FLOW / CONTEXT  →  Gemma 4 (Google AI Studio, grátis)
CYBER                   →  Gemma 4 (PAPER_MODE=true)
EXEC                    →  Python puro, simula ordens no Redis
Corretora               →  Não necessária
Profit Pro              →  Não necessário
```

---

## PARTE 5 — PROFITDLL: A DECISÃO FINAL

### Os 3 Caminhos de Integração Python → B3

**Caminho 1 — ProfitDLL pura (produto institucional)**
```
Python → ProfitDLL.dll → Servidores Nelogica → B3
```
- Licença separada, paga, negociada via `corporativo@nelogica.com.br`
- Sem preço público, sem plano pessoa física
- **Conclusão: produto para peixe grande — fundos, fintechs, mesas prop**
- **❌ Descartado para o projeto**

**Caminho 2 — Profit Pro + Módulo NTSL**
```
Profit Pro (aberto) → Editor Estratégias NTSL → B3
```
- Robôs escritos em NTSL, não Python
- Profit Pro precisa ficar aberto durante o pregão
- **❌ Não serve diretamente — EXEC agent é Python**

**Caminho 3 — Python → Redis → NTSL Relay ✅ ESCOLHIDO**
```
Python (CYBER/EXEC) → arquivo/Redis → NTSL mínimo → Profit Pro → B3
```
- Profit Pro fica aberto como "terminal de execução"
- Python escreve sinais no Redis
- Uma estratégia NTSL mínima (~20 linhas) lê o sinal e dispara a ordem
- **Toda a inteligência fica 100% em Python**
- **Custo adicional: R$ 0,00**

### Conclusão ProfitDLL

```
ProfitDLL:  ❌ Produto institucional — sem acesso PF documentado
            Pesquisa exaustiva não encontrou caminho para pessoa física
            O repositório GitHub oficial aponta para negociação B2B
            Encerrado o assunto
```

---

## PARTE 6 — DECISÃO FINAL DE STACK

```
┌─────────────────────────────────────────────────┐
│           CYBER TRADE — DOIS ROBÔS              │
│                                                  │
│  Python (7-8 agentes) → Redis → NTSL Relay      │
│                                                  │
│  ┌──────────────┐    ┌──────────────┐            │
│  │  WIN v2.1    │    │  WDO v7.1    │            │
│  │  WINFUT      │    │  WDOFUT      │            │
│  └──────┬───────┘    └──────┬───────┘            │
│         └─────────┬─────────┘                    │
│                   ▼                              │
│         Profit Pro (1 licença)                   │
│         Santander Corretora                      │
│         DMA4 — co-location B3                    │
│         Grátis com 4 minis/mês                   │
└─────────────────────────────────────────────────┘

Corretora:         Santander Corretora (conta já existente no banco)
Plataforma:        Profit Pro — grátis com 4 minis/30 dias
Latência:          DMA4 — melhor do Brasil
Corretagem:        Zero (com ou sem RLP)
ProfitDLL:         Descartada — produto institucional
Integração Python: Caminho 3 — relay Redis→NTSL
Dois robôs:        Uma licença Profit Pro, duas estratégias simultâneas
Custo paper:       R$ 0,00
Custo produção:    R$ 0,00 (com ≥4 minis/mês)
```

### Sequência de Deploy

| Fase | Ação | Custo |
|---|---|---|
| Agora | Paper trading WIN v2.1 — Python + Redis, sem corretora | R$ 0,00 |
| Após 8 semanas | Conta real WIN, Santander Corretora, 1 contrato | R$ 0,00 |
| Escala | WDO v7.1 ativado no mesmo Profit Pro | R$ 0,00 |

---

## PARTE 7 — DEPLOY WIN v2.1: PASSO A PASSO

### Ambiente
- Windows 11 + WSL2 instalado
- Python 3.11+ instalado
- Deploy do zero

### STEP 0 — Pré-requisitos (antes de qualquer comando)

Separar:
- **Google AI Studio API Key** — gratuita em [aistudio.google.com](https://aistudio.google.com) → "Get API Key"
- **Telegram Bot Token** — via [@BotFather](https://t.me/BotFather) → `/newbot`
- **Telegram Chat ID** — via [@userinfobot](https://t.me/userinfobot)
- Anthropic API Key (opcional para paper — só Gemma é usada)

### STEP 1 — Abrir WSL2 e verificar Python

```bash
# Win + S → wsl → Enter
python3 --version
# Esperado: Python 3.11.x ou superior
```

### STEP 2 — Instalar Redis no WSL2

```bash
sudo apt update && sudo apt install -y redis-server
sudo service redis-server start
redis-cli ping
# Esperado: PONG ✅
```

### STEP 3 — Criar estrutura de pastas

```bash
mkdir -p cyber_trade_win/{agents,tape,infrastructure,utils,skills,config,data/win_b3/{candles,ticks,synthetic},logs,scripts}
cd cyber_trade_win
find . -type d | sort
```

### STEP 4 — Criar requirements.txt

```bash
cat > requirements.txt << 'EOF'
# Core
python-dotenv==1.0.1
redis==5.0.4
aiohttp==3.9.5
asyncio-mqtt==0.16.2

# LLM
anthropic==0.28.0
google-generativeai==0.7.2

# Data
polars==0.20.31
numpy==1.26.4

# Database
sqlalchemy==2.0.30

# Telegram
python-telegram-bot==21.3

# Monitoring
psutil==5.9.8
httpx==0.27.0

# Utils
pytz==2024.1
EOF
```

### STEP 5 — Criar venv e instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import redis, anthropic, google.generativeai, polars, telegram; print('✅ Todas dependências OK')"
```

### STEP 6 — Criar .env

```bash
cat > .env << 'EOF'
# ============================================================
# CYBER TRADE WIN v2.1 — CONFIGURAÇÃO
# ⚠️ NUNCA subir este arquivo para git
# ============================================================

# === APIs ===
ANTHROPIC_API_KEY=sk-ant-api03-COLE_SUA_KEY_AQUI
GOOGLE_AI_API_KEY=COLE_SUA_KEY_AQUI

# === MODO OPERAÇÃO ===
PAPER_MODE=true

# === TELEGRAM ===
TELEGRAM_BOT_TOKEN=COLE_SEU_TOKEN_AQUI
TELEGRAM_CHAT_ID=COLE_SEU_CHAT_ID_AQUI

# === CAPITAL WIN ===
CAPITAL_INICIAL=1000.00
VALOR_PONTO_WIN=0.20
PRECO_BASE_SIMULADO=132500.0

# === RISCO ===
RISCO_POR_TRADE_PCT=1.0
STOP_DAY_PCT=5.0
MAX_OPERACOES_DIA=5
ATR_MINIMO=200.0
MAX_CONTRATOS_NORMAL=1
SCORE_MIN_NORMAL=72
RR_MINIMO=1.5
SLIPPAGE_MAX_PTS=10.0
LATENCIA_MAX_S=5.0
COOL_DOWN_LOSSES=3
COOL_DOWN_MINUTOS=30
BREAKEVEN_PTS=60.0
TRAILING_FLOOR_PTS=80.0

# === REDIS ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# === DB ===
DB_PATH=./cyber_trade_win.db
MEMORY_DB_PATH=./learn_memory_win.db
OPENCLAW_JSON_PATH=./config/openclaw_win.json

# === CUSTOS ===
DAILY_API_BUDGET_USD=0.10
COST_ALERT_THRESHOLD_PCT=80
COST_LOG_PATH=./logs/cost_today.json

# === SISTEMA ===
LOG_LEVEL=INFO
EOF

# Editar com suas chaves reais
nano .env
# Ctrl+X → Y → Enter para salvar
```

### STEP 7 — Criar .gitignore

```bash
cat > .gitignore << 'EOF'
.env
.venv/
__pycache__/
*.pyc
*.db
logs/
*.log
credentials.json
data/win_b3/ticks/
data/win_b3/candles/
EOF
```

### STEP 7 — Checkpoint: Teste do ambiente

```bash
python3 - << 'EOF'
import os
from dotenv import load_dotenv
import redis

load_dotenv()

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set('test_cyber', 'WIN_OK')
val = r.get('test_cyber')
print(f"Redis: {'✅ OK' if val == 'WIN_OK' else '❌ FALHOU'}")

capital = os.getenv('CAPITAL_INICIAL')
modo = os.getenv('PAPER_MODE')
valor_ponto = os.getenv('VALOR_PONTO_WIN')
print(f"PAPER_MODE: {modo}")
print(f"CAPITAL_INICIAL: R$ {capital}")
print(f"VALOR_PONTO_WIN: R$ {valor_ponto}")
print("✅ Ambiente OK" if all([capital, modo, valor_ponto]) else "❌ Verifique o .env")
EOF
```

**Resultado esperado:**
```
Redis: ✅ OK
PAPER_MODE: true
CAPITAL_INICIAL: R$ 1000.00
VALOR_PONTO_WIN: R$ 0.20
✅ Ambiente OK
```

### Próximos STEPs (após checkpoint passar)
- STEP 8: Teste do Telegram Bot
- STEP 9: Arquivo de código — guard.py
- STEP 10: Arquivo de código — main.py
- STEP 11: Agentes (infrastructure, utils, agents)
- STEP 12: Primeira execução paper trading

---

## PARTE 8 — PARÂMETROS CRÍTICOS WIN v2.1

```
VALOR_PONTO_WIN = 0.20   ← R$0,20/ponto/contrato (NÃO é R$5,00!)
HORARIO_CUTOFF  = 17:30  ← WIN fecha 17:30 BRT (NÃO é 16:00 como WDO)
ATR_MINIMO      = 200    ← mínimo para operar (mercado morto = ignorar)
RISCO_POR_TRADE = 1%     ← sagrado, nunca alterável pelo LEARN
STOP_DAY        = 5%     ← Nível 1, adaptativo por nível de capital
```

```python
# Cálculo correto WIN:
resultado_reais = resultado_pts * 0.20 * contratos

# Exemplos:
# +200pts × 0.20 × 1 contrato = +R$40,00  ✅
# +200pts × 5.00 × 1 contrato = +R$1.000  ❌ ERRADO (confusão com WDO)
```

---

## PARTE 9 — SISTEMA DE NÍVEIS WIN v2.1

| Nível | Capital | Max Contratos | Score Min | Stop-Day |
|---|---|---|---|---|
| 1 🌱 | R$1.000–1.999 | 1 | 72 | -5% |
| 2 📈 | R$2.000–2.999 | 2 | 70 | -4% |
| 3 🚀 | R$3.000–4.999 | 3 | 68 | -3,5% |
| 4 💰 | R$5.000–6.999 | 4 | 65 | -2,5% ★ META |
| 5 🏆 | R$7.000–9.999 | 5 | 65 | -2,5% |
| 6 ⭐ | R$10.000+ | 5 | 65 | -2,5% ★ MATURIDADE |

Gatilho automático ao cruzar marcos: Telegram + Redis + SQLite + ajuste de parâmetros.

---

## PARTE 10 — REGRAS IMUTÁVEIS

```
1. PAPER_MODE=true SEMPRE como padrão
2. Nunca operar capital real sem ≥ 8 semanas de validação
3. Métricas mínimas: acerto ≥ 55%, Profit Factor ≥ 1.2, drawdown ≤ 5%
4. VALOR_PONTO_WIN = 0.20 em TODOS os módulos — sem exceção
5. WIN fecha às 17:30 BRT — fechar posições até 17:15
6. RISCO_POR_TRADE = 1% — nunca alterável pelo LEARN
7. R:R mínimo = 1.5 — nunca autorizar abaixo disso
8. Stop > 2×ATR_WIN — NUNCA permitido
```

---

*Documento gerado em 19/04/2026 — Cyber Trade WIN v2.1 + WDO v7.1*  
*Ponto focal: Claude (Anthropic) — decisões consolidadas e validadas*
