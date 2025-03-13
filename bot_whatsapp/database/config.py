from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote

load_dotenv()  # Carrega as variáveis do .env

# Recupera as variáveis de ambiente
username = quote(os.getenv("DB_USER", "postgres"))
password = quote(os.getenv("DB_PASSWORD", "senha"))
dbname = os.getenv("DB_NAME", "bot_WhatsApp")

# Cria a URL de conexão com o banco de dados
DATABASE_URL = f"postgresql://{username}:{password}@localhost/{dbname}"

# Exibe a URL de conexão
print("DATABASE_URL:", DATABASE_URL)

# Teste de conexão direta com psycopg2
try:
    conn = psycopg2.connect(
        dbname=dbname,
        user=username,
        password=password,
        host="localhost",
        client_encoding='UTF8'  # Força o uso de UTF-8
    )
    print("Conexão bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

# Criação do engine para conectar ao banco de dados PostgreSQL
engine = create_engine(DATABASE_URL)

# SessionLocal configura a sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos declarativos
Base = declarative_base()
