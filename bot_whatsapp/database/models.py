from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telefone = Column(String(15), unique=True, nullable=False)
    nome = Column(String(100), nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)

    # Relacionamento com mensagens
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    mensagem = Column(Text, nullable=False)
    resposta = Column(Text, nullable=True)
    data_envio = Column(DateTime, default=datetime.utcnow)
    numero = Column(Text, nullable=True)  # Campo adicional para compatibilidade

    # Relacionamento com usuário
    user = relationship("User", back_populates="messages")

class Feedback(Base):
    """
    Tabela para armazenar feedbacks recebidos via webhook
    """
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    feedback = Column(Text, nullable=False)
    sentimento = Column(String(20), nullable=True)  # positivo, negativo, neutro
    data_recebimento = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback(id={self.id}, email='{self.email}', sentimento='{self.sentimento}')>"

class BotConfig(Base):
    """
    Configurações do bot
    """
    __tablename__ = "bot_config"
    
    id = Column(Integer, primary_key=True, index=True)
    bot_name = Column(String(50), nullable=False, default="WhatsApp Bot")
    default_response = Column(Text, nullable=False, default="Obrigado pela sua mensagem!")

class PredefinedResponse(Base):
    """
    Respostas predefinidas para palavras-chave
    """
    __tablename__ = "predefined_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Log(Base):
    """
    Logs do sistema
    """
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Log(id={self.id}, event_type='{self.event_type}')>"
