# test_mt5_win.py
import MetaTrader5 as mt5

mt5.initialize()

# Try WIN$ - mini indice continuo
sym = "WIN$"
if mt5.symbol_select(sym, True):
    info = mt5.symbol_info(sym)
    print(f"{sym}: Bid={info.bid}, Ask={info.ask}")
else:
    print(f"{sym} nao disponivel")

# Try trading symbols
for sym in ["WINM26", "WINJ26"]:
    if mt5.symbol_select(sym, True):
        info = mt5.symbol_info(sym)
        print(f"{sym}: Bid={info.bid}, Ask={info.ask}")

mt5.shutdown()