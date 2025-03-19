from fastapi import FastAPI
from routes import router  # Importando as rotas corretamente
from database.config import engine, Base  # Configuração do banco de dados
import logging

# Inicializa a aplicação FastAPI
app = FastAPI()

# Criar tabelas no banco de dados, se ainda não existirem
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas verificadas/criadas com sucesso!")
except Exception as e:
    print(f"❌ ERRO ao criar tabelas: {e}")

# Incluir as rotas do webhook
app.include_router(router)

# Configurar logs detalhados para debug
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Rota para verificar se a API está rodando
@app.get("/")
def home():
    return {"message": "✅ Bot de WhatsApp rodando!"}

# Executar servidor no Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, timeout_keep_alive=120)
