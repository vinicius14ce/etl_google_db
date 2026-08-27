import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv


load_dotenv()

DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")

# ============================================================
# CONEXÃO
# ============================================================

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# ============================================================
# RECURSOS GENÉRICOS
# ============================================================

def testar_conexao():

    with engine.connect() as conn:

        conn.execute(
            text("SELECT 1")
        )

    return True


def executar_sql(
    sql,
    parametros=None
):

    with engine.begin() as conn:

        resultado = conn.execute(
            text(sql),
            parametros or {}
        )

    return resultado


def consultar_sql(
    sql,
    parametros=None
):

    with engine.connect() as conn:

        resultado = conn.execute(
            text(sql),
            parametros or {}
        )

        return resultado.fetchall()