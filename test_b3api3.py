# test_b3api3.py
from b3api import assets

try:
    info = assets.get("WIN")
    print(f"WIN info: {info}")
except Exception as e:
    print(f"Error: {e}")