import os
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# BANCO DE DADOS
# ============================================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "inadimplencia")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================

def validar_configuracao():

    if not DB_HOST:
        raise ValueError(
            "DB_HOST não encontrado no .env"
        )

    if not DB_USER:
        raise ValueError(
            "DB_USER não encontrado no .env"
        )

    if not DB_PASSWORD:
        raise ValueError(
            "DB_PASSWORD não encontrado no .env"
        )