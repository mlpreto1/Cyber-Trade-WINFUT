# test_mt5_servers.py
import MetaTrader5 as mt5
import time

print("=== Teste MT5 com Python Integration ===")

# Primeiro: verificar se MT5 está rodando
import subprocess
result = subprocess.run(["tasklist"], capture_output=True, text=True)
if "Terminal.exe" in result.stdout:
    print("✓ MT5 Terminal está rodando")
else:
    print("✗ MT5 NÃO está rodando!")

# Tentar initialize() simples (sem parâmetros)
print("\n1. Tentando initialize() simples...")
time.sleep(1)
if mt5.initialize():
    print("✓ Conectou!")
    print(mt5.terminal_info())
    mt5.shutdown()
else:
    print("✗ Falhou")
    print("Código:", mt5.last_error())
    
    print("\n2. Tentando com path do terminal...")
    # Tentar com path
    paths = [
        "C:/Program Files/MetaTrader 5/terminal64.exe",
        "C:/Program Files (x86)/MetaTrader 5/terminal.exe",
    ]
    for path in paths:
        try:
            import os
            if os.path.exists(path):
                print(f"Tentando: {path}")
                if mt5.initialize(path):
                    print("✓ Conectou!")
                    mt5.shutdown()
                    break
        except:
            pass
    
    print("\n⚠️ SOLUÇÃO:")
    print("1. Vá no MT5: Tools → Options → Community")
    print("2. Enable: Python Integration")
    print("3. Restart MT5")
    print("4. Rode este script novamente")