import os
from pipeline.bronze import executar_bronze
from dotenv import load_dotenv

try:
    executar_bronze()

except Exception:

    print(f'erro')

    raise

