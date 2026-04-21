# test_mt5_prices.py
import MetaTrader5 as mt5

mt5.initialize()

# Get last tick for WIN
for sym in ["WIN", "WIN$", "WINM26"]:
    tick = mt5.symbol_info_tick(sym)
    if tick:
        print(f"{sym}: Last={tick.last}, Bid={tick.bid}, Ask={tick.ask}")
    else:
        print(f"{sym}: Sem tick")

# Check if market is open
print("\n=== Verificando mercado ===")
for sym in ["WIN$", "WINM26"]:
    info = mt5.symbol_info(sym)
    if info:
        print(f"{sym}: visible={info.visible}, session_open={info.session_open}")

mt5.shutdown()