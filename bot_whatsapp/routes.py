from fastapi import APIRouter, Request, HTTPException
import psycopg2
import os
from datetime import datetime

router = APIRouter()

# Pegando a URL do banco do Supabase
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Erro: DATABASE_URL não foi encontrada! Configure no Vercel.")

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco: {str(e)}")

@router.post("/api/salvar")
async def salvar_mensagem(request: Request):
    try:
        data = await request.json()
        user_id = data.get("numero")
        message = data.get("mensagem")

        if not user_id or not message:
            raise HTTPException(status_code=400, detail="Campos obrigatórios: 'numero' e 'mensagem'")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar resposta pré-definida
        cursor.execute("SELECT response FROM predefined_responses WHERE keyword = %s;", (message,))
        response = cursor.fetchone()

        data_envio = datetime.utcnow()

        if response:
            # Se houver resposta pré-definida, salva a mensagem e resposta
            cursor.execute(
                "INSERT INTO messages (user_id, mensagem, resposta, data_envio) VALUES (%s, %s, %s, %s)",
                (user_id, message, response[0], data_envio)
            )
            conn.commit()
            conn.close()
            return {
                "status": "Predefined response found",
                "resposta": response[0]
            }

        # Se não houver resposta, salva somente a mensagem
        cursor.execute(
            "INSERT INTO messages (user_id, mensagem, data_envio) VALUES (%s, %s, %s)",
            (user_id, message, data_envio)
        )
        conn.commit()
        conn.close()
        return {
            "status": "Message saved (no predefined response)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar mensagem: {str(e)}")
