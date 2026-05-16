"""
SISTEMA DE FICHA TÉCNICA - VERSÃO COMPLETA
Interface Intuitiva e Responsiva
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

st.markdown("""
<style>
    .main-title {font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem;}
    .stButton>button {border-radius: 5px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

init_db()

if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()

db = st.session_state.db

# SIDEBAR
st.sidebar.markdown("# 📋 Sistema de Ficha Técnica")
st.sidebar.markdown("---")

menu = st.sidebar.radio("**Navegação:**", [
    "🏠 Início", "👥 Clientes", "📦 Insumos",
    "💰 Custos Operacionais", "📝 Fichas Técnicas", "💵 Precificação"
])

st.sidebar.markdown("---")
total_clientes = db.query(Cliente).filter(Cliente.ativo == 1).count()
total_insumos = db.query(Insumo).filter(Insumo.ativo == 1).count()
total_fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).count()

st.sidebar.metric("Clientes", total_clientes)
st.sidebar.metric("Insumos", total_insumos)
st.sidebar.metric("Fichas", total_fichas)

# ==================== INÍCIO ====================
if menu == "🏠 Início":
    st.markdown('<p class="main-title">📋 Sistema de Ficha Técnica</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    col1.info("### 👥 Clientes\nGerencie clientes")
    col2.info("### 📦 Insumos\nGerencie ingredientes")
    col3.info("### 📝 Fichas\nCrie receitas")
    
    st.markdown("---")
    if total_clientes == 0:
        st.warning("👉 Cadastre clientes primeiro")
    elif total_insumos == 0:
        st.warning("👉 Cadastre insumos agora")
    elif total_fichas == 0:
        st.success("✅ Pronto! Crie fichas técnicas")

# ==================== CLIENTES ====================
elif menu == "👥 Clientes":
    st.markdown('<p class="main-title">👥 Clientes</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
    
    with tab1:
        clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
        if clientes:
            st.subheader(f"Total: {len(clientes)}")
            
            df = pd.DataFrame([
                {'ID': c.id, 'Nome': c.nome, 'Telefone': c.telefone or '-', 'Email': c.email or '-'}
                for c in clientes
            ])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            with st.expander("🎨 Logos"):
                for cliente in clientes:
                    st.markdown(f"### {cliente.nome}")
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if cliente.logo_path:
                            try:
                                logo = carregar_logo_cliente(cliente.logo_path)
                                if logo:
                                    st.image(logo, width=150)
                            except:
                                st.caption("❌ Erro")
                        else:
                            st.caption("📷 Sem logo")
                    
                    with col2:
                        nova = st.file_uploader("Upload:", type=['png','jpg','jpeg'], key=f"l{cliente.id}")
                        if nova and st.button("💾 Salvar", key=f"s{cliente.id}"):
                            try:
                                path = salvar_logo_cliente(cliente.id, nova)
                                if path:
                                    if cliente.logo_path:
                                        deletar_logo_cliente(cliente.logo_path)
                                    cliente.logo_path = path
                                    db.commit()
                                    st.success("✅ Salvo!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ {e}")
                        
                        if cliente.logo_path and st.button("🗑️ Remover", key=f"d{cliente.id}"):
                            deletar_logo_cliente(cliente.logo_path)
                            cliente.logo_path = None
                            db.commit()
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("📭 Nenhum cliente")
    
    with tab2:
        with st.form("form_cliente", clear_on_submit=True):
            nome = st.text_input("* Nome:", placeholder="Padaria Pão Quente")
            telefone = st.text_input("Telefone:")
            email = st.text_input("Email:")
            logo = st.file_uploader("Logo:", type=['png','jpg','jpeg'])
            
            if st.form_submit_button("💾 Salvar", type="primary"):
                if nome:
                    try:
                        c = Cliente(nome=nome, telefone=telefone, email=email)
                        db.add(c)
                        db.flush()
                        if logo:
                            path = salvar_logo_cliente(c.id, logo)
                            if path:
                                c.logo_path = path
                        db.commit()
                        st.success(f"✅ '{nome}' cadastrado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
                        db.rollback()

# ==================== INSUMOS ====================
elif menu == "📦 Insumos":
    st.markdown('<p class="main-title">📦 Insumos</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
    
    with tab1:
        insumos = db.query(Insumo).filter(Insumo.ativo == 1).all()
        if insumos:
            st.subheader(f"Total: {len(insumos)}")
            
            df = pd.DataFrame([
                {'ID': i.id, 'Nome': i.nome, 'Unidade': i.unidade_medida,
                 'Preço': float(i.preco_unitario), 'Fornecedor': i.fornecedor or '-'}
                for i in insumos
            ])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 Nenhum insumo")
    
    with tab2:
        with st.form("form_insumo", clear_on_submit=True):
            nome = st.text_input("* Nome:", placeholder="Farinha de Trigo")
            col1, col2 = st.columns(2)
            with col1:
                unidade = st.selectbox("* Unidade:", ["kg", "g", "L", "ml", "unidade", "dúzia"])
            with col2:
                preco = st.number_input("* Preço (R$):", min_value=0.0, format="%.2f")
            fornecedor = st.text_input("Fornecedor:")
            
            if st.form_submit_button("💾 Salvar", type="primary"):
                if nome and preco > 0:
                    try:
                        i = Insumo(nome=nome, unidade_medida=unidade,
                                  preco_unitario=Decimal(str(preco)), fornecedor=fornecedor)
                        db.add(i)
                        db.commit()
                        st.success(f"✅ '{nome}' cadastrado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

# ==================== CUSTOS ====================
elif menu == "💰 Custos Operacionais":
    st.markdown('<p class="main-title">💰 Custos Operacionais</p>', unsafe_allow_html=True)
    
    clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
    if not clientes:
        st.warning("⚠️ Cadastre clientes primeiro!")
    else:
        cliente_nome = st.selectbox("Cliente:", [c.nome for c in clientes])
        cliente_id = next(c.id for c in clientes if c.nome == cliente_nome)
        
        tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
        
        with tab1:
            custos = db.query(CustoOperacional).filter(
                CustoOperacional.cliente_id == cliente_id,
                CustoOperacional.ativo == 1
            ).all()
            
            if custos:
                df = pd.DataFrame([
                    {'Tipo': c.tipo.upper(), 'Descrição': c.descricao, 'Valor': float(c.valor_mensal)}
                    for c in custos
                ])
                st.dataframe(df, use_container_width=True, hide_index=True)
                total = sum(float(c.valor_mensal) for c in custos)
                st.metric("**Total Mensal**", f"R$ {total:,.2f}")
            else:
                st.info("📭 Nenhum custo")
        
        with tab2:
            with st.form("form_custo"):
                tipo = st.radio("Tipo:", ["Fixo", "Variável"])
                descricao = st.text_input("Descrição:", placeholder="Aluguel, Energia...")
                valor = st.number_input("Valor Mensal (R$):", min_value=0.0, format="%.2f")
                
                if st.form_submit_button("💾 Salvar", type="primary"):
                    if descricao and valor > 0:
                        c = CustoOperacional(
                            cliente_id=cliente_id,
                            tipo='fixo' if tipo == "Fixo" else 'variavel',
                            descricao=descricao,
                            valor_mensal=Decimal(str(valor))
                        )
                        db.add(c)
                        db.commit()
                        st.success("✅ Custo cadastrado!")
                        st.rerun()

# ==================== FICHAS ====================
elif menu == "📝 Fichas Técnicas":
    st.markdown('<p class="main-title">📝 Fichas Técnicas</p>', unsafe_allow_html=True)
    
    if db.query(Cliente).filter(Cliente.ativo == 1).count() == 0:
        st.warning("⚠️ Cadastre clientes primeiro!")
    elif db.query(Insumo).filter(Insumo.ativo == 1).count() == 0:
        st.warning("⚠️ Cadastre insumos primeiro!")
    else:
        tab1, tab2 = st.tabs(["📋 Minhas Fichas", "➕ Nova Ficha"])
        
        with tab1:
            fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
            if fichas:
                for ficha in fichas:
                    with st.expander(f"📝 {ficha.codigo} - {ficha.nome}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Custo", f"R$ {float(ficha.custo_insumos):,.2f}")
                        col2.metric("Total", f"R$ {float(ficha.custo_total):,.2f}")
                        col3.metric("Venda", f"R$ {float(ficha.preco_venda):,.2f}")
                        
                        st.markdown("**Ingredientes:**")
                        for item in ficha.itens:
                            st.write(f"• {item.insumo.nome}: {float(item.quantidade)} {item.insumo.unidade_medida}")
                        
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        if col1.button("📊 Excel", key=f"xe{ficha.id}"):
                            excel = gerar_excel_ficha(ficha)
                            st.download_button("💾 Baixar Excel", excel,
                                             f"ficha_{ficha.codigo}.xlsx",
                                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                             key=f"de{ficha.id}")
                        
                        if col2.button("📄 PDF", key=f"xp{ficha.id}"):
                            pdf = gerar_pdf_ficha(ficha)
                            st.download_button("💾 Baixar PDF", pdf,
                                             f"ficha_{ficha.codigo}.pdf",
                                             "application/pdf",
                                             key=f"dp{ficha.id}")
            else:
                st.info("📭 Nenhuma ficha")
        
        with tab2:
            if 'ingredientes' not in st.session_state:
                st.session_state.ingredientes = []
            
            clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
            cliente_nome = st.selectbox("* Cliente:", [c.nome for c in clientes])
            cliente_id = next(c.id for c in clientes if c.nome == cliente_nome)
            
            col1, col2 = st.columns(2)
            with col1:
                codigo = st.text_input("* Código:", placeholder="REC001")
                nome = st.text_input("* Nome:", placeholder="Pão Francês")
            with col2:
                categoria = st.text_input("Categoria:", placeholder="Pães")
                rendimento = st.text_input("Rendimento:", placeholder="50 unidades")
            
            st.markdown("---")
            st.subheader("🥖 Ingredientes")
            
            col1, col2, col3 = st.columns([3, 2, 1])
            insumos = db.query(Insumo).filter(Insumo.ativo == 1).all()
            
            with col1:
                insumo_nome = st.selectbox("Insumo:", 
                    [f"{i.nome} (R$ {float(i.preco_unitario):.2f}/{i.unidade_medida})" for i in insumos])
            with col2:
                qtd = st.number_input("Quantidade:", min_value=0.0, value=1.0, step=0.1)
            with col3:
                st.write("")
                st.write("")
                if st.button("➕", use_container_width=True):
                    insumo_id = next(i.id for i in insumos if i.nome in insumo_nome)
                    insumo = next(i for i in insumos if i.id == insumo_id)
                    custo = float(qtd) * float(insumo.preco_unitario)
                    
                    st.session_state.ingredientes.append({
                        'insumo_id': insumo.id,
                        'nome': insumo.nome,
                        'qtd': qtd,
                        'unidade': insumo.unidade_medida,
                        'preco': float(insumo.preco_unitario),
                        'custo': custo
                    })
                    st.rerun()
            
            if st.session_state.ingredientes:
                st.markdown("### Adicionados:")
                custo_total = 0
                for idx, ing in enumerate(st.session_state.ingredientes):
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                    col1.write(f"**{ing['nome']}**")
                    col2.write(f"{ing['qtd']} {ing['unidade']}")
                    col3.write(f"R$ {ing['preco']:.2f}")
                    col4.write(f"R$ {ing['custo']:.2f}")
                    if col5.button("🗑️", key=f"del{idx}"):
                        st.session_state.ingredientes.pop(idx)
                        st.rerun()
                    custo_total += ing['custo']
                
                st.markdown("---")
                st.metric("**CUSTO TOTAL**", f"R$ {custo_total:,.2f}")
                
                if st.button("💾 SALVAR FICHA", type="primary", use_container_width=True):
                    if codigo and nome:
                        ficha = FichaTecnica(
                            cliente_id=cliente_id, codigo=codigo, nome=nome,
                            categoria=categoria, rendimento=rendimento,
                            custo_insumos=Decimal(str(custo_total)),
                            custo_total=Decimal(str(custo_total))
                        )
                        db.add(ficha)
                        db.flush()
                        
                        for idx, ing in enumerate(st.session_state.ingredientes):
                            item = ItemFichaTecnica(
                                ficha_tecnica_id=ficha.id,
                                insumo_id=ing['insumo_id'],
                                quantidade=Decimal(str(ing['qtd'])),
                                custo_item=Decimal(str(ing['custo'])),
                                ordem=idx
                            )
                            db.add(item)
                        
                        db.commit()
                        st.success(f"✅ Ficha '{nome}' criada!")
                        st.session_state.ingredientes = []
                        st.rerun()

# ==================== PRECIFICAÇÃO ====================
elif menu == "💵 Precificação":
    st.markdown('<p class="main-title">💵 Precificação</p>', unsafe_allow_html=True)
    
    fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
    if not fichas:
        st.info("📭 Crie fichas técnicas primeiro!")
    else:
        ficha_nome = st.selectbox("Ficha:", [f"{f.codigo} - {f.nome}" for f in fichas])
        ficha_id = next(f.id for f in fichas if f"{f.codigo} - {f.nome}" == ficha_nome)
        ficha = db.query(FichaTecnica).get(ficha_id)
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Custos")
            st.metric("Insumos", f"R$ {float(ficha.custo_insumos):,.2f}")
            
            custos = db.query(CustoOperacional).filter(
                CustoOperacional.cliente_id == ficha.cliente_id,
                CustoOperacional.ativo == 1
            ).all()
            total_op = sum(float(c.valor_mensal) for c in custos)
            st.metric("Operacionais/mês", f"R$ {total_op:,.2f}")
            
            custo_total = float(ficha.custo_insumos) + (total_op / 30)
            st.metric("**TOTAL**", f"R$ {custo_total:,.2f}")
        
        with col2:
            st.subheader("💰 Preço de Venda")
            margem = st.slider("Margem (%):", 0, 200, 30)
            preco = custo_total * (1 + margem/100)
            st.metric("**PREÇO SUGERIDO**", f"R$ {preco:,.2f}")
            
            if st.button("💾 Salvar Preço", type="primary", use_container_width=True):
                ficha.custo_total = Decimal(str(custo_total))
                ficha.margem_percentual = Decimal(str(margem))
                ficha.preco_venda = Decimal(str(preco))
                db.commit()
                st.success("✅ Preço salvo!")
                st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'><p>Sistema de Ficha Técnica v1.0</p></div>", unsafe_allow_html=True)
