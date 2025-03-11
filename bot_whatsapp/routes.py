from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.config import SessionLocal
from database.models import User, Message

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/webhook")
def receive_message(payload: dict, db: Session = Depends(get_db)):
    phone = payload.get("phone")  # Corrigido para "phone"
    message = payload.get("message")  # Corrigido para "message"

    if not phone or not message:
        return {"error": "Payload inválido"}

    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        user = User(phone=phone)  # Corrigido para "phone"
        db.add(user)
        db.commit()
        db.refresh(user)

    new_message = Message(user_id=user.id, message=message)  # Corrigido para "message"
    db.add(new_message)
    db.commit()

    return {"status": "Mensagem recebida", "message": message}
