# test_mt5_symbols.py
import MetaTrader5 as mt5

mt5.initialize()

# Get all symbols
symbols = mt5.symbols_get()
print(f"Total de simbolos: {len(symbols)}")

# Find WIN symbols
win_symbols = [s.name for s in symbols if 'WIN' in s.name]
print(f"\nSimbolos com WIN: {win_symbols[:20]}")

# Try to get quotes
print("\n=== Tentando encontrar WIN ===")
for sym in ["WIN", "WINJ26", "WINM26", "WINQ26", "WIND26", "WINF26", "WINH26"]:
    if mt5.symbol_select(sym, True):
        info = mt5.symbol_info(sym)
        if info:
            print(f"{sym}: Bid={info.bid}, Ask={info.ask}")

mt5.shutdown()