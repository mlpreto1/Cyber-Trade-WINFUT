# test_mt5_v2.py
import MetaTrader5 as mt5
import time

print("=== Teste MT5 Clear v2 ===")
print("Aguardando MT5...")
time.sleep(2)

# Try initialize
result = mt5.initialize()
print(f"Inicialize result: {result}")

if result:
    print("MT5 OK!")
    account = mt5.account_info()
    if account:
        print(f"Conta: {account.login}")
        print(f"Servidor: {account.server}")
    
    # Try symbols
    symbols = ["WINJ26", "WINM26", "WIN"]
    for sym in symbols:
        if mt5.symbol_select(sym, True):
            info = mt5.symbol_info(sym)
            if info:
                print(f"{sym}: Bid={info.bid}, Ask={info.ask}")
                break
    mt5.shutdown()
else:
    err = mt5.last_error()
    print(f"Erro: {err}")
    # Try wait more
    print("Tentando novamente...")
    time.sleep(3)
    result2 = mt5.initialize()
    if result2:
        print("Agora foi!")
        account = mt5.account_info()
        if account:
            print(f"Conta: {account.login}")
            print(f"Servidor: {account.server}")
        mt5.shutdown()
    else:
        print(f"Falhou: {mt5.last_error()}")