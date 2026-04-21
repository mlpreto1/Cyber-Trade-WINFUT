# test_mt5_check.py
import MetaTrader5 as mt5

print("=== MT5 Conectado! ===")

if mt5.initialize():
    info = mt5.terminal_info()
    print(f"Empresa: {info.company}")
    print(f"Conexao: {info.connected}")
    
    account = mt5.account_info()
    if account:
        print(f"Conta: {account.login}")
        print(f"Servidor: {account.server}")
        print(f"Balance: R$ {account.balance}")
    
    # Procurar WIN
    symbols = ["WINJ26", "WINM26", "WIN"]
    for sym in symbols:
        if mt5.symbol_select(sym, True):
            info = mt5.symbol_info(sym)
            if info and info.bid > 0:
                print(f"\n{sym}: Bid={info.bid}, Ask={info.ask}")
                break
    else:
        print("\nNenhum simbolo WIN encontrado")
    
    mt5.shutdown()
    print("\n=== SUCESSO! MT5 FUNCIONANDO! ===")
else:
    print("Falhou:", mt5.last_error())