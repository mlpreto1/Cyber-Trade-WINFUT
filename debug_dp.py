# debug_dp.py
import asyncio
import sys
sys.path.insert(0, "H:/Meu Drive/Cyber Trade/Winfut")
from infrastructure.data_provider import DataProvider, _dia_de_pregao, _horario_mercado_aberto

async def debug():
    dp = DataProvider(source="mt5")
    
    print("=== DEBUG DataProvider ===")
    print(f"_dia_de_pregao(): {_dia_de_pregao()}")
    print(f"_horario_mercado_aberto(): {_horario_mercado_aberto()}")
    
    print("\n=== get_preco_atual() ===")
    preco = await dp.get_preco_atual()
    print(f"Preco: {preco}")
    
    print("\n=== get_dados_candle() ===")
    candles = await dp.get_dados_candle("5min", 10)
    print(f"Qtde candles: {len(candles)}")
    for c in candles[:3]:
        print(c)

if __name__ == "__main__":
    asyncio.run(debug())