# dashboard.py
# Cyber Trade WIN v3.0 — Visual Dashboard com Refresh Real

import streamlit as st
import redis
import json
import time
from datetime import datetime

st.set_page_config(page_title="Cyber Trade WIN v3.0", page_icon="📈", layout="wide")

st.title("📈 Cyber Trade WIN v3.0")

COLORS = {
    "NEO": "#00ff00",
    "ARCHITECT": "#00ffff",
    "MORPHEUS": "#ff00ff",
    "ORACLE": "#ffff00",
    "SYSTEM": "#ff6600",
    "EXEC": "#00ffcc",
    "CYCLE": "#ffffff",
}

def conectar_redis():
    try:
        return redis.Redis(host='localhost', port=6379, decode_responses=True)
    except Exception:
        return None

def get_redis_value(r, key):
    try:
        return r.get(key)
    except:
        return None

def get_logs(r):
    logs = []
    if not r:
        return logs
    try:
        for key in r.scan_iter("log:*"):
            data = r.get(key)
            if data:
                try:
                    logs.append(json.loads(data))
                except:
                    pass
    except:
        pass
    return sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:50]

placeholder = st.empty()

_redis_conn = conectar_redis()

while True:
    with placeholder.container():
        r = _redis_conn
        if r:
            try:
                r.ping()
            except Exception:
                _redis_conn = conectar_redis()
                r = _redis_conn

        st.title("📈 Cyber Trade WIN v3.0")

        if r:
            col1, col2, col3, col4, col5 = st.columns(5)

            preco = get_redis_value(r, "preco_atual_win")
            with col1:
                st.metric("WIN", f"{preco or '---'}")

            modo = get_redis_value(r, "modo") or "PAPER"
            with col2:
                st.metric("Modo", modo)

            sniper = get_redis_value(r, "sniper_mode") or "false"
            with col3:
                st.metric("Sniper", sniper.upper())

            ciclo = get_redis_value(r, "ciclo_atual") or "?"
            with col4:
                st.metric("Ciclo", ciclo)

            info_dados_str = get_redis_value(r, "info_dados")
            info_dados = {}
            if info_dados_str:
                try:
                    info_dados = json.loads(info_dados_str)
                except:
                    pass
            data_candle = info_dados.get("ultimo_candle", "---")
            with col5:
                st.metric("Data Dados", data_candle)

            st.divider()

            st.subheader("🎯 Logs dos Agentes (tempo real)")

            logs = get_logs(r)

            if logs:
                for log in logs[:12]:
                    agente = log.get("agente", "SYSTEM")
                    mensagem = log.get("mensagem", "")
                    timestamp = log.get("timestamp", "")
                    ts_curto = timestamp[-12:-5] if timestamp else ""
                    cor = COLORS.get(agente, "#ffffff")
                    st.markdown(f"<span style='color:{cor}; font-size:13px'>**[{ts_curto}] {agente}:**</span> {mensagem}", unsafe_allow_html=True)
            else:
                st.info("Aguardando ciclos... Execute main.py")
                st.code("python main.py", language="bash")

            st.divider()

            col_graph, col_flow = st.columns(2)

            with col_graph:
                st.subheader("📊 ARCHITECT (Gráfico)")
                sinal = get_redis_value(r, "sinal_grafico") or "NEUTRO"
                conf = get_redis_value(r, "confianca_grafico") or "0"
                tendencia = get_redis_value(r, "tendencia_grafico") or "INDEFINIDA"
                ema9 = get_redis_value(r, "ema9_grafico") or "---"
                ema21 = get_redis_value(r, "ema21_grafico") or "---"
                atr = get_redis_value(r, "atr_grafico") or "---"
                rsi = get_redis_value(r, "rsi_grafico") or "---"

                st.write(f"**Sinal:** {sinal}")
                st.write(f"**Confiança:** {conf}")
                st.write(f"**Tendência:** {tendencia}")
                st.write(f"**EMA9:** {ema9}")
                st.write(f"**EMA21:** {ema21}")
                st.write(f"**ATR14:** {atr}")
                st.write(f"**RSI14:** {rsi}")

            with col_flow:
                st.subheader("🌊 MORPHEUS (Fluxo)")
                fluxo_dir = get_redis_value(r, "direcao_fluxo") or "NEUTRO"
                fluxo_forca = get_redis_value(r, "forca_fluxo") or "0"
                cvd = get_redis_value(r, "cvd_total") or "0"

                st.write(f"**Direção:** {fluxo_dir}")
                st.write(f"**Força:** {fluxo_forca}")
                st.write(f"**CVD:** {cvd}")

            st.divider()

            st.subheader("🔮 ORACLE (Contexto)")
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                regime = get_redis_value(r, "regime_mercado") or "NORMAL"
                status_macro = get_redis_value(r, "status_macro") or "NORMAL"
                tendencia_merc = get_redis_value(r, "tendencia_mercado") or "INDEFINIDA"

                st.write(f"**Regime:** {regime}")
                st.write(f"**Status Macro:** {status_macro}")
                st.write(f"**Tendência:** {tendencia_merc}")

            with col_o2:
                ibov = get_redis_value(r, "ibov_variacao") or "0"
                hora = datetime.now().strftime("%H:%M:%S")

                st.write(f"**IBOV:** {ibov}%")
                st.write(f"**Hora:** {hora}")

            st.divider()

            st.subheader("📜 Log Completo")
            for log in logs:
                agente = log.get("agente", "SYSTEM")
                mensagem = log.get("mensagem", "")
                timestamp = log.get("timestamp", "")
                ts_curto = timestamp[-12:-5] if timestamp else ""
                cor = COLORS.get(agente, "#ffffff")
                st.markdown(f"<span style='color:{cor}'>[{ts_curto}]</span> **{agente}:** {mensagem}", unsafe_allow_html=True)

        else:
            st.error("❌ Não foi possível conectar ao Redis")
            st.info("Execute o Redis: docker run -d -p 6379:6379 redis:alpine")
            if st.button("Tentar novamente"):
                continue

        st.divider()
        ciclo_atual = get_redis_value(r, "ciclo_atual") if r else "?"
        st.caption(f"Ciclo: {ciclo_atual} | Atualizado: {datetime.now().strftime('%H:%M:%S')} | Auto-refresh a cada 5s")

    time.sleep(5)