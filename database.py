"""
Configuração do Banco de Dados SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Configuração SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./ficha_tecnica.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Cria todas as tabelas"""
    Base.metadata.create_all(bind=engine)
    print("✅ Banco de dados inicializado!")

def get_db():
    """Retorna sessão do banco"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
