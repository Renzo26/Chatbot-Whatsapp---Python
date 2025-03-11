from fastapi import FastAPI
from routes import router  # Importando corretamente
from database.config import engine, Base  # Configuração do banco de dados
import logging

# Inicializa a aplicação FastAPI
app = FastAPI(debug=True)

# Criar tabelas no banco de dados, se ainda não existirem
Base.metadata.create_all(bind=engine)

# Incluir as rotas do webhook
app.include_router(router)

# Configurar logs para capturar erros detalhados
logging.basicConfig(level=logging.DEBUG)

# Rota para verificar se a API está rodando
@app.get("/")
def home():
    return {"message": "Bot de WhatsApp rodando!"}
