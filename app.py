"""
SISTEMA DE FICHA TÉCNICA - VERSÃO PREMIUM COMPLETA
Interface Moderna e Profissional
✨ ATUALIZADO: Suporte a Fichas Aninhadas
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_db
from models import Cliente, Insumo, CustoOperacional, FichaTecnica, ItemFichaTecnica
from exportacao_premium import gerar_excel_ficha, gerar_pdf_ficha
from gerenciador_logos import salvar_logo_cliente, carregar_logo_cliente, deletar_logo_cliente

# Importar módulos de fichas aninhadas
try:
    from calculos_custos import (
        validar_dependencia_circular,
        calcular_custo_ficha_recursivo,
        recalcular_todas_fichas,
        obter_hierarquia_ingredientes
    )
    FICHAS_ANINHADAS_DISPONIVEL = True
except ImportError:
    FICHAS_ANINHADAS_DISPONIVEL = False

st.set_page_config(page_title="Ficha Técnica PRO", page_icon="📋", layout="wide")

# CSS PREMIUM
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * {font-family: 'Poppins', sans-serif;}
    .main {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    [data-testid="stSidebar"] {background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);}
    [data-testid="stSidebar"] * {color: white !important;}
    .main-title {font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem;}
    .subtitle {font-size: 1.2rem; color: #64748b; text-align: center; margin-bottom: 2rem;}
    .card {background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0; transition: all 0.3s;}
    .card:hover {transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.15);}
    .stButton>button {border-radius: 12px; font-weight: 600; padding: 0.7rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
        border: none; box-shadow: 0 4px 15px rgba(102,126,234,0.4); transition: all 0.3s;}
    .stButton>button:hover {transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102,126,234,0.6);}
    .stTabs [data-baseweb="tab-list"] {gap: 1rem; background: white; padding: 1rem; border-radius: 15px;}
    .stTabs [aria-selected="true"] {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important;}
    [data-testid="stMetric"] {background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

init_db()

# Migração automática (executa só uma vez)
if FICHAS_ANINHADAS_DISPONIVEL and not os.path.exists('.migrado'):
    try:
        from migrar_fichas_aninhadas import migrar_banco
        with st.spinner("🔄 Atualizando banco de dados..."):
            if migrar_banco():
                with open('.migrado', 'w') as f:
                    f.write('OK')
                st.success("✅ Sistema atualizado!")
    except Exception as e:
        st.warning(f"⚠️ Migração pendente: {e}")

if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()
db = st.session_state.db

# SIDEBAR
st.sidebar.markdown("# 📋 Ficha Técnica PRO")
if FICHAS_ANINHADAS_DISPONIVEL:
    st.sidebar.markdown("✨ *Fichas Aninhadas*")
st.sidebar.markdown("---")
menu = st.sidebar.radio("", ["🏠 Início", "👥 Clientes", "📦 Insumos", "💰 Custos", "📝 Fichas", "💵 Precificação"])
st.sidebar.markdown("---")
st.sidebar.metric("👥 Clientes", db.query(Cliente).filter(Cliente.ativo == 1).count())
st.sidebar.metric("📦 Insumos", db.query(Insumo).filter(Insumo.ativo == 1).count())
st.sidebar.metric("📝 Fichas", db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).count())

# INÍCIO
if menu == "🏠 Início":
    st.markdown('<p class="main-title">📋 Sistema de Ficha Técnica</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Gestão Profissional de Custos</p>', unsafe_allow_html=True)
    
    if FICHAS_ANINHADAS_DISPONIVEL:
        st.info("✨ **NOVO:** Suporte a fichas técnicas aninhadas! Use preparações intermediárias como ingredientes.")
    
    col1, col2, col3 = st.columns(3)
    for col, icon, title, desc in [
        (col1, "👥", "Clientes", "Gerencie clientes com logos"),
        (col2, "📦", "Insumos", "Controle preços e fornecedores"),
        (col3, "📝", "Fichas", "Crie receitas profissionais")
    ]:
        col.markdown(f"""<div class="card" style="text-align:center;">
            <div style="font-size:3.5rem;">{icon}</div>
            <h2 style="color:#667eea;margin:1rem 0;">{title}</h2>
            <p style="color:#64748b;">{desc}</p></div>""", unsafe_allow_html=True)

# CLIENTES
elif menu == "👥 Clientes":
    st.markdown('<p class="main-title">👥 Clientes</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
    
    with tab1:
        clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
        if clientes:
            st.subheader(f"📊 {len(clientes)} clientes cadastrados")
            df = pd.DataFrame([{'ID': c.id, 'Nome': c.nome, 'Telefone': c.telefone or '-', 'Email': c.email or '-'} for c in clientes])
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            with st.expander("🎨 Gerenciar Logos"):
                for c in clientes:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**{c.nome}**")
                        if c.logo_path:
                            try:
                                st.image(carregar_logo_cliente(c.logo_path), width=120)
                            except:
                                st.caption("❌ Erro")
                        else:
                            st.caption("📷 Sem logo")
                    with col2:
                        logo = st.file_uploader("Upload:", type=['png','jpg'], key=f"l{c.id}")
                        if logo:
                            path = salvar_logo_cliente(c.id, logo)
                            c.logo_path = path
                            db.commit()
                            st.success("✅")
                            st.rerun()
        else:
            st.info("📭 Nenhum cliente")
    
    with tab2:
        with st.form("fc", clear_on_submit=True):
            nome = st.text_input("* Nome:", placeholder="Padaria do João")
            col1, col2 = st.columns(2)
            tel = col1.text_input("Telefone:", placeholder="(49) 99999-9999")
            email = col2.text_input("Email:", placeholder="contato@email.com")
            if st.form_submit_button("💾 Salvar Cliente", type="primary", use_container_width=True):
                if nome:
                    db.add(Cliente(nome=nome, telefone=tel, email=email))
                    db.commit()
                    st.success(f"✅ '{nome}' cadastrado!")
                    st.rerun()

# INSUMOS
elif menu == "📦 Insumos":
    st.markdown('<p class="main-title">📦 Insumos</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
    
    with tab1:
        insumos = db.query(Insumo).filter(Insumo.ativo == 1).all()
        if insumos:
            st.subheader(f"📊 {len(insumos)} insumos cadastrados")
            df = pd.DataFrame([{
                'Nome': i.nome,
                'Unidade': i.unidade_medida,
                'Preço': f"R$ {float(i.preco_unitario):.2f}",
                'Fornecedor': i.fornecedor or '-'
            } for i in insumos])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 Nenhum insumo")
    
    with tab2:
        with st.form("fi", clear_on_submit=True):
            nome = st.text_input("* Nome:", placeholder="Farinha de Trigo")
            col1, col2 = st.columns(2)
            unidade = col1.selectbox("* Unidade:", ["kg", "g", "L", "ml", "unidade"])
            preco = col2.number_input("* Preço (R$):", min_value=0.0, format="%.2f")
            if st.form_submit_button("💾 Salvar Insumo", type="primary", use_container_width=True):
                if nome and preco > 0:
                    db.add(Insumo(nome=nome, unidade_medida=unidade, preco_unitario=Decimal(str(preco))))
                    db.commit()
                    st.success(f"✅ '{nome}' cadastrado!")
                    st.rerun()

# CUSTOS
elif menu == "💰 Custos":
    st.markdown('<p class="main-title">💰 Custos Operacionais</p>', unsafe_allow_html=True)
    clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
    if not clientes:
        st.warning("⚠️ Cadastre clientes primeiro!")
    else:
        cn = st.selectbox("Cliente:", [c.nome for c in clientes])
        cid = next(c.id for c in clientes if c.nome == cn)
        tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
        
        with tab1:
            custos = db.query(CustoOperacional).filter(CustoOperacional.cliente_id == cid, CustoOperacional.ativo == 1).all()
            if custos:
                df = pd.DataFrame([{'Tipo': c.tipo.upper(), 'Descrição': c.descricao, 'Valor': f"R$ {float(c.valor_mensal):.2f}"} for c in custos])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.metric("💰 Total Mensal", f"R$ {sum(float(c.valor_mensal) for c in custos):,.2f}")
            else:
                st.info("📭 Nenhum custo")
        
        with tab2:
            with st.form("fco"):
                tipo = st.radio("Tipo:", ["Fixo", "Variável"])
                desc = st.text_input("Descrição:")
                val = st.number_input("Valor (R$):", min_value=0.0, format="%.2f")
                if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
                    if desc and val > 0:
                        db.add(CustoOperacional(cliente_id=cid, tipo='fixo' if tipo=="Fixo" else 'variavel', descricao=desc, valor_mensal=Decimal(str(val))))
                        db.commit()
                        st.success("✅ Salvo!")
                        st.rerun()

# FICHAS (ATUALIZADO)
elif menu == "📝 Fichas":
    st.markdown('<p class="main-title">📝 Fichas Técnicas</p>', unsafe_allow_html=True)
    
    if db.query(Cliente).count() == 0 or db.query(Insumo).count() == 0:
        st.warning("⚠️ Cadastre clientes e insumos primeiro!")
    else:
        tab1, tab2 = st.tabs(["📋 Minhas Fichas", "➕ Nova"])
        
        with tab1:
            fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
            if fichas:
                if FICHAS_ANINHADAS_DISPONIVEL:
                    if st.button("🔄 Recalcular Custos"):
                        with st.spinner("Recalculando..."):
                            stats = recalcular_todas_fichas(db)
                            st.success(f"✅ {stats['processadas']} fichas!")
                            st.rerun()
                
                for f in fichas:
                    badge = "🔗" if (FICHAS_ANINHADAS_DISPONIVEL and f.eh_intermediaria) else "📝"
                    with st.expander(f"{badge} {f.codigo} - {f.nome}"):
                        cols = st.columns(4) if FICHAS_ANINHADAS_DISPONIVEL else st.columns(3)
                        cols[0].metric("Custo", f"R$ {float(f.custo_total):,.2f}")
                        cols[1].metric("Venda", f"R$ {float(f.preco_venda):,.2f}")
                        if FICHAS_ANINHADAS_DISPONIVEL:
                            if f.rendimento_gramas:
                                cols[2].metric("Rendimento", f"{float(f.rendimento_gramas):.0f}g")
                        
                        st.markdown("**Ingredientes:**")
                        
                        if FICHAS_ANINHADAS_DISPONIVEL:
                            try:
                                hierarquia = obter_hierarquia_ingredientes(db, f.id)
                                for item in hierarquia:
                                    nivel = item['nivel']
                                    indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * nivel
                                    prefixo = "└─ " if nivel > 0 else "• "
                                    
                                    if item['eh_aninhado']:
                                        st.markdown(f"{indent}{prefixo}**{item['nome']}** ({item['quantidade']:.1f}g) R$ {item['custo']:.2f}", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"{indent}{prefixo}{item['nome']} ({item['quantidade']:.1f}g) R$ {item['custo']:.2f}", unsafe_allow_html=True)
                            except:
                                for i in f.itens:
                                    if i.insumo:
                                        st.write(f"• {i.insumo.nome}: {float(i.quantidade)}g")
                        else:
                            for i in f.itens:
                                if i.insumo:
                                    st.write(f"• {i.insumo.nome}: {float(i.quantidade)}g")
                        
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        if col1.button("📊 Excel", key=f"xe{f.id}"):
                            excel = gerar_excel_ficha(f)
                            st.download_button("💾 Baixar", excel, f"ficha_{f.codigo}.xlsx", 
                                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"de{f.id}")
                        if col2.button("📄 PDF", key=f"xp{f.id}"):
                            pdf = gerar_pdf_ficha(f)
                            st.download_button("💾 Baixar", pdf, f"ficha_{f.codigo}.pdf", "application/pdf", key=f"dp{f.id}")
            else:
                st.info("📭 Nenhuma ficha")
        
        with tab2:
            if 'ing' not in st.session_state:
                st.session_state.ing = []
            
            clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
            cn = st.selectbox("* Cliente:", [c.nome for c in clientes])
            cid = next(c.id for c in clientes if c.nome == cn)
            
            col1, col2 = st.columns(2)
            cod = col1.text_input("* Código:", placeholder="REC001")
            nom = col2.text_input("* Nome:", placeholder="Pão Francês")
            
            if FICHAS_ANINHADAS_DISPONIVEL:
                col1, col2 = st.columns(2)
                rendimento_gramas = col1.number_input("Rendimento (g):", min_value=0.0, value=0.0, step=10.0)
                eh_intermediaria = col2.checkbox("📋 Pode ser ingrediente")
            
            st.markdown("---")
            st.subheader("🥖 Ingredientes")
            
            if FICHAS_ANINHADAS_DISPONIVEL:
                tipo_ingrediente = st.radio("Tipo:", ["🥄 Insumo", "📋 Ficha"], horizontal=True)
            else:
                tipo_ingrediente = "🥄 Insumo"
            
            if tipo_ingrediente == "🥄 Insumo":
                col1, col2, col3 = st.columns([3, 2, 1])
                insumos = db.query(Insumo).filter(Insumo.ativo == 1).all()
                if insumos:
                    insn = col1.selectbox("Insumo:", [f"{i.nome} (R$ {float(i.preco_unitario):.2f})" for i in insumos])
                    qtd = col2.number_input("Qtd (g):", min_value=0.0, value=100.0, step=10.0)
                    if col3.button("➕"):
                        iid = next(i.id for i in insumos if i.nome in insn)
                        ins = next(i for i in insumos if i.id == iid)
                        st.session_state.ing.append({
                            'tipo': 'insumo', 'id': ins.id, 'nome': ins.nome,
                            'qtd': qtd, 'preco': float(ins.preco_unitario),
                            'custo': qtd * float(ins.preco_unitario)
                        })
                        st.rerun()
            
            else:  # Ficha
                if FICHAS_ANINHADAS_DISPONIVEL:
                    fichas_inter = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1, FichaTecnica.eh_intermediaria == 1).all()
                    if fichas_inter:
                        col1, col2, col3 = st.columns([3, 2, 1])
                        ficha_sel = col1.selectbox("Ficha:", options=fichas_inter, format_func=lambda x: f"{x.nome} ({float(x.rendimento_gramas):.0f}g)")
                        qtd_ficha = col2.number_input("Qtd (g):", min_value=0.0, value=float(ficha_sel.rendimento_gramas or 100), step=10.0)
                        if col3.button("➕"):
                            rend_g = float(ficha_sel.rendimento_gramas or 1)
                            custo_g = float(ficha_sel.custo_total) / rend_g if rend_g > 0 else 0
                            st.session_state.ing.append({
                                'tipo': 'ficha', 'id': ficha_sel.id, 'nome': f"📋 {ficha_sel.nome}",
                                'qtd': qtd_ficha, 'preco': custo_g, 'custo': custo_g * qtd_ficha
                            })
                            st.rerun()
                    else:
                        st.warning("⚠️ Nenhuma ficha intermediária")
            
            if st.session_state.ing:
                st.markdown("### ✅ Adicionados:")
                total = 0
                for idx, ing in enumerate(st.session_state.ing):
                    col1, col2, col3, col4 = st.columns([3,1,1,1])
                    col1.write(f"**{ing['nome']}**")
                    col2.write(f"{ing['qtd']:.1f}g")
                    col3.write(f"R$ {ing['custo']:.2f}")
                    if col4.button("🗑️", key=f"del{idx}"):
                        st.session_state.ing.pop(idx)
                        st.rerun()
                    total += ing['custo']
                
                st.metric("**💰 TOTAL**", f"R$ {total:,.2f}")
                
                if st.button("💾 SALVAR FICHA", type="primary", use_container_width=True):
                    if cod and nom:
                        fic_data = {'cliente_id': cid, 'codigo': cod, 'nome': nom, 'custo_total': Decimal(str(total))}
                        if FICHAS_ANINHADAS_DISPONIVEL:
                            fic_data.update({'rendimento_gramas': Decimal(str(rendimento_gramas)), 'eh_intermediaria': 1 if eh_intermediaria else 0})
                        
                        fic = FichaTecnica(**fic_data)
                        db.add(fic)
                        db.flush()
                        
                        for idx, ing in enumerate(st.session_state.ing):
                            item_data = {
                                'ficha_tecnica_id': fic.id, 'tipo_item': ing.get('tipo', 'insumo'),
                                'quantidade': Decimal(str(ing['qtd'])), 'custo_item': Decimal(str(ing['custo'])),
                                'custo_unitario_historico': Decimal(str(ing['preco'])), 'ordem': idx
                            }
                            if ing.get('tipo') == 'ficha':
                                item_data['ficha_ingrediente_id'] = ing['id']
                            else:
                                item_data['insumo_id'] = ing['id']
                            db.add(ItemFichaTecnica(**item_data))
                        
                        db.commit()
                        st.success(f"✅ '{nom}' criada!")
                        st.session_state.ing = []
                        st.rerun()

# PRECIFICAÇÃO
elif menu == "💵 Precificação":
    st.markdown('<p class="main-title">💵 Precificação</p>', unsafe_allow_html=True)
    fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
    if not fichas:
        st.info("📭 Crie fichas primeiro!")
    else:
        fn = st.selectbox("Ficha:", [f"{f.codigo} - {f.nome}" for f in fichas])
        fid = next(f.id for f in fichas if f"{f.codigo} - {f.nome}" == fn)
        f = db.query(FichaTecnica).get(fid)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Composição")
            st.metric("Custo", f"R$ {float(f.custo_total):,.2f}")
            custos = db.query(CustoOperacional).filter(CustoOperacional.cliente_id == f.cliente_id, CustoOperacional.ativo == 1).all()
            top = sum(float(c.valor_mensal) for c in custos)
            st.metric("Operacionais/mês", f"R$ {top:,.2f}")
            ct = float(f.custo_total) + (top / 30)
            st.metric("**TOTAL**", f"R$ {ct:,.2f}")
        
        with col2:
            st.subheader("💰 Preço")
            mg = st.slider("Margem (%):", 0, 200, 30)
            pv = ct * (1 + mg/100)
            st.metric("**SUGERIDO**", f"R$ {pv:,.2f}")
            if st.button("💾 Salvar", type="primary", use_container_width=True):
                f.margem_percentual = Decimal(str(mg))
                f.preco_venda = Decimal(str(pv))
                db.commit()
                st.success("✅ Salvo!")
                st.rerun()

st.markdown("---")
versao = "v2.1 ✨" if FICHAS_ANINHADAS_DISPONIVEL else "v2.0"
st.markdown(f"<div style='text-align:center;color:#888;'><p>Ficha Técnica PRO {versao}</p></div>", unsafe_allow_html=True)
