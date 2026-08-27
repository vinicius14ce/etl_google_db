from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO DO LOG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PASTA_LOGS = BASE_DIR / "logs"

ARQUIVO_LOG_ERROS = PASTA_LOGS / "etl_erros.log"


# ============================================================
# PREPARAR DIRETÓRIO
# ============================================================

def preparar_diretorio_logs():

    PASTA_LOGS.mkdir(
        parents=True,
        exist_ok=True
    )


# ============================================================
# DATA E HORA
# ============================================================

def obter_timestamp():

    agora = datetime.now()

    return {
        "data": agora.strftime("%d/%m/%Y"),
        "horario": agora.strftime("%H:%M:%S")
    }


# ============================================================
# REGISTRAR ERRO
# ============================================================

def registrar_erro(
    etapa,
    erro,
    arquivo=None,
    subetapa=None
):

    preparar_diretorio_logs()

    timestamp = obter_timestamp()

    data = timestamp["data"]
    horario = timestamp["horario"]

    mensagem = (
        "\n"
        + "=" * 80
        + "\n"
        + "ERRO NO PROCESSO ETL\n"
        + "=" * 80
        + "\n"
        + f"Etapa    : {etapa}\n"
        + f"Subetapa : {subetapa}\n"
        + f"Arquivo  : {arquivo if arquivo else '-'}\n"
        + f"Data     : {data}\n"
        + f"Horário  : {horario}\n"
        + f"Erro     : {erro}\n"
        + "=" * 80
        + "\n"
    )

    # --------------------------------------------------------
    # TERMINAL
    # --------------------------------------------------------

    print(mensagem)

    # --------------------------------------------------------
    # ARQUIVO
    # --------------------------------------------------------

    with open(
        ARQUIVO_LOG_ERROS,
        "a",
        encoding="utf-8"
    ) as arquivo_log:

        arquivo_log.write(mensagem)