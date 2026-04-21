# utils/pixel_agents.py
# Interface Pixel Art para Agentes

import os
import json
from datetime import datetime

VERDE = "\033[92m"
AZUL = "\033[94m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CIANO = "\033[96m"
MAGENTA = "\033[95m"
BRANCO = "\033[97m"
NEGRITO = "\033[1m"
RESET = "\033[0m"

AGENTES_ICONS = {
    "architect": "🏗️",
    "morpheus": "🌊", 
    "oracle": "🔮",
    "neo": "🎯",
    "exec": "⚡"
}

AGENTES_CORES = {
    "architect": AZUL,
    "morpheus": CIANO,
    "oracle": MAGENTA,
    "neo": VERDE,
    "exec": AMARELO
}


def print_pixel_header():
    print(f"""
{CIANO}╔══════════════════════════════════════════════════════════╗
║     ██████╗ ███████╗██╗   ██╗██╗  ██╗██╗   ██╗███████╗        ║
║     ██╔══██╗██╔════╝██║   ██║██║ ██╔╝██║   ██║██╔════╝        ║
║     ██║  ██║█████╗  ██║   ██║███╔╝ ██║   ██║███████╗        ║
║     ██║  ██║██╔══╝  ╚██╗ ██╔╝██╔═██╗ ╚██╗ ██╔╝╚════██║        ║
║     ██████╔╝███████╗ ╚████╔╝ ██║  ██╗ ╚████╔╝ ███████║        ║
║     ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝  ╚═╝  ╚═══╝  ╚══════╝        ║
║                    ██████╗ ███████╗███████╗                    ║
║                    ██╔══██╗██╔════╝██╔════╝                    ║
║                    ██║  ██║█████╗  ███████╗                    ║
║                    ██║  ██║██╔══╝  ╚════██║                    ║
║                    ██████╔╝███████╗███████║                    ║
║                    ╚═════╝ ╚══════╝╚══════╝                    ║
║                       AGENTS v2.4 - CYBER TRADE                ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def print_agente(nome: str, dado: dict, emoji: str = None):
    nome_upper = nome.upper()
    cor = AGENTES_CORES.get(nome.lower(), BRANCO)
    icon = emoji or AGENTES_ICONS.get(nome.lower(), "🤖")
    
    print(f"{cor}┌{'─' * 58}┐{RESET}")
    print(f"{cor}│{RESET} {NEGRITO}{icon} {nome_upper:<54}{cor}│{RESET}")
    print(f"{cor}├{'─' * 58}┤{RESET}")
    
    if dado:
        for k, v in dado.items():
            if isinstance(v, float):
                v_str = f"{v:.2f}"
            elif isinstance(v, dict):
                v_str = json.dumps(v)[:40]
            else:
                v_str = str(v)[:40]
            print(f"{cor}│{RESET}   {k:<20}: {v_str:<35}{cor}│{RESET}")
    else:
        print(f"{cor}│{RESET}   {AMARELO}Aguardando dados...{' ' * 25}{cor}│{RESET}")
    
    print(f"{cor}└{'─' * 58}┘{RESET}")


def print_status_sistema(preco: float, pnl: float, ops: int, modo: str):
    print(f"""
{VERDE}╔══════════════════════════════════════════════════════════╗
║  {VERDE}🎯 SISTEMA{VERDE}                                          ║
╠══════════════════════════════════════════════════════════╣
║  Preço WIN     : {preco:>10.0f} pts                        ║
║  PnL Dia       : {pnl:>+10.2f} %                        ║
║  Operações     : {ops:>10d}                               ║
║  Modo          : {modo:<10}                          ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def print_decisao(decisao: str, direcao: str, score: int, motivo: str):
    if decisao == "ARMAR":
        cor = VERDE
        icon = "🚀"
    elif decisao == "CANCELAR":
        cor = AMARELO
        icon = "⏸️"
    else:
        cor = VERMELHO
        icon = "🛑"
    
    print(f"""
{cor}╔══════════════════════════════════════════════════════════╗
║  {icon} DECISÃO: {decisao:<46}{cor}║
╠══════════════════════════════════════════════════════════╣
║  Direção       : {direcao:<46}{cor}║
║  Score         : {score:>46}{cor}║
║  Motivo        : {motivo[:46]:<46}{cor}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_ciclo(num: int):
    print(f"\n{AZUL}═══ CICLO {num:03d} ═══{RESET} {datetime.now().strftime('%H:%M:%S')}")


def gerar_html(estado: dict) -> str:
    agents = estado.get("agentes", {})
    sistema = estado.get("sistema", {})
    decisao = estado.get("decisao", {})
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CYBER TRADE - AGENTS</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #0a0a0a;
            font-family: 'VT323', monospace;
            color: #00ff00;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        h1 {{
            text-align: center;
            font-size: 48px;
            color: #00ffff;
            text-shadow: 0 0 10px #00ffff;
            margin-bottom: 30px;
            letter-spacing: 8px;
        }}
        
        .sistema {{
            background: #111;
            border: 2px solid #00ff00;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            font-size: 24px;
        }}
        
        .sistema span {{ color: #ffff00; }}
        
        .agents-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .agent {{
            background: #0d0d0d;
            border: 2px solid #333;
            padding: 15px;
        }}
        
        .agent.architect {{ border-color: #00bfff; }}
        .agent.morpheus {{ border-color: #00ffff; }}
        .agent.oracle {{ border-color: #ff00ff; }}
        .agent.neo {{ border-color: #00ff00; }}
        
        .agent-title {{
            font-size: 28px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .agent.architect .agent-title {{ color: #00bfff; }}
        .agent.morpheus .agent-title {{ color: #00ffff; }}
        .agent.oracle .agent-title {{ color: #ff00ff; }}
        .agent.neo .agent-title {{ color: #00ff00; }}
        
        .agent-data {{ font-size: 18px; color: #aaa; }}
        .agent-data span {{ color: #fff; }}
        
        .decisao {{
            background: #111;
            border: 4px solid #333;
            padding: 30px;
            text-align: center;
            font-size: 36px;
        }}
        
        .decisao.armar {{ border-color: #00ff00; color: #00ff00; }}
        .decisao.cancelar {{ border-color: #ffff00; color: #ffff00; }}
        .decisao.fechar {{ border-color: #ff0000; color: #ff0000; }}
        
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 16px;
        }}
        
        .pixel-art {{
            image-rendering: pixelated;
            display: inline-block;
        }}
    </style>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <div class="container">
        <h1>▓▓ CYBER TRADE ▓▓</h1>
        
        <div class="sistema">
            <div>PREÇO: <span>{sistema.get('preco', 0):.0f}</span></div>
            <div>PnL: <span>{sistema.get('pnl', 0):+.2f}%</span></div>
            <div>OPS: <span>{sistema.get('ops', 0)}</span></div>
            <div>MODO: <span>{sistema.get('modo', 'PAPER')}</span></div>
        </div>
        
        <div class="agents-grid">
            <div class="agent architect">
                <div class="agent-title">🏗️ ARCHITECT</div>
                <div class="agent-data">
                    <div>Sinal: <span>{agents.get('architect', {}).get('sinal', '-')}</span></div>
                    <div>Confiança: <span>{agents.get('architect', {}).get('confianca', 0)}</span></div>
                    <div>EMA9: <span>{agents.get('architect', {}).get('ema9_5m', 0):.0f}</span></div>
                    <div>ATR: <span>{agents.get('architect', {}).get('atr14_5m', 0):.1f}</span></div>
                    <div>RSI: <span>{agents.get('architect', {}).get('rsi14_5m', 0):.1f}</span></div>
                </div>
            </div>
            
            <div class="agent morpheus">
                <div class="agent-title">🌊 MORPHEUS</div>
                <div class="agent-data">
                    <div>Fluxo: <span>{agents.get('morpheus', {}).get('direcao_fluxo', '-')}</span></div>
                    <div>Força: <span>{agents.get('morpheus', {}).get('forca_fluxo', 0)}</span></div>
                    <div>CVD: <span>{agents.get('morpheus', {}).get('cvd_total', 0)}</span></div>
                    <div>Volume: <span>{agents.get('morpheus', {}).get('volume_total', 0)}</span></div>
                </div>
            </div>
            
            <div class="agent oracle">
                <div class="agent-title">🔮 ORACLE</div>
                <div class="agent-data">
                    <div>Regime: <span>{agents.get('oracle', {}).get('regime_mercado', '-')}</span></div>
                    <div>Macro: <span>{agents.get('oracle', {}).get('status_macro', '-')}</span></div>
                    <div>Tendência: <span>{agents.get('oracle', {}).get('tendencia_mercado', '-')}</span></div>
                </div>
            </div>
            
            <div class="agent neo">
                <div class="agent-title">🎯 NEO</div>
                <div class="agent-data">
                    <div>Decisão: <span>{agents.get('neo', {}).get('decisao', '-')}</span></div>
                    <div>Score: <span>{agents.get('neo', {}).get('score_final', 0)}</span></div>
                    <div>Direção: <span>{agents.get('neo', {}).get('direcao', '-')}</span></div>
                    <div>Motivo: <span>{agents.get('neo', {}).get('motivo', '-')}</span></div>
                </div>
            </div>
        </div>
        
        <div class="decisao {decisao.get('decisao', 'cancelar').lower()}">
            ▓▓ {decisao.get('decisao', 'AGUARDANDO')} ▓▓
            <br>
            <small>{decisao.get('motivo', '')}</small>
        </div>
        
        <div class="footer">
            CYBER TRADE WIN v2.4 | Atualizado: {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    return html


def salvar_html(estado: dict, path: str = "H:\\Meu Drive\\Cyber Trade\\Winfut\\agents.html"):
    html = gerar_html(estado)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
