# 🏦 Cyber Trade v5.2 — Análise de Corretoras & Plataforma
**Data:** 18/04/2026  
**Projeto:** Cyber Trade v5.2 — Scalping WDO na B3  
**Tema:** Escolha de corretora gratuita + requisitos do Profit Pro

---

## 1. Corretora Recomendada — Análise Inicial

### Por que Clear Corretora (resposta inicial)?
- Primeira corretora do Brasil com corretagem zero (todos os produtos)
- Profit Pro gratuito com RLP ativo + 5 minicontratos em dias distintos/mês
- Sem taxa de custódia e manutenção de conta
- **Alerta:** A partir de maio/2026, Profit Pro custa R$160/mês se não atingir a condição

### Alternativa — modalmais (XP Group)
- Profit Pro gratuito operando apenas 1 WDO ou WIN/mês com RLP ativo
- Condição mais fácil de atingir

---

## 2. Profit Pro — É Obrigatório?

**Sim. O Profit Pro (ou Ultra) é obrigatório para automação.** A Nelogica só libera o módulo de Automação de Estratégias (robô em conta real) para usuários do Profit Pro ou Ultra.

| Situação | Custo |
|---|---|
| Paper trading (simulação) | **R$ 0,00** — gratuito no Profit Pro |
| 7 dias em conta real (teste) | **R$ 0,00** — período de teste |
| Conta real produção | Módulo pago na Nelogica Store |

### ⚠️ Ponto Crítico de Arquitetura
O módulo de automação do Profit usa **NTSL** (Nelogica Trading System Language), não Python. O EXEC agent do Cyber Trade é Python. Há dois caminhos:

- **Opção A:** Reescrever lógica do EXEC em NTSL (mais simples, menos flexível)
- **Opção B:** Python orquestra → NTSL faz relay de ordens → mantém os 7 agentes intactos ✅

A automação do Profit **roda no hardware local** — o Profit precisa estar aberto durante o pregão.

---

## 3. Comparativo Completo: Clear vs Rico vs Toro vs CM Capital

### 3.1 Condições de Gratuidade do Profit Pro

| Corretora | Minis/mês p/ Profit Pro grátis | RLP obrigatório? | Custo sem condição |
|---|---|---|---|
| **Clear** | 5 minis em dias distintos | Sim | R$ 160/mês *(maio/2026)* |
| **Rico** | 10 minicontratos/mês | Sim | ~R$ 160/mês |
| **Toro** | 4 minicontratos em 30 dias | **Não** | Plataforma **pausada**, sem cobrança |
| **CM Capital** | 50 minicontratos a cada 30 dias | Sim | R$ 189,90/mês |

🏆 **Vencedora em facilidade:** Toro — menor exigência + sem RLP + sem cobrança por inatividade.

---

### 3.2 Corretagem

| Corretora | Corretagem WDO | Observação |
|---|---|---|
| Clear | Zero | Com RLP ativo |
| Rico | Zero | Com RLP ativo |
| **Toro** | **Zero** | **Com ou sem RLP — única do mercado** |
| CM Capital | Zero | Com RLP ativo |

🏆 **Vencedora:** Toro — corretagem zero independente de RLP.

---

### 3.3 Infraestrutura e Latência — CRÍTICO para Scalping WDO

| Corretora | Infraestrutura | Relevância |
|---|---|---|
| Clear | DMA2 padrão | OK para scalping normal |
| Rico | DMA2/DMA3 | OK para scalping normal |
| **Toro** | **Co-location DMA4** — servidores físicos dentro da B3, latência de milissegundos igual a fundos de alta frequência | **Alta — vantagem real no tick-a-tick** |
| CM Capital | DMA2 | OK para scalping normal |

🏆 **Vencedora absoluta:** Toro — DMA4 é a menor latência possível no Brasil.  
Para scalping de WDO com o EXEC agent do Cyber Trade, microsegundos impactam diretamente o slippage.

---

### 3.4 Módulo de Automação (robô em conta real)

**CM Capital tem diferencial relevante:** oferece isenção do módulo de automação por volume:

