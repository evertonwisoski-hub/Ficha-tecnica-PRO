"""
SISTEMA DE FICHA TÉCNICA PRO v2.2
✨ COM EDIÇÃO COMPLETA
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal
import sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, init_db
from models import Cliente, Insumo, CustoOperacional, FichaTecnica, ItemFichaTecnica
from exportacao_premium import gerar_excel_ficha, gerar_pdf_ficha
from gerenciador_logos import salvar_logo_cliente, carregar_logo_cliente

try:
    from calculos_custos import recalcular_todas_fichas, obter_hierarquia_ingredientes
    FICHAS_ANINHADAS_DISPONIVEL = True
except ImportError:
    FICHAS_ANINHADAS_DISPONIVEL = False

st.set_page_config(page_title="Ficha Técnica PRO", page_icon="📋", layout="wide")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
* {font-family: 'Poppins', sans-serif;}
.main {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
[data-testid="stSidebar"] {background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);}
[data-testid="stSidebar"] * {color: white !important;}
.main-title {font-size: 2.8rem; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem;}
.stButton>button {border-radius: 12px; font-weight: 600; padding: 0.7rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;
    border: none; box-shadow: 0 4px 15px rgba(102,126,234,0.4);}
</style>""", unsafe_allow_html=True)

init_db()

if FICHAS_ANINHADAS_DISPONIVEL and not os.path.exists('.migrado'):
    try:
        from migrar_fichas_aninhadas import migrar_banco
        with st.spinner("🔄 Atualizando..."):
            if migrar_banco():
                with open('.migrado', 'w') as f:
                    f.write('OK')
    except: pass

if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()
db = st.session_state.db

# SIDEBAR
st.sidebar.markdown("# 📋 Ficha Técnica PRO")
if FICHAS_ANINHADAS_DISPONIVEL:
    st.sidebar.markdown("✨ *Fichas Aninhadas* | **v2.2 Editável**")
st.sidebar.markdown("---")
menu = st.sidebar.radio("", ["🏠 Início", "👥 Clientes", "📦 Insumos", "💰 Custos", "📝 Fichas", "💵 Precificação"])
st.sidebar.markdown("---")
st.sidebar.metric("👥 Clientes", db.query(Cliente).filter(Cliente.ativo == 1).count())
st.sidebar.metric("📦 Insumos", db.query(Insumo).filter(Insumo.ativo == 1).count())
st.sidebar.metric("📝 Fichas", db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).count())

# INÍCIO
if menu == "🏠 Início":
    st.markdown('<p class="main-title">📋 Sistema de Ficha Técnica</p>', unsafe_allow_html=True)
    if FICHAS_ANINHADAS_DISPONIVEL:
        st.info("✨ **v2.2:** Agora com edição completa de clientes, insumos, custos e fichas!")
    col1, col2, col3 = st.columns(3)
    for col, icon, title in [(col1, "👥", "Clientes"), (col2, "📦", "Insumos"), (col3, "📝", "Fichas")]:
        col.markdown(f'<div style="text-align:center;font-size:3.5rem;">{icon}</div><h3 style="text-align:center;color:#667eea;">{title}</h3>', unsafe_allow_html=True)

