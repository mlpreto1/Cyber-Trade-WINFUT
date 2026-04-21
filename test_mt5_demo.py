# test_mt5_demo.py
import MetaTrader5 as mt5
import time

print("=== Teste MT5 Demo ===")

# Initialize sem login específico (pega o que estiver logado)
result = mt5.initialize(login=0)  # 0 = qualquer conta
print(f"Inicialize: {result}")

if not result:
    err = mt5.last_error()
    print(f"Erro: {err}")
    
    # Tentar com servidor específico da Clear
    print("\nTentando com servidor Clear...")
    result = mt5.initialize(server="ClearInvestimentos-C")
    print(f"Resultado: {result}")
    if not result:
        print(f"Erro: {mt5.last_error()}")

else:
    print("MT5 conectado!")
    account = mt5.account_info()
    if account:
        print(f"Login: {account.login}")
        print(f"Servidor: {account.server}")
        print(f"Tipo: {'REAL' if not account.login % 100000 else 'DEMO'}")
    
    # Procurar WIN
    for sym in ["WINJ26", "WINM26", "WINQ26", "WIN"]:
        if mt5.symbol_select(sym, True):
            info = mt5.symbol_info(sym)
            if info and info.bid > 0:
                print(f"\n{sym}: Bid={info.bid}, Ask={info.ask}")
                break
    else:
        print("\nWIN não encontrado")
    
    mt5.shutdown()