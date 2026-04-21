# test_b3api_final.py
import b3api

# Testar com ação conhecida
try:
    data = b3api.assets.get('ITSA4')
    print("ITSA4:", data)
except Exception as e:
    print("ITSA4 error:", e)

# Testar WIN
try:
    data = b3api.assets.get('WIN')
    print("WIN:", data)
except Exception as e:
    print("WIN error:", e)