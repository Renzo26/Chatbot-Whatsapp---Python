from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import quote

# Carrega variáveis do .env
load_dotenv()

# Obtém a URL do banco de dados do ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ ERRO: DATABASE_URL não configurada! Verifique as variáveis de ambiente no Vercel.")

# Teste de conexão direta com o Supabase usando psycopg2
try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")  # Supabase exige SSL
    conn.close()
    print("✅ Conexão bem-sucedida com o banco de dados Supabase!")
except Exception as e:
    print(f"❌ ERRO ao conectar ao banco de dados: {e}")

# Criar o engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Garante que a conexão está ativa antes de usá-la
    connect_args={"sslmode": "require"}  # SSL obrigatório para Supabase
)

# Criar sessão com pool de conexões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base para os modelos
Base = declarative_base()
