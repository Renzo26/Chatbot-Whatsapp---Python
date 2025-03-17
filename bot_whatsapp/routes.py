from fastapi import APIRouter, HTTPException
import psycopg2
import os

router = APIRouter()

# Conectar ao banco
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@router.post("/save_message/")
async def save_message(user_id: str, message: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar se existe uma resposta pré-definida
        cursor.execute("SELECT response FROM predefined_responses WHERE keyword = %s;", (message,))
        response = cursor.fetchone()

        if response:
            return {"status": "Predefined response found", "response": response[0]}

        # Se não houver resposta pré-definida, salvar a mensagem
        cursor.execute("INSERT INTO messages (user_id, message) VALUES (%s, %s)", (user_id, message))
        conn.commit()
        conn.close()
        return {"status": "Message saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
