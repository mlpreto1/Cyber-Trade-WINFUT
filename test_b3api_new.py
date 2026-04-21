# test_b3api_new.py
import b3api

print("Modules:", dir(b3api))

# Try to get info about the package
import b3api.assets as assets

# Test listing
try:
    result = assets.list_stocks()
    print("Stocks:", result[:3] if result else "empty")
except Exception as e:
    print("list_stocks error:", e)

# Try get stock info
try:
    result = assets.get_info("WIN")
    print("WIN info:", result)
except Exception as e:
    print("get_info WIN error:", e)