# test_mt5_clear.py
import MetaTrader5 as mt5
import time

print("=== Teste MT5 Clear ===")

# Initialize
if not mt5.initialize():
    print("ERRO: MetaTrader5 não conectado")
    print("Erro:", mt5.last_error())
    print("\nSolução: Abra o MT5 e faça login na Clear")
else:
    print("MT5 conectado!")
    
    # Get account info
    account = mt5.account_info()
    if account:
        print(f"Conta: {account.login}")
        print("Servidor:", account.server)
        print("Empresa:", account.company)
    
    # Get WIN symbol info
    symbol = "WINJ26"  # Abril 2026
    if mt5.symbol_select(symbol, True):
        info = mt5.symbol_info(symbol)
        if info:
            print(f"\n{symbol}:")
            print(f"  Bid: {info.bid}")
            print(f"  Ask: {info.ask}")
            print(f"  Última: {info.last}")
        else:
            print(f"Símbolo {symbol} não encontrado")
    else:
        print(f"Símbolo {symbol} não disponível")
        # Try current month
        from datetime import datetime
        mes = datetime.now().month
        ano = str(datetime.now().year)[-2:]
        symbol = f"WIN{mes}{ano}"
        print(f"Tentando {symbol}...")
        if mt5.symbol_select(symbol, True):
            info = mt5.symbol_info(symbol)
            if info:
                print(f"{symbol}: Bid={info.bid}, Ask={info.ask}")
    
    mt5.shutdown()
    print("\nDesconectado")