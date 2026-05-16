"""
SISTEMA DE FICHA TÉCNICA
Interface Intuitiva e Responsiva
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal
import sys
from pathlib import Path

# Adiciona diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_db
from models import Cliente, Insumo, CustoOperacional, FichaTecnica, ItemFichaTecnica
from exportacao import gerar_excel_ficha, gerar_pdf_ficha
from gerenciador_logos import salvar_logo_cliente, carregar_logo_cliente, deletar_logo_cliente

# Configuração da página
st.set_page_config(
    page_title="Sistema de Ficha Técnica",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 5px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Inicializa banco
init_db()

# Sessão do banco
if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()

db = st.session_state.db

# ==================== SIDEBAR ====================

st.sidebar.markdown("# 📋 Sistema de Ficha Técnica")
st.sidebar.markdown("### Gestão Completa de Custos")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "**Navegação:**",
    [
        "🏠 Início",
        "👥 Clientes", 
        "📦 Insumos",
        "💰 Custos Operacionais",
        "📝 Fichas Técnicas",
        "💵 Precificação"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estatísticas")
total_clientes = db.query(Cliente).filter(Cliente.ativo == 1).count()
total_insumos = db.query(Insumo).filter(Insumo.ativo == 1).count()
total_fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).count()

st.sidebar.metric("Clientes", total_clientes)
st.sidebar.metric("Insumos", total_insumos)
st.sidebar.metric("Fichas Técnicas", total_fichas)

# ==================== INÍCIO ====================

if menu == "🏠 Início":
    st.markdown('<p class="main-title">📋 Sistema de Ficha Técnica</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Gestão Completa de Custos e Precificação</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 👥 Clientes\nCadastre e gerencie seus clientes")
    
    with col2:
        st.info("### 📦 Insumos\nGerencie ingredientes e preços")
    
    with col3:
        st.info("### 📝 Fichas Técnicas\nCrie e calcule custos de receitas")
    
    st.markdown("---")
    
    if total_clientes == 0:
        st.warning("👉 **Comece cadastrando clientes** no menu '👥 Clientes'")
    elif total_insumos == 0:
        st.warning("👉 **Cadastre insumos** no menu '📦 Insumos' para criar fichas técnicas")
    elif total_fichas == 0:
        st.success("✅ Sistema pronto! **Crie sua primeira ficha técnica** em '📝 Fichas Técnicas'")

# ==================== CLIENTES ====================

elif menu == "👥 Clientes":
    st.markdown('<p class="main-title">👥 Gerenciar Clientes</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista de Clientes", "➕ Adicionar Novo"])
    
    with tab1:
        clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
        
        if clientes:
            st.subheader(f"Total: {len(clientes)} clientes")
            
            # Tabela simples primeiro
            df_clientes = pd.DataFrame([
                {
                    'ID': c.id,
                    'Nome': c.nome,
                    'Telefone': c.telefone or '-',
                    'Email': c.email or '-'
                } for c in clientes
            ])
            
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
            
            # Gerenciar Logos
            st.markdown("---")
            with st.expander("🎨 Gerenciar Logos"):
                for cliente in clientes:
                    st.markdown(f"### {cliente.nome}")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if cliente.logo_path:
                            try:
                                logo_img = carregar_logo_cliente(cliente.logo_path)
                                if logo_img:
                                    st.image(logo_img, width=150)
                                else:
                                    st.caption("❌ Logo não encontrada")
                            except:
                                st.caption("❌ Erro ao carregar logo")
                        else:
                            st.caption("📷 Sem logo")
                    
                    with col2:
                        nova_logo = st.file_uploader(
                            "Upload nova logo:",
                            type=['png', 'jpg', 'jpeg'],
                            key=f"logo_{cliente.id}"
                        )
                        
                        if nova_logo:
                            if st.button("💾 Salvar", key=f"save_{cliente.id}"):
                                try:
                                    logo_path = salvar_logo_cliente(cliente.id, nova_logo)
                                    if logo_path:
                                        if cliente.logo_path:
                                            deletar_logo_cliente(cliente.logo_path)
                                        cliente.logo_path = logo_path
                                        db.commit()
                                        st.success("✅ Logo salva!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Erro: {e}")
                        
                        if cliente.logo_path:
                            if st.button("🗑️ Remover Logo", key=f"del_{cliente.id}"):
                                deletar_logo_cliente(cliente.logo_path)
                                cliente.logo_path = None
                                db.commit()
                                st.success("✅ Logo removida!")
                                st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("📭 Nenhum cliente cadastrado")
    
    with tab2:
        with st.form("form_cliente", clear_on_submit=True):
            st.subheader("Cadastrar Novo Cliente")
            
            nome = st.text_input("* Nome:", placeholder="Ex: Padaria Pão Quente")
            telefone = st.text_input("Telefone:", placeholder="Ex: (47) 99999-9999")
            email = st.text_input("Email:", placeholder="Ex: contato@padaria.com")
            logo_file = st.file_uploader("Logo:", type=['png', 'jpg', 'jpeg'])
            
            submitted = st.form_submit_button("💾 Salvar Cliente", type="primary")
            
            if submitted and nome:
                try:
                    novo_cliente = Cliente(nome=nome, telefone=telefone, email=email)
                    db.add(novo_cliente)
                    db.flush()
                    
                    if logo_file:
                        logo_path = salvar_logo_cliente(novo_cliente.id, logo_file)
                        if logo_path:
                            novo_cliente.logo_path = logo_path
                    
                    db.commit()
                    st.success(f"✅ Cliente '{nome}' cadastrado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
                    db.rollback()

# Continua com outros menus...
st.info("💡 Outros menus em desenvolvimento...")
