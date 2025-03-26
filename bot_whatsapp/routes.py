from fastapi import APIRouter, HTTPException
import psycopg2
import os
from datetime import datetime

router = APIRouter()

# URL do banco (vem do Supabase)
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
async def salvar_mensagem(numero: str, mensagem: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 🔍 Verifica se já existe um usuário com esse número
        cursor.execute("SELECT id FROM users WHERE telefone = %s", (numero,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
        else:
            # 👤 Se não existir, cria novo usuário
            cursor.execute(
                "INSERT INTO users (telefone, nome, data_cadastro) VALUES (%s, %s, %s) RETURNING id",
                (numero, 'Usuário WhatsApp', datetime.utcnow())
            )
            user_id = cursor.fetchone()[0]
            conn.commit()

        # 🔍 Verifica se a mensagem tem resposta pré-definida
        cursor.execute("SELECT response FROM predefined_responses WHERE keyword = %s", (mensagem,))
        predefined = cursor.fetchone()

        if predefined:
            conn.close()
            return {"status": "Resposta automática", "resposta": predefined[0]}

        # 💾 Se não houver resposta, salva a mensagem na tabela messages
        cursor.execute(
            "INSERT INTO messages (user_id, mensagem, data_envio) VALUES (%s, %s, %s)",
            (user_id, mensagem, datetime.utcnow())
        )
        conn.commit()
        conn.close()

        return {"status": "Mensagem salva com sucesso", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar mensagem: {str(e)}")
