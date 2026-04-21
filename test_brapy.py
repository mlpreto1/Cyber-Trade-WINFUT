# test_brapy.py
from brapy import Client

# Test with token
api = Client()

# Test PETR4
try:
    result = api.select('PETR4').prices()
    print("PETR4:", result)
except Exception as e:
    print("PETR4 error:", e)

# Test WIN
try:
    result = api.select('WIN').prices()
    print("WIN:", result)
except Exception as e:
    print("WIN error:", e)