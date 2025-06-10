# ADICIONE ESTAS IMPORTAÇÕES NO INÍCIO DO SEU routes.py
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
import psycopg2
import os
from datetime import datetime
import re
import json
from database.config import get_db
from database.models import User, Message, Feedback, Log

# NOVOS MODELOS PYDANTIC PARA VALIDAÇÃO

class WebhookFeedbackPayload(BaseModel):
    """
    Modelo para receber dados do webhook do n8n
    Formato exato conforme especificado
    """
    nome: str
    email: EmailStr
    feedback: str
    
    @validator('nome')
    def nome_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome não pode estar vazio')
        return v.strip()
    
    @validator('feedback')
    def feedback_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Feedback não pode estar vazio')
        return v.strip()

class FeedbackResponse(BaseModel):
    """
    Modelo de resposta após salvar feedback
    """
    id: int
    nome: str
    email: str
    feedback: str
    sentimento: Optional[str]
    data_recebimento: datetime
    status: str = "processado"

    class Config:
        from_attributes = True

# FUNÇÃO PARA ANÁLISE DE SENTIMENTO SIMPLES
def analyze_sentiment(text: str) -> str:
    """
    Análise de sentimento básica usando palavras-chave em português
    """
    text_lower = text.lower()
    
    # Palavras positivas
    positive_words = [
        'excelente', 'ótimo', 'bom', 'maravilhoso', 'perfeito', 'incrível',
        'fantástico', 'adorei', 'amei', 'gostei', 'satisfeito', 'feliz',
        'contente', 'alegre', 'positivo', 'recomendo', 'aprovado', 'legal',
        'show', 'top', 'demais', 'sucesso'
    ]
    
    # Palavras negativas
    negative_words = [
        'ruim', 'péssimo', 'horrível', 'terrível', 'odiei', 'detestei',
        'insatisfeito', 'decepcionado', 'frustrado', 'chateado', 'triste',
        'negativo', 'problema', 'erro', 'falha', 'defeito', 'reclamação',
        'lixo', 'porcaria', 'desastre'
    ]
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positivo"
    elif negative_count > positive_count:
        return "negativo"
    else:
        return "neutro"

# NOVO ENDPOINT WEBHOOK PARA N8N
@router.post("/webhook/feedback", response_model=FeedbackResponse)
async def webhook_feedback_n8n(payload: WebhookFeedbackPayload, db: Session = Depends(get_db)):
    """
    Webhook endpoint para receber feedback do n8n
    URL para configurar no n8n: https://sua-api.vercel.app/webhook/feedback
    """
    try:
        # Log da requisição recebida
        print(f"Feedback recebido via webhook: {payload.nome} - {payload.email}")
        
        # Análise de sentimento
        sentimento = analyze_sentiment(payload.feedback)
        
        # Criar novo registro de feedback
        novo_feedback = Feedback(
            nome=payload.nome,
            email=payload.email,
            feedback=payload.feedback,
            sentimento=sentimento,
            data_recebimento=datetime.utcnow()
        )
        
        # Salvar no banco de dados
        db.add(novo_feedback)
        db.commit()
        db.refresh(novo_feedback)
        
        # Registrar log do evento
        log_entry = Log(
            event_type="WEBHOOK_FEEDBACK",
            message=f"Feedback recebido via webhook de {payload.email} - Sentimento: {sentimento}",
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        
        # Retornar resposta de sucesso
        return FeedbackResponse(
            id=novo_feedback.id,
            nome=novo_feedback.nome,
            email=novo_feedback.email,
            feedback=novo_feedback.feedback,
            sentimento=novo_feedback.sentimento,
            data_recebimento=novo_feedback.data_recebimento,
            status="processado"
        )
        
    except Exception as e:
        db.rollback()
        # Registrar erro no log
        log_error = Log(
            event_type="WEBHOOK_ERROR",
            message=f"Erro ao processar feedback via webhook: {str(e)}",
            timestamp=datetime.utcnow()
        )
        db.add(log_error)
        db.commit()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar feedback: {str(e)}"
        )