| Plano CM Capital | Preço | Isenção com |
|---|---|---|
| Automação Basic | R$ 99,50/mês | 200 minicontratos/mês |
| Automação Plus | R$ 276,60/mês | 600 minicontratos/mês |
| Automação Premium | R$ 431,60/mês | 900 minicontratos/mês |

Até 50 estratégias simultâneas, gerenciamento de risco por conta/estratégia/carteira.

> ⚠️ **Confirmado:** Profit One **não é compatível** com automações — Profit Pro é obrigatório.

---

### 3.5 Outras Diferenças

| Critério | Clear | Rico | Toro | CM Capital |
|---|---|---|---|---|
| Grupo econômico | XP Inc. | XP Inc. | Santander | Independente (1986) |
| Scalper Pro disponível | Não | Não | Não | Sim (300 minis/mês) |
| Profit Ultra disponível | Não | Não | Não | Sim (230 minis/mês) |
| Automação integrada extra | Não | Não | Não | SmarttBot integrado |
| Conflito de interesses | XP é market maker | XP é market maker | Santander é contraparte | **Independente** ✅ |

---

## 4. O Problema do Paper Trading

> **"Em paper trading não vamos atingir a exigência de nenhuma corretora — terá custo."**

Análise real:

| Corretora | Situação durante paper trading |
|---|---|
| Clear | ❌ Cobrará R$160/mês |
| Rico | ❌ Cobrará ~R$160/mês |
| CM Capital | ❌ Cobrará R$189,90/mês |
| **Toro** | ✅ Plataforma **pausada sem cobrança** — reativa grátis quando quiser |

**Mas há uma solução melhor:**

---

## 5. Solução Arquitetural — Paper Trading Sem Custo de Corretora

O Cyber Trade v5.2 **não precisa do Profit Pro durante o paper trading**. O EXEC agent é Python puro e pode simular execuções internamente:

```
Paper Trading do Cyber Trade v5.2:
───────────────────────────────────
GRAPH / FLOW / CONTEXT  →  Gemma 4 via Google AI Studio (grátis)
CYBER                   →  Gemma 4 (PAPER_MODE=true, grátis)
EXEC                    →  Python puro, simula ordens no Redis
GUARD                   →  monitora e envia alertas via Telegram
LEARN                   →  roda no horário de almoço normalmente
Corretora               →  não necessária nesta fase
Profit Pro              →  não necessário nesta fase
─────────────────────────────────────────────
Custo total paper trading  →  R$ 0,00
```

---

## 6. Quando o Profit Pro Vira Obrigatório

Somente na transição para **conta real**. Duas opções:

### Opção A — Execução via NTSL no Profit Pro
- Requer Profit Pro ativo + módulo de automação pago
- Com Toro: 4 minis reais no primeiro dia = Profit Pro grátis

### Opção B — Execução via API REST da corretora direto no Python *(a investigar)*
- O EXEC agent Python envia ordens via HTTP sem o Profit Pro aberto
- Profit Pro vira opcional, usado apenas para monitoramento visual
- **Elimina custo de plataforma mesmo em produção**

---

## 7. Recomendação Final

### Fase Paper Trading (agora)
→ **Corretora: nenhuma necessária**  
→ **Profit Pro: não necessário**  
→ **Custo: R$ 0,00**

### Fase Produção (após validação)

| Volume de trades | Corretora recomendada | Motivo |
|---|---|---|
| < 100 minis/mês | **Toro** | DMA4 + zero burocracia + sem RLP obrigatório |
| > 200 minis/mês | **CM Capital** | Isenção do módulo de automação + ecossistema institucional |

**Ação prática:** Abrir conta nas duas (gratuito) durante o paper trading, e decidir na produção com base no volume real gerado pelo bot.

---

## 8. Próximos Passos Mapeados

- [ ] Validar se alguma corretora tem API REST de ordens acessível para Python (eliminaria necessidade do Profit Pro em produção)
- [ ] Executar paper trading completo com PAPER_MODE=true
- [ ] Medir volume de trades/mês gerado pelo Cyber Trade em simulação
- [ ] Decidir corretora de produção com base no volume real
- [ ] Contratar módulo de Automação Nelogica apenas quando for para conta real

---

*Documento gerado em 18/04/2026 — Cyber Trade v5.2 Project*
