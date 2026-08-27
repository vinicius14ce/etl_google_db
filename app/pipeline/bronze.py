import os
import re
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from services.logger import registrar_erro
from services.database import engine

# __INIT__
load_dotenv()
SCHEMA = "bronze"
DIR_CRED_GOOGLE = os.getenv("DIR_CRED_GOOGLE")
BASE_DIR = os.path.dirname(os.path.abspath(DIR_CRED_GOOGLE))
SHEET = os.getenv('GOOGLE_SPREADSHEET_ID')
RANGE = 'BASE!A1:Q'

# AUTENTICAÇÃO GOOGLE
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets"
]
CREDENTIALS_FILE = os.path.join(
    BASE_DIR,
    "google",
    "credential.json"
)
TOKEN_FILE = os.path.join(
    BASE_DIR,
    'google',
    "token.json"
)
# ALTENTICAÇÕES
def autenticar_google():
    credentials = None
    # Verificar token existente    
    if os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES
        )
    # Se não existir ou estiver inválido
    if not credentials or not credentials.valid:
        # Tentar renovar
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())
        # Nova autenticação
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES
            )
            credentials = flow.run_local_server(
                port=0
            )
        # Salvar token
        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8"
        ) as token:
            token.write(
                credentials.to_json()
            )
    return credentials
# OBTER SERVIÇO GOOGLE SHEETS
def obter_servico_sheets(credentials):
    # Instancia cliente da API do Google Sheets v4
    return build('sheets', 'v4', credentials=credentials)
# VALIDAR IDs DAS PLANILHAS
def validar_spreadsheet_ids(SHEET):
    SHEET = SHEET
    planilhas = {
        "CONTRATOS": SHEET,
    }
    for nome, spreadsheet_id in planilhas.items():

        if not spreadsheet_id:
            return f'invalid sheet'
# CONEXÃO BANCO // CORRIGIR URL INSERIR IP DA MAQUINA DO BANCO
# EXTRAÇÃO
def extrair_dados_planilha(service, spreadsheet_id, range_name):
    # Executa requisição HTTP GET na API
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    
    # Retorna matriz de valores brutos
    return result.get('values', [])
# TRATAMENTOS
def transformar_dataframe(dados):
    # Tratar caso matriz vazia
    if_not = 'Sem dados validos'

    if not dados:
        return pd.DataFrame([if_not], columns=["def transformar_dataframe"])

    cabecalho = dados[0]
    linhas = dados[1:]
    return pd.DataFrame(linhas, columns=cabecalho)
def limpar_nome_tabela(nome):
    """Converte o nome do arquivo em um nome de tabela válido para PostgreSQL"""
    nome = nome.lower()
    nome = Path(nome).stem
    nome = re.sub(
        r"[^a-z0-9_]+",
        "_",
        nome
    )
    nome = re.sub(
        r"_+",
        "_",
        nome
    )
    nome = nome.strip("_")
    return nome
def limpar_colunas(df):
    """Padroniza os nomes das colunas"""
    novas_colunas = []
    for coluna in df.columns:
        coluna = str(coluna).strip().lower()
        coluna = re.sub(
            r"[^a-z0-9_]+",
            "_",
            coluna
        )
        coluna = re.sub(
            r"_+",
            "_",
            coluna
        )
        coluna = coluna.strip("_")
        novas_colunas.append(coluna)
    df.columns = novas_colunas
    return df
def date_time(df):
    df["data_carga"] = datetime.now()
    return df
# EXPORT
def to_db(df):
    df.to_sql(
        name='base_contratos',
        con=engine,
        schema=SCHEMA,
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )
# EXECUÇÃO
def executar_bronze():
    # marcação console
    print("\n" + "=" * 70)
    print("INICIANDO ETAPA BRONZE")
    print("=" * 70)
    # validar credencial banco
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as erro:
        registrar_erro(
                etapa="BRONZE",
                subetapa="Validar Credencial Banco",
                erro=erro
        )
        raise
    # Executar Autenticação Google
    try:
        credenciais = autenticar_google()
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="gerar credencial de acesso ao google",
            erro=erro
        )
        raise
    # Iniciar Serviço de Conexão Google
    try:
        service = obter_servico_sheets(credenciais)
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="criar serviço de conexão com google",
            erro=erro
        )
        raise
    # Extrair Objeto da Conexão
    try:
        dados = extrair_dados_planilha(service, SHEET, RANGE)
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="extrair dados do serviço conectado",
            erro=erro
        )
        raise
    # Transformar objeto em DataFrame
    try:
        df = transformar_dataframe(dados)
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="tranformar os dados em objeto pandas 'df' ",
            erro=erro
        )
        raise
    # Limpar Colunas com Regex
    try:
        df = limpar_colunas(df)
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="limpar colunas",
            erro=erro
        )
        raise
    # Inserir Coluna com Registro da Ultima Atualização
    try:
        df = date_time(df)
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="coluna ultima carga",
            erro=erro
        )
        raise
    # Carga no Banco
    try:
        to_db(df)
    except Exception as erro:
        registrar_erro(
            etapa="BRONZE",
            subetapa="Carga no Banco",
            erro=erro
        )
        raise
        
if __name__ == "__main__":
    executar_bronze()

