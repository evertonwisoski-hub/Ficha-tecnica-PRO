"""
SISTEMA DE FICHA TECNICA PRO v2.3
COM EDICAO COMPLETA E MODO ADMIN
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

st.set_page_config(page_title="Ficha Tecnica PRO", page_icon="📋", layout="wide")

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
        with st.spinner("Atualizando..."):
            if migrar_banco():
                with open('.migrado', 'w') as f:
                    f.write('OK')
    except: pass

if 'db' not in st.session_state:
    st.session_state.db = SessionLocal()
db = st.session_state.db

st.sidebar.markdown("# Ficha Tecnica PRO v2.3")
st.sidebar.markdown("---")
menu = st.sidebar.radio("", ["Inicio", "Clientes", "Insumos", "Custos", "Fichas", "Precificacao"])
st.sidebar.markdown("---")
st.sidebar.metric("Clientes", db.query(Cliente).filter(Cliente.ativo == 1).count())
st.sidebar.metric("Insumos", db.query(Insumo).filter(Insumo.ativo == 1).count())
st.sidebar.metric("Fichas", db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).count())
st.sidebar.markdown("---")
if st.sidebar.checkbox("MODO ADMIN"):
    st.session_state.admin_mode = True
else:
    st.session_state.admin_mode = False

if menu == "Inicio":
    st.markdown('<p class="main-title">Sistema de Ficha Tecnica</p>', unsafe_allow_html=True)
    st.info("v2.3: Edicao completa + Modo Admin")
    col1, col2, col3 = st.columns(3)
    for col, t in [(col1, "Clientes"), (col2, "Insumos"), (col3, "Fichas")]:
        col.markdown(f'<h3 style="text-align:center;color:#667eea;">{t}</h3>', unsafe_allow_html=True)

elif menu == "Clientes":
    st.markdown('<p class="main-title">Clientes</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Lista", "Novo"])
    with tab1:
        clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
        if clientes:
            for c in clientes:
                with st.expander(f"{c.nome}"):
                    col1, col2, col3 = st.columns([2,1,1])
                    with col1:
                        st.write(f"Tel: {c.telefone or '-'} | Email: {c.email or '-'}")
                    with col2:
                        if st.button("Editar", key=f"ec{c.id}"):
                            st.session_state[f'ed_c_{c.id}'] = True
                            st.rerun()
                    with col3:
                        fc = db.query(FichaTecnica).filter(FichaTecnica.cliente_id==c.id, FichaTecnica.ativo==1).count()
                        if fc > 0:
                            st.warning(f"{fc} fichas")
                            if st.session_state.get('admin_mode'):
                                if st.button("FORCAR", key=f"fc{c.id}"):
                                    for f in db.query(FichaTecnica).filter(FichaTecnica.cliente_id==c.id).all():
                                        for i in db.query(ItemFichaTecnica).filter(ItemFichaTecnica.ficha_tecnica_id==f.id).all():
                                            db.delete(i)
                                        db.delete(f)
                                    db.delete(c)
                                    db.commit()
                                    st.rerun()
                        elif st.button("Del", key=f"dc{c.id}"):
                            c.ativo = 0
                            db.commit()
                            st.rerun()
                    if st.session_state.get(f'ed_c_{c.id}'):
                        with st.form(f"fec{c.id}"):
                            nn = st.text_input("Nome:", value=c.nome)
                            nt = st.text_input("Tel:", value=c.telefone or "")
                            ne = st.text_input("Email:", value=c.email or "")
                            col1, col2 = st.columns(2)
                            if col1.form_submit_button("Salvar"):
                                c.nome, c.telefone, c.email = nn, nt or None, ne or None
                                db.commit()
                                del st.session_state[f'ed_c_{c.id}']
                                st.rerun()
                            if col2.form_submit_button("Cancelar"):
                                del st.session_state[f'ed_c_{c.id}']
                                st.rerun()
        else:
            st.info("Nenhum cliente")
    with tab2:
        with st.form("fc", clear_on_submit=True):
            nome = st.text_input("Nome:")
            col1, col2 = st.columns(2)
            tel = col1.text_input("Telefone:")
            email = col2.text_input("Email:")
            if st.form_submit_button("Salvar", type="primary"):
                if nome:
                    db.add(Cliente(nome=nome, telefone=tel, email=email))
                    db.commit()
                    st.success("OK!")
                    st.rerun()

elif menu == "Insumos":
    st.markdown('<p class="main-title">Insumos</p>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Lista", "Novo"])
    with tab1:
        insumos = db.query(Insumo).filter(Insumo.ativo == 1).all()
        if insumos:
            for i in insumos:
                with st.expander(f"{i.nome} - R$ {float(i.preco_unitario):.2f}"):
                    col1, col2, col3 = st.columns([2,1,1])
                    with col1:
                        st.write(f"Preco: R$ {float(i.preco_unitario):.2f}")
                    with col2:
                        if st.button("Editar", key=f"ei{i.id}"):
                            st.session_state[f'ed_i_{i.id}'] = True
                            st.rerun()
                    with col3:
                        uso = db.query(ItemFichaTecnica).filter(ItemFichaTecnica.insumo_id==i.id).count()
                        if uso > 0:
                            st.warning(f"{uso} fichas")
                            if st.button("Inativar", key=f"ii{i.id}"):
                                i.ativo = 0
                                db.commit()
                                st.rerun()
                        elif st.button("Del", key=f"di{i.id}"):
                            db.delete(i)
                            db.commit()
                            st.rerun()
                    if st.session_state.get(f'ed_i_{i.id}'):
                        with st.form(f"fei{i.id}"):
                            nn = st.text_input("Nome:", value=i.nome)
                            col1, col2 = st.columns(2)
                            idx = ["kg","g","L","ml","unidade"].index(i.unidade_medida) if i.unidade_medida in ["kg","g","L","ml","unidade"] else 0
                            nu = col1.selectbox("Un:", ["kg","g","L","ml","unidade"], index=idx)
                            np = col2.number_input("Preco:", min_value=0.0, value=float(i.preco_unitario), format="%.2f")
                            col1, col2 = st.columns(2)
                            if col1.form_submit_button("Salvar"):
                                i.nome, i.unidade_medida, i.preco_unitario = nn, nu, Decimal(str(np))
                                db.commit()
                                if FICHAS_ANINHADAS_DISPONIVEL:
                                    recalcular_todas_fichas(db)
                                del st.session_state[f'ed_i_{i.id}']
                                st.rerun()
                            if col2.form_submit_button("Cancelar"):
                                del st.session_state[f'ed_i_{i.id}']
                                st.rerun()
        else:
            st.info("Nenhum insumo")
    with tab2:
        with st.form("fi", clear_on_submit=True):
            nome = st.text_input("Nome:")
            col1, col2 = st.columns(2)
            unidade = col1.selectbox("Unidade:", ["kg", "g", "L", "ml", "unidade"])
            preco = col2.number_input("Preco:", min_value=0.0, format="%.2f")
            if st.form_submit_button("Salvar", type="primary"):
                if nome and preco > 0:
                    db.add(Insumo(nome=nome, unidade_medida=unidade, preco_unitario=Decimal(str(preco))))
                    db.commit()
                    st.success("OK!")
                    st.rerun()

elif menu == "Custos":
    st.markdown('<p class="main-title">Custos</p>', unsafe_allow_html=True)
    clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
    if not clientes:
        st.warning("Cadastre clientes primeiro!")
    else:
        cn = st.selectbox("Cliente:", [c.nome for c in clientes])
        cid = next(c.id for c in clientes if c.nome == cn)
        tab1, tab2 = st.tabs(["Lista", "Novo"])
        with tab1:
            custos = db.query(CustoOperacional).filter(CustoOperacional.cliente_id==cid, CustoOperacional.ativo==1).all()
            if custos:
                for cu in custos:
                    with st.expander(f"{cu.tipo}: {cu.descricao}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Editar", key=f"ec{cu.id}"):
                                st.session_state[f'ed_cu_{cu.id}'] = True
                                st.rerun()
                        with col2:
                            if st.button("Del", key=f"dc{cu.id}"):
                                cu.ativo = 0
                                db.commit()
                                st.rerun()
                        if st.session_state.get(f'ed_cu_{cu.id}'):
                            with st.form(f"fecu{cu.id}"):
                                nt = st.radio("Tipo:", ["Fixo", "Variavel"], index=0 if cu.tipo=='fixo' else 1)
                                nd = st.text_input("Desc:", value=cu.descricao)
                                nv = st.number_input("Valor:", min_value=0.0, value=float(cu.valor_mensal), format="%.2f")
                                col1, col2 = st.columns(2)
                                if col1.form_submit_button("Salvar"):
                                    cu.tipo, cu.descricao, cu.valor_mensal = 'fixo' if nt=="Fixo" else 'variavel', nd, Decimal(str(nv))
                                    db.commit()
                                    del st.session_state[f'ed_cu_{cu.id}']
                                    st.rerun()
                                if col2.form_submit_button("Cancelar"):
                                    del st.session_state[f'ed_cu_{cu.id}']
                                    st.rerun()
                st.metric("Total", f"R$ {sum(float(c.valor_mensal) for c in custos):,.2f}")
            else:
                st.info("Nenhum custo")
        with tab2:
            with st.form("fco"):
                tipo = st.radio("Tipo:", ["Fixo", "Variavel"])
                desc = st.text_input("Descricao:")
                val = st.number_input("Valor:", min_value=0.0, format="%.2f")
                if st.form_submit_button("Salvar", type="primary"):
                    if desc and val > 0:
                        db.add(CustoOperacional(cliente_id=cid, tipo='fixo' if tipo=="Fixo" else 'variavel', descricao=desc, valor_mensal=Decimal(str(val))))
                        db.commit()
                        st.rerun()

elif menu == "Fichas":
    st.markdown('<p class="main-title">Fichas</p>', unsafe_allow_html=True)
    if db.query(Cliente).count() == 0 or db.query(Insumo).count() == 0:
        st.warning("Cadastre clientes e insumos primeiro!")
    else:
        tab1, tab2 = st.tabs(["Lista", "Nova"])
        with tab1:
            fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
            if fichas:
                if FICHAS_ANINHADAS_DISPONIVEL:
                    if st.button("Recalcular Custos"):
                        recalcular_todas_fichas(db)
                        st.rerun()
                for f in fichas:
                    with st.expander(f"{f.codigo} - {f.nome}"):
                        cols = st.columns(3)
                        cols[0].metric("Custo", f"R$ {float(f.custo_total):.2f}")
                        cols[1].metric("Venda", f"R$ {float(f.preco_venda):.2f}")
                        st.markdown("**Ingredientes:**")
                        if FICHAS_ANINHADAS_DISPONIVEL:
                            try:
                                hier = obter_hierarquia_ingredientes(db, f.id)
                                for item in hier:
                                    st.write(f"{'  '*item['nivel']}• {item['nome']} ({item['quantidade']:.1f}g) R$ {item['custo']:.2f}")
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
                        if col1.button("Excel", key=f"xe{f.id}"):
                            excel = gerar_excel_ficha(f)
                            st.download_button("Baixar", excel, f"ficha_{f.codigo}.xlsx", key=f"de{f.id}")
                        if col2.button("PDF", key=f"xp{f.id}"):
                            pdf = gerar_pdf_ficha(f)
                            st.download_button("Baixar", pdf, f"ficha_{f.codigo}.pdf", key=f"dp{f.id}")
                        with col3:
                            if FICHAS_ANINHADAS_DISPONIVEL:
                                usada = db.query(ItemFichaTecnica).filter(ItemFichaTecnica.ficha_ingrediente_id==f.id).count()
                                if usada > 0:
                                    st.warning(f"Em {usada}")
                                    if st.session_state.get('admin_mode'):
                                        if st.button("FORCAR", key=f"ff{f.id}"):
                                            for i in db.query(ItemFichaTecnica).filter(ItemFichaTecnica.ficha_ingrediente_id==f.id).all():
                                                db.delete(i)
                                            for i in db.query(ItemFichaTecnica).filter(ItemFichaTecnica.ficha_tecnica_id==f.id).all():
                                                db.delete(i)
                                            db.delete(f)
                                            db.commit()
                                            st.rerun()
                                elif st.button("Del", key=f"df{f.id}"):
                                    f.ativo = 0
                                    db.commit()
                                    st.rerun()
                            else:
                                if st.button("Del", key=f"df{f.id}"):
                                    f.ativo = 0
                                    db.commit()
                                    st.rerun()
            else:
                st.info("Nenhuma ficha")
        with tab2:
            if 'ing' not in st.session_state:
                st.session_state.ing = []
            clientes = db.query(Cliente).filter(Cliente.ativo == 1).all()
            cn = st.selectbox("Cliente:", [c.nome for c in clientes])
            cid = next(c.id for c in clientes if c.nome == cn)
            col1, col2 = st.columns(2)
            cod = col1.text_input("Codigo:")
            nom = col2.text_input("Nome:")
            if FICHAS_ANINHADAS_DISPONIVEL:
                col1, col2 = st.columns(2)
                rend = col1.number_input("Rendimento (g):", min_value=0.0, step=10.0)
                inter = col2.checkbox("Pode ser ingrediente")
            st.subheader("Ingredientes")
            tipo = st.radio("Tipo:", ["Insumo", "Ficha"], horizontal=True) if FICHAS_ANINHADAS_DISPONIVEL else "Insumo"
            if tipo == "Insumo":
                col1, col2, col3 = st.columns([3,2,1])
                insumos = db.query(Insumo).filter(Insumo.ativo == 1).all()
                if insumos:
                    insn = col1.selectbox("Insumo:", [f"{i.nome}" for i in insumos])
                    qtd = col2.number_input("Qtd (g):", min_value=0.0, value=100.0, step=10.0)
                    if col3.button("ADD"):
                        ins = next(i for i in insumos if i.nome == insn)
                        st.session_state.ing.append({'tipo':'insumo','id':ins.id,'nome':ins.nome,'qtd':qtd,'preco':float(ins.preco_unitario),'custo':qtd*float(ins.preco_unitario)})
                        st.rerun()
            else:
                fichas_inter = db.query(FichaTecnica).filter(FichaTecnica.ativo==1, FichaTecnica.eh_intermediaria==1).all()
                if fichas_inter:
                    col1, col2, col3 = st.columns([3,2,1])
                    fs = col1.selectbox("Ficha:", options=fichas_inter, format_func=lambda x: f"{x.nome}")
                    qtd = col2.number_input("Qtd (g):", min_value=0.0, value=100.0, step=10.0)
                    if col3.button("ADD"):
                        rg = float(fs.rendimento_gramas or 1)
                        cg = float(fs.custo_total)/rg if rg>0 else 0
                        st.session_state.ing.append({'tipo':'ficha','id':fs.id,'nome':fs.nome,'qtd':qtd,'preco':cg,'custo':cg*qtd})
                        st.rerun()
            if st.session_state.ing:
                total = 0
                for idx, ing in enumerate(st.session_state.ing):
                    col1, col2, col3 = st.columns([3,1,1])
                    col1.write(ing['nome'])
                    col2.write(f"{ing['qtd']:.1f}g - R$ {ing['custo']:.2f}")
                    if col3.button("X", key=f"del{idx}"):
                        st.session_state.ing.pop(idx)
                        st.rerun()
                    total += ing['custo']
                st.metric("TOTAL", f"R$ {total:.2f}")
                if st.button("SALVAR FICHA", type="primary"):
                    if cod and nom:
                        fd = {'cliente_id':cid,'codigo':cod,'nome':nom,'custo_total':Decimal(str(total))}
                        if FICHAS_ANINHADAS_DISPONIVEL:
                            fd.update({'rendimento_gramas':Decimal(str(rend)),'eh_intermediaria':1 if inter else 0})
                        fic = FichaTecnica(**fd)
                        db.add(fic)
                        db.flush()
                        for idx, ing in enumerate(st.session_state.ing):
                            itd = {'ficha_tecnica_id':fic.id,'tipo_item':ing.get('tipo','insumo'),'quantidade':Decimal(str(ing['qtd'])),'custo_item':Decimal(str(ing['custo'])),'custo_unitario_historico':Decimal(str(ing['preco'])),'ordem':idx}
                            if ing.get('tipo')=='ficha':
                                itd['ficha_ingrediente_id'] = ing['id']
                            else:
                                itd['insumo_id'] = ing['id']
                            db.add(ItemFichaTecnica(**itd))
                        db.commit()
                        st.session_state.ing = []
                        st.rerun()

elif menu == "Precificacao":
    st.markdown('<p class="main-title">Precificacao</p>', unsafe_allow_html=True)
    fichas = db.query(FichaTecnica).filter(FichaTecnica.ativo == 1).all()
    if not fichas:
        st.info("Crie fichas primeiro!")
    else:
        fn = st.selectbox("Ficha:", [f"{f.codigo} - {f.nome}" for f in fichas])
        fid = next(f.id for f in fichas if f"{f.codigo} - {f.nome}" == fn)
        f = db.query(FichaTecnica).get(fid)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Composicao")
            st.metric("Custo", f"R$ {float(f.custo_total):.2f}")
        with col2:
            st.subheader("Preco")
            mg = st.slider("Margem (%):", 0, 200, 30)
            pv = float(f.custo_total) * (1 + mg/100)
            st.metric("SUGERIDO", f"R$ {pv:.2f}")
            if st.button("Salvar", type="primary"):
                f.margem_percentual = Decimal(str(mg))
                f.preco_venda = Decimal(str(pv))
                db.commit()
                st.rerun()

st.markdown("---")
st.markdown("<div style='text-align:center;color:#888;'>Ficha Tecnica PRO v2.3</div>", unsafe_allow_html=True)
