# test_mt5_path.py
import MetaTrader5 as mt5
import os

print("=== Teste MT5 com path ===")

# Mostrar onde está procurando
print("Path MT5:", os.getenv("MQL5_PATH", "não definido"))

# Tentar initialize com timeout
print("\nTentando initialize...")
result = mt5.initialize(
    login=0,
    server="ClearInvestimentos-C",
    timeout=10000
)

print(f"Resultado: {result}")
if not result:
    print("Erro:", mt5.last_error())
    
    # Verificar se MT5 está rodando
    import subprocess
    result = subprocess.run(["tasklist"], capture_output=True, text=True)
    if "Terminal.exe" in result.stdout:
        print("\nMT5 Terminal.exe está RODANDO")
    else:
        print("\nMT5 NÃO está rodando!")