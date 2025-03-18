from fastapi import APIRouter, HTTPException
import psycopg2
import os

router = APIRouter()

# Pegando a URL do banco do Supabase (corrigido)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("Erro: DATABASE_URL não foi encontrada! Configure no Vercel.")

# Conectar ao banco com um pool de conexões para evitar sobrecarga
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")  # Adicionando SSL para Supabase
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco: {str(e)}")

@router.post("/save_message/")
async def save_message(user_id: str, message: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se existe uma resposta pré-definida
        cursor.execute("SELECT response FROM predefined_responses WHERE keyword = %s;", (message,))
        response = cursor.fetchone()

        if response:
            conn.close()
            return {"status": "Predefined response found", "response": response[0]}

        # Se não houver resposta pré-definida, salvar a mensagem
        cursor.execute("INSERT INTO messages (user_id, message) VALUES (%s, %s)", (user_id, message))
        conn.commit()
        conn.close()
        return {"status": "Message saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar mensagem: {str(e)}")
