# test_source.py
import os
print("DATA_SOURCE:", os.getenv("DATA_SOURCE", "NAO DEFINIDO"))

from infrastructure.data_provider import DataProvider
d = DataProvider()
print("DataProvider source:", d.source)