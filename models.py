"""
Sistema de Ficha Técnica - Models SQLAlchemy
Estrutura Simples e Eficiente
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Cliente(Base):
    """Clientes"""
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    contato = Column(String(100))
    telefone = Column(String(20))
    email = Column(String(100))
    cnpj = Column(String(18))
    logo_path = Column(String(500))
    ativo = Column(Integer, default=1)
    data_cadastro = Column(DateTime, default=datetime.now)
    
    fichas_tecnicas = relationship("FichaTecnica", back_populates="cliente")
    custos_operacionais = relationship("CustoOperacional", back_populates="cliente")


class Insumo(Base):
    """Insumos/Ingredientes"""
    __tablename__ = 'insumos'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    unidade_medida = Column(String(20), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    fornecedor = Column(String(200))
    observacoes = Column(Text)
    ativo = Column(Integer, default=1)
    data_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    itens_ficha = relationship("ItemFichaTecnica", back_populates="insumo")


class CustoOperacional(Base):
    """Custos Fixos e Variáveis por Cliente"""
    __tablename__ = 'custos_operacionais'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    tipo = Column(String(20), nullable=False)
    descricao = Column(String(200), nullable=False)
    valor_mensal = Column(Numeric(10, 2), nullable=False)
    ativo = Column(Integer, default=1)
    
    cliente = relationship("Cliente", back_populates="custos_operacionais")


class FichaTecnica(Base):
    """Fichas Técnicas (Receitas)"""
    __tablename__ = 'fichas_tecnicas'
    
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    codigo = Column(String(50), nullable=False)
    nome = Column(String(200), nullable=False)
    categoria = Column(String(100))
    rendimento = Column(String(100))
    tempo_preparo = Column(Integer)
    observacoes = Column(Text)
    
    custo_insumos = Column(Numeric(10, 2), default=0)
    custo_total = Column(Numeric(10, 2), default=0)
    margem_percentual = Column(Numeric(5, 2), default=0)
    preco_venda = Column(Numeric(10, 2), default=0)
    
    ativo = Column(Integer, default=1)
    data_criacao = Column(DateTime, default=datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    cliente = relationship("Cliente", back_populates="fichas_tecnicas")
    itens = relationship("ItemFichaTecnica", back_populates="ficha_tecnica", cascade="all, delete-orphan")


class ItemFichaTecnica(Base):
    """Ingredientes de uma Ficha Técnica"""
    __tablename__ = 'itens_ficha_tecnica'
    
    id = Column(Integer, primary_key=True)
    ficha_tecnica_id = Column(Integer, ForeignKey('fichas_tecnicas.id'), nullable=False)
    insumo_id = Column(Integer, ForeignKey('insumos.id'), nullable=False)
    quantidade = Column(Numeric(10, 3), nullable=False)
    custo_item = Column(Numeric(10, 2), default=0)
    ordem = Column(Integer, default=0)
    
    ficha_tecnica = relationship("FichaTecnica", back_populates="itens")
    insumo = relationship("Insumo", back_populates="itens_ficha")
