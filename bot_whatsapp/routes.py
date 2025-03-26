from fastapi import APIRouter, HTTPException, Request
import psycopg2
import os
from datetime import datetime

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não configurado!")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na conexão com o banco: {str(e)}")

@router.post("/api/salvar")
async def salvar_dados(request: Request):
    try:
        body = await request.json()

        mensagem = body.get("mensagem")
        numero = body.get("numero")
        timestamp = body.get("timestamp")

        if not mensagem or not numero:
            raise HTTPException(status_code=400, detail="Campos obrigatórios: 'numero' e 'mensagem'")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o número já está cadastrado na tabela 'users'
        cursor.execute("SELECT id FROM users WHERE telefone = %s", (numero,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
        else:
            # Insere novo usuário e recupera o ID gerado automaticamente
            cursor.execute("INSERT INTO users (telefone, data_cadastro) VALUES (%s, %s) RETURNING id", (numero, datetime.now()))
            user_id = cursor.fetchone()[0]

        # Verifica se há resposta pré-definida
        cursor.execute("SELECT response FROM predefined_responses WHERE keyword = %s;", (mensagem,))
        response = cursor.fetchone()

        if response:
            conn.close()
            return {"status": "Resposta automática encontrada", "resposta": response[0]}

        # Salva a mensagem
        cursor.execute(
            "INSERT INTO messages (user_id, mensagem, data_envio) VALUES (%s, %s, %s)",
            (user_id, mensagem, timestamp)
        )

        conn.commit()
        conn.close()
        return {"status": "Mensagem salva com sucesso"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar mensagem: {str(e)}")
