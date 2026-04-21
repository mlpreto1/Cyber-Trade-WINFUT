# test_b3api2.py
import b3api.assets as assets

print("Assets module functions:", [f for f in dir(assets) if not f.startswith('_')])