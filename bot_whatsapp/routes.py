from fastapi import APIRouter, HTTPException, Request
import psycopg2
import os
from datetime import datetime

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não foi encontrada!")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco: {str(e)}")

@router.post("/api/salvar")
async def save_message(request: Request):
    try:
        data = await request.json()

        user_id = str(data.get("numero"))
        mensagem = data.get("mensagem")
        data_envio = data.get("timestamp")

        if not user_id or not mensagem:
            raise HTTPException(status_code=400, detail="Campos obrigatórios: 'numero' e 'mensagem'")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar resposta pré-definida
        cursor.execute("SELECT response FROM predefined_responses WHERE keyword = %s;", (mensagem,))
        response = cursor.fetchone()

        if response:
            conn.close()
            return {"status": "Resposta pré-definida encontrada", "resposta": response[0]}

        # Inserir mensagem no banco
        cursor.execute("""
            INSERT INTO messages (user_id, mensagem, data_envio)
            VALUES (%s, %s, %s);
        """, (user_id, mensagem, data_envio))

        conn.commit()
        conn.close()

        return {"status": "Mensagem salva com sucesso"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar mensagem: {str(e)}")