# ENDPOINT ALTERNATIVO SEM VALIDAÇÃO RÍGIDA (para testes)
@router.post("/webhook/feedback/raw")
async def webhook_feedback_raw(request: Request, db: Session = Depends(get_db)):
    """
    Webhook alternativo que aceita qualquer formato JSON
    Para casos onde o n8n envia dados em formato diferente
    """
    try:
        # Receber dados brutos
        body = await request.json()
        print(f"Dados recebidos no webhook raw: {json.dumps(body, indent=2)}")
        
        # Extrair campos (com fallbacks)
        nome = body.get("nome") or body.get("name") or body.get("usuario") or "Anônimo"
        email = body.get("email") or body.get("e-mail") or body.get("mail") or ""
        feedback_text = body.get("feedback") or body.get("mensagem") or body.get("message") or ""
        
        if not feedback_text:
            raise HTTPException(status_code=400, detail="Campo 'feedback' é obrigatório")
        
        if not email:
            raise HTTPException(status_code=400, detail="Campo 'email' é obrigatório")
        
        # Análise de sentimento
        sentimento = analyze_sentiment(feedback_text)
        
        # Salvar no banco
        novo_feedback = Feedback(
            nome=nome,
            email=email,
            feedback=feedback_text,
            sentimento=sentimento,
            data_recebimento=datetime.utcnow()
        )
        
        db.add(novo_feedback)
        db.commit()
        db.refresh(novo_feedback)
        
        # Log
        log_entry = Log(
            event_type="WEBHOOK_RAW_FEEDBACK",
            message=f"Feedback recebido via webhook raw de {email}",
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        
        return {
            "status": "success",
            "message": "Feedback recebido e processado com sucesso",
            "data": {
                "id": novo_feedback.id,
                "sentimento": sentimento,
                "data_recebimento": novo_feedback.data_recebimento.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# ENDPOINT PARA CONSULTAR FEEDBACKS
@router.get("/api/feedback", response_model=List[FeedbackResponse])
async def listar_feedbacks(
    skip: int = 0,
    limit: int = 50,
    sentimento: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Listar feedbacks com filtros opcionais
    """
    try:
        query = db.query(Feedback)
        
        if sentimento:
            query = query.filter(Feedback.sentimento == sentimento)
        
        if email:
            query = query.filter(Feedback.email.ilike(f"%{email}%"))
        
        feedbacks = query.order_by(Feedback.data_recebimento.desc()).offset(skip).limit(limit).all()
        
        return [
            FeedbackResponse(
                id=f.id,
                nome=f.nome,
                email=f.email,
                feedback=f.feedback,
                sentimento=f.sentimento,
                data_recebimento=f.data_recebimento,
                status="processado"
            ) for f in feedbacks
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar feedbacks: {str(e)}")

# ENDPOINT PARA ESTATÍSTICAS
@router.get("/api/feedback/stats")
async def estatisticas_feedback(db: Session = Depends(get_db)):
    """
    Obter estatísticas dos feedbacks
    """
    try:
        from sqlalchemy import func
        
        # Total de feedbacks
        total = db.query(func.count(Feedback.id)).scalar()
        
        # Contagem por sentimento
        sentimentos = db.query(
            Feedback.sentimento,
            func.count(Feedback.id).label('count')
        ).group_by(Feedback.sentimento).all()
        
        # Feedbacks por dia (últimos 7 dias)
        from datetime import datetime, timedelta
        sete_dias_atras = datetime.utcnow() - timedelta(days=7)
        
        feedbacks_recentes = db.query(
            func.date(Feedback.data_recebimento).label('data'),
            func.count(Feedback.id).label('count')
        ).filter(
            Feedback.data_recebimento >= sete_dias_atras
        ).group_by(
            func.date(Feedback.data_recebimento)
        ).all()
        
        return {
            "total_feedbacks": total,
            "por_sentimento": {s.sentimento or "indefinido": s.count for s in sentimentos},
            "ultimos_7_dias": [
                {"data": str(f.data), "total": f.count} for f in feedbacks_recentes
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")
