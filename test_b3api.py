# test_b3api.py
from b3api import B3API

api = B3API()

try:
    info = api.quote("WIN")
    print(f"WIN price: {info.price}")
    print(f"WIN change: {info.change}")
except Exception as e:
    print(f"Error: {e}")