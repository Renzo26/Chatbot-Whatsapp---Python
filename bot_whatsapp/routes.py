from fastapi import APIRouter, Request, HTTPException
import psycopg2
import os

router = APIRouter()

# URL do banco (Vercel env var)
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

        if response:
            conn.close()
            return {"status": "Predefined response found", "response": response[0]}

        # Se não houver, salvar a mensagem
        cursor.execute("INSERT INTO messages (user_id, message) VALUES (%s, %s)", (user_id, message))
        conn.commit()
        conn.close()
        return {"status": "Message saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar mensagem: {str(e)}")
