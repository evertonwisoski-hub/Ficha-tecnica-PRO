"""
Sistema de Autenticação - Ficha Técnica PRO
Autor: Claude + Everton
Data: 2024
"""

import streamlit as st
import bcrypt
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base SQLAlchemy
Base = declarative_base()

# Modelo de Usuário
class User(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='user')  # 'admin' ou 'user'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class AuthSystem:
    """Sistema de autenticação completo"""
    
    def __init__(self, db_path='ficha_tecnica.db'):
        """Inicializa sistema de autenticação"""
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def hash_password(self, password: str) -> str:
        """Criptografa senha com bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica se senha está correta"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> bool:
        """Cria novo usuário"""
        try:
            # Verifica se username já existe
            existing_user = self.session.query(User).filter_by(username=username).first()
            if existing_user:
                return False, "Usuário já existe!"
            
            # Verifica se email já existe
            existing_email = self.session.query(User).filter_by(email=email).first()
            if existing_email:
                return False, "Email já cadastrado!"
            
            # Cria usuário
            password_hash = self.hash_password(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                role=role
            )
            
            self.session.add(new_user)
            self.session.commit()
            return True, "Usuário criado com sucesso!"
            
        except Exception as e:
            self.session.rollback()
            return False, f"Erro ao criar usuário: {str(e)}"
    
    def authenticate(self, username: str, password: str) -> tuple:
        """Autentica usuário"""
        try:
            user = self.session.query(User).filter_by(username=username).first()
            
            if not user:
                return False, None, "Usuário não encontrado!"
            
            if not user.is_active:
                return False, None, "Usuário desativado!"
            
            if not self.verify_password(password, user.password_hash):
                return False, None, "Senha incorreta!"
            
            # Atualiza último login
            user.last_login = datetime.now()
            self.session.commit()
            
            return True, user, "Login realizado com sucesso!"
            
        except Exception as e:
            return False, None, f"Erro ao autenticar: {str(e)}"
    
    def get_all_users(self):
        """Retorna todos os usuários"""
        return self.session.query(User).all()
    
    def get_user_by_id(self, user_id: int):
        """Retorna usuário por ID"""
        return self.session.query(User).filter_by(id=user_id).first()
    
    def update_user(self, user_id: int, **kwargs):
        """Atualiza dados do usuário"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Usuário não encontrado!"
            
            for key, value in kwargs.items():
                if key == 'password':
                    value = self.hash_password(value)
                    setattr(user, 'password_hash', value)
                elif hasattr(user, key):
                    setattr(user, key, value)
            
            self.session.commit()
            return True, "Usuário atualizado com sucesso!"
            
        except Exception as e:
            self.session.rollback()
            return False, f"Erro ao atualizar usuário: {str(e)}"
    
    def deactivate_user(self, user_id: int):
        """Desativa usuário"""
        return self.update_user(user_id, is_active=False)
    
    def activate_user(self, user_id: int):
        """Ativa usuário"""
        return self.update_user(user_id, is_active=True)
    
    def has_users(self) -> bool:
        """Verifica se existe algum usuário cadastrado"""
        return self.session.query(User).count() > 0
    
    def count_users(self) -> int:
        """Conta total de usuários"""
        return self.session.query(User).count()
    
    def count_admins(self) -> int:
        """Conta total de admins"""
        return self.session.query(User).filter_by(role='admin').count()


# Funções auxiliares para Streamlit
def check_authentication():
    """Verifica se usuário está autenticado"""
    return st.session_state.get('authenticated', False)

def get_current_user():
    """Retorna usuário atual da sessão"""
    return st.session_state.get('current_user', None)

def is_admin():
    """Verifica se usuário atual é admin"""
    user = get_current_user()
    return user and user.get('role') == 'admin'

def logout():
    """Faz logout do usuário"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.rerun()

def login_user(user):
    """Faz login do usuário na sessão"""
    st.session_state.authenticated = True
    st.session_state.current_user = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }
