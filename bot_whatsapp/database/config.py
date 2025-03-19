from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote

load_dotenv()  # Carrega as variáveis do .env

# Recupera as variáveis do ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Erro: DATABASE_URL não encontrada! Configure no Vercel com a URL do Supabase.")

# Exibe a URL de conexão (somente para depuração - remova em produção)
print("DATABASE_URL:", DATABASE_URL)

# Teste de conexão direta com psycopg2
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")  # SSL obrigatório no Supabase
    print("Conexão com o banco de dados bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")

# Criação do engine para conectar ao banco de dados PostgreSQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=True, connect_args={"sslmode": "require"})

# SessionLocal configura a sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos declarativos
Base = declarative_base()
