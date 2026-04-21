# test_mt5.py
import MetaTrader5 as mt5

print('MT5 version:', mt5.__version__ if hasattr(mt5, '__version__') else 'installed')
result = mt5.initialize()
print('Initialize result:', result)
if not result:
    print('Error:', mt5.last_error())
mt5.shutdown()