# CLIENTES
elif menu == "👥 Clientes":
    st.markdown('<p class="main-title">👥 Clientes</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 Lista", "➕ Novo"])
    
    with tab1:
        clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
        if clientes:
            for c in clientes:
                with st.expander(f"👤 {c.nome}"):
                    col1, col2, col3 = st.columns([2,1,1])
                    with col1:
                        st.write(f"**Tel:** {c.telefone or '-'} | **Email:** {c.email or '-'}")
                    with col2:
                        if st.button("✏️ Editar", key=f"ec{c.id}"):
                            st.session_state[f'ed_c_{c.id}'] = True
                            st.rerun()
                    with col3:
                        fc = db.query(FichaTecnica).filter(FichaTecnica.cliente_id==c.id, FichaTecnica.ativo==1).count()
                        if fc > 0:
                            st.warning(f"⚠️ {fc} fichas")
                        elif st.button("🗑️ Del", key=f"dc{c.id}"):
                            c.ativo = 0
                            db.commit()
                            st.rerun()
                    
                    if st.session_state.get(f'ed_c_{c.id}'):
                        with st.form(f"fc{c.id}"):
                            nn = st.text_input("Nome:", value=c.nome)
                            nt = st.text_input("Tel:", value=c.telefone or "")
                            ne = st.text_input("Email:", value=c.email or "")
                            col1, col2 = st.columns(2)
                            if col1.form_submit_button("💾 Salvar"):
                                c.nome, c.telefone, c.email = nn, nt or None, ne or None
                                db.commit()
                                del st.session_state[f'ed_c_{c.id}']
                                st.success("✅ OK!")
                                st.rerun()
                            if col2.form_submit_button("❌ Cancelar"):
                                del st.session_state[f'ed_c_{c.id}']
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
            for i in insumos:
                with st.expander(f"📦 {i.nome} - R$ {float(i.preco_unitario):.2f}/{i.unidade_medida}"):
                    col1, col2, col3 = st.columns([2,1,1])
                    with col1:
                        st.write(f"**Preço:** R$ {float(i.preco_unitario):.2f} | **Fornecedor:** {i.fornecedor or '-'}")
                    with col2:
                        if st.button("✏️ Editar", key=f"ei{i.id}"):
                            st.session_state[f'ed_i_{i.id}'] = True
                            st.rerun()
                    with col3:
                        em_uso = db.query(ItemFichaTecnica).filter(ItemFichaTecnica.insumo_id==i.id, ItemFichaTecnica.tipo_item=='insumo').count()
                        if em_uso > 0:
                            st.warning(f"⚠️ {em_uso} fichas")
                            if st.button("🔒 Inativar", key=f"ii{i.id}"):
                                i.ativo = 0
                                db.commit()
                                st.rerun()
                        elif st.button("🗑️ Del", key=f"di{i.id}"):
                            db.delete(i)
                            db.commit()
                            st.rerun()
                    
                    if st.session_state.get(f'ed_i_{i.id}'):
                        with st.form(f"fi{i.id}"):
                            nn = st.text_input("Nome:", value=i.nome)
                            col1, col2 = st.columns(2)
                            idx = ["kg","g","L","ml","unidade"].index(i.unidade_medida) if i.unidade_medida in ["kg","g","L","ml","unidade"] else 0
                            nu = col1.selectbox("Un:", ["kg","g","L","ml","unidade"], index=idx)
                            np = col2.number_input("Preço:", min_value=0.0, value=float(i.preco_unitario), format="%.2f")
                            col1, col2 = st.columns(2)
                            if col1.form_submit_button("💾 Salvar"):
                                i.nome, i.unidade_medida, i.preco_unitario = nn, nu, Decimal(str(np))
                                db.commit()
                                if FICHAS_ANINHADAS_DISPONIVEL:
                                    recalcular_todas_fichas(db)
                                del st.session_state[f'ed_i_{i.id}']
                                st.success("✅ Recalculado!")
                                st.rerun()
                            if col2.form_submit_button("❌ Cancelar"):
                                del st.session_state[f'ed_i_{i.id}']
                                st.rerun()
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
            custos = db.query(CustoOperacional).filter(CustoOperacional.cliente_id==cid, CustoOperacional.ativo==1).all()
            if custos:
                for cu in custos:
                    with st.expander(f"{cu.tipo.upper()}: {cu.descricao} - R$ {float(cu.valor_mensal):.2f}"):
                        col1, col2, col3 = st.columns([2,1,1])
                        with col2:
                            if st.button("✏️ Editar", key=f"ecu{cu.id}"):
                                st.session_state[f'ed_cu_{cu.id}'] = True
                                st.rerun()
                        with col3:
                            if st.button("🗑️ Del", key=f"dcu{cu.id}"):
                                cu.ativo = 0
                                db.commit()
                                st.rerun()
                        
                        if st.session_state.get(f'ed_cu_{cu.id}'):
                            with st.form(f"fcu{cu.id}"):
                                nt = st.radio("Tipo:", ["Fixo", "Variável"], index=0 if cu.tipo=='fixo' else 1)
                                nd = st.text_input("Desc:", value=cu.descricao)
                                nv = st.number_input("Valor:", min_value=0.0, value=float(cu.valor_mensal), format="%.2f")
                                col1, col2 = st.columns(2)
                                if col1.form_submit_button("💾 Salvar"):
                                    cu.tipo = 'fixo' if nt=="Fixo" else 'variavel'
                                    cu.descricao, cu.valor_mensal = nd, Decimal(str(nv))
                                    db.commit()
                                    del st.session_state[f'ed_cu_{cu.id}']
                                    st.rerun()
                                if col2.form_submit_button("❌ Cancelar"):
                                    del st.session_state[f'ed_cu_{cu.id}']
                                    st.rerun()
                
                st.metric("💰 Total", f"R$ {sum(float(c.valor_mensal) for c in custos):,.2f}")
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

# FICHAS
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
                        if FICHAS_ANINHADAS_DISPONIVEL and f.rendimento_gramas:
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
                        col1, col2, col3 = st.columns(3)
                        if col1.button("📊 Excel", key=f"xe{f.id}"):
                            excel = gerar_excel_ficha(f)
                            st.download_button("💾 Baixar", excel, f"ficha_{f.codigo}.xlsx", 
                                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"de{f.id}")
                        if col2.button("📄 PDF", key=f"xp{f.id}"):
                            pdf = gerar_pdf_ficha(f)
                            st.download_button("💾 Baixar", pdf, f"ficha_{f.codigo}.pdf", "application/pdf", key=f"dp{f.id}")
                        
                        with col3:
                            if FICHAS_ANINHADAS_DISPONIVEL:
                                usada = db.query(ItemFichaTecnica).filter(ItemFichaTecnica.ficha_ingrediente_id==f.id, ItemFichaTecnica.tipo_item=='ficha').count()
                                if usada > 0:
                                    st.warning(f"⚠️ Em {usada}")
                                elif st.button("🗑️ Del", key=f"df{f.id}"):
                                    f.ativo = 0
                                    db.commit()
                                    st.rerun()
                            else:
                                if st.button("🗑️ Del", key=f"df{f.id}"):
                                    f.ativo = 0
                                    db.commit()
                                    st.rerun()
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
            
            else:
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
versao = "v2.2 ✨ Editável" if FICHAS_ANINHADAS_DISPONIVEL else "v2.2"
st.markdown(f"<div style='text-align:center;color:#888;'><p>Ficha Técnica PRO {versao}</p></div>", unsafe_allow_html=True)
