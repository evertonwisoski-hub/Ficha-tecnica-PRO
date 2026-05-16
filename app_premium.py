"""
SISTEMA DE FICHA TÉCNICA - VERSÃO PREMIUM
Interface Moderna e Profissional
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_db
from models import Cliente, Insumo, CustoOperacional, FichaTecnica, ItemFichaTecnica
from exportacao import gerar_excel_ficha, gerar_pdf_ficha
from gerenciador_logos import salvar_logo_cliente, carregar_logo_cliente, deletar_logo_cliente

st.set_page_config(
    page_title="Sistema de Ficha Técnica",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS PREMIUM - Design Moderno
st.markdown("""
<style>
    /* Importar fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Configurações globais */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Fundo com gradiente sutil */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Títulos elegantes */
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-align: center;
        animation: fadeIn 1s ease-in;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    /* Cards modernos com sombra */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Botões modernos */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 2rem;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Inputs modernos */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background: transparent;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Métricas do sidebar */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    /* Dataframes modernos */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    /* Expanders elegantes */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        font-weight: 600;
        border: 2px solid #e2e8f0;
    }
    
    /* Forms com cards */
    [data-testid="stForm"] {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Alertas modernos */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
        animation: slideIn 0.5s ease;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Info boxes com gradiente */
    .stInfo {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #10b98115 0%, #0ea77015 100%);
        border-left: 4px solid #10b981;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b15 0%, #d9770615 100%);
        border-left: 4px solid #f59e0b;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef444415 0%, #dc262615 100%);
        border-left: 4px solid #ef4444;
    }
    
    /* Upload de arquivos */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 15px;
        border: 2px dashed #cbd5e1;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #667eea05;
    }
    
    /* Slider moderno */
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

init_db()

if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()

db = st.session_state.db

# ==================== SIDEBAR PREMIUM ====================
st.sidebar.markdown("# 📋 Ficha Técnica PRO")
st.sidebar.markdown("### Sistema de Gestão de Custos")
st.sidebar.markdown("---")

menu = st.sidebar.radio("**Navegação:**", [
    "🏠 Início", "👥 Clientes", "📦 Insumos",
    "💰 Custos Operacionais", "📝 Fichas Técnicas", "💵 Precificação"
], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Resumo Geral")
total_clientes = db.query(Cliente).filter(Cliente.ativo == 1).count()
total_insumos = db.query(Insumo).filter(Insumo.ativo == 1).count()
total_fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).count()

st.sidebar.metric("👥 Clientes", total_clientes)
st.sidebar.metric("📦 Insumos", total_insumos)
st.sidebar.metric("📝 Fichas", total_fichas)

# ==================== INÍCIO PREMIUM ====================
if menu == "🏠 Início":
    st.markdown('<p class="main-title">📋 Sistema de Ficha Técnica</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Gestão Profissional de Custos e Precificação</p>', unsafe_allow_html=True)
    
    # Cards de ação com ícones grandes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center;">
                <div style="font-size: 4rem;">👥</div>
                <h2 style="color: #667eea; margin: 1rem 0;">Clientes</h2>
                <p style="color: #64748b;">Gerencie sua carteira de clientes com logos personalizadas</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center;">
                <div style="font-size: 4rem;">📦</div>
                <h2 style="color: #764ba2; margin: 1rem 0;">Insumos</h2>
                <p style="color: #64748b;">Controle preços e fornecedores em tempo real</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="text-align: center;">
                <div style="font-size: 4rem;">📝</div>
                <h2 style="color: #667eea; margin: 1rem 0;">Fichas</h2>
                <p style="color: #64748b;">Crie receitas e exporte em Excel/PDF</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Status do sistema
    if total_clientes == 0:
        st.warning("👉 **Comece cadastrando clientes** para começar a usar o sistema")
    elif total_insumos == 0:
        st.info("👉 **Cadastre insumos** para poder criar fichas técnicas")
    elif total_fichas == 0:
        st.success("✅ **Sistema pronto!** Crie sua primeira ficha técnica agora")
    else:
        # Dashboard com métricas visuais
        st.markdown("### 📊 Visão Geral do Sistema")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("👥 Clientes Ativos", total_clientes, delta="Crescendo")
        col2.metric("📦 Insumos Cadastrados", total_insumos, delta="Atualizado")
        col3.metric("📝 Fichas Criadas", total_fichas, delta="Operacional")
        
        # Calcular valor médio das fichas
        fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
        if fichas:
            valor_medio = sum(float(f.custo_insumos) for f in fichas) / len(fichas)
            col4.metric("💰 Custo Médio", f"R$ {valor_medio:.2f}", delta="Por ficha")

# Continua nos próximos arquivos... (Clientes, Insumos, etc)
# Vou criar em partes para não quebrar

st.info("💡 **Outras seções sendo finalizadas...** Use o menu lateral para navegar!")
