"""
PATCH: Adicionar ao app.py - Seção de Fichas Aninhadas
Insira este código na seção de criação de fichas técnicas
"""

# ===== ADICIONAR NA SEÇÃO DE CRIAÇÃO DE FICHA TÉCNICA =====
# Substituir a parte de adicionar ingredientes por este código:

st.subheader("📦 Ingredientes")

# NOVO: Seletor de tipo de ingrediente
tipo_ingrediente = st.radio(
    "Tipo de ingrediente:",
    ["🥄 Insumo básico", "📋 Ficha técnica (preparação intermediária)"],
    horizontal=True,
    key="tipo_ing"
)

if tipo_ingrediente == "🥄 Insumo básico":
    # Lógica original de insumos
    insumos_disponiveis = db.query(Insumo).filter(Insumo.ativo == 1).all()
    
    if insumos_disponiveis:
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            insumo_selecionado = st.selectbox(
                "Selecione o insumo:",
                options=insumos_disponiveis,
                format_func=lambda x: f"{x.nome} ({x.unidade_medida})",
                key="sel_insumo"
            )
        
        with col2:
            quantidade = st.number_input(
                f"Quantidade (g):",
                min_value=0.001,
                value=100.0,
                step=10.0,
                format="%.3f",
                key="qtd_insumo"
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Adicionar", key="add_insumo"):
                # Calcular custo
                custo_item = float(insumo_selecionado.preco_unitario) * float(quantidade)
                
                novo_item = ItemFichaTecnica(
                    ficha_tecnica_id=ficha_temp.id,
                    tipo_item='insumo',
                    insumo_id=insumo_selecionado.id,
                    quantidade=quantidade,
                    custo_item=custo_item,
                    custo_unitario_historico=insumo_selecionado.preco_unitario,
                    ordem=len(ficha_temp.itens)
                )
                db.add(novo_item)
                db.commit()
                st.success(f"✅ {insumo_selecionado.nome} adicionado!")
                st.rerun()
    else:
        st.warning("⚠️ Cadastre insumos primeiro!")

else:  # Ficha técnica
    # NOVO: Seletor de fichas intermediárias
    from calculos_custos import validar_dependencia_circular
    
    fichas_intermediarias = db.query(FichaTecnica).filter(
        FichaTecnica.ativo == 1,
        FichaTecnica.eh_intermediaria == 1
    ).all()
    
    if fichas_intermediarias:
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            ficha_selecionada = st.selectbox(
                "Selecione a ficha técnica:",
                options=fichas_intermediarias,
                format_func=lambda x: f"📋 {x.nome} ({x.rendimento_gramas}g)",
                key="sel_ficha"
            )
        
        with col2:
            quantidade_ficha = st.number_input(
                "Quantidade (g):",
                min_value=0.001,
                value=float(ficha_selecionada.rendimento_gramas) if ficha_selecionada.rendimento_gramas else 100.0,
                step=10.0,
                format="%.3f",
                key="qtd_ficha"
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Adicionar", key="add_ficha"):
                # Validar dependência circular
                valido, mensagem = validar_dependencia_circular(
                    db, 
                    ficha_temp.id, 
                    ficha_selecionada.id
                )
                
                if not valido:
                    st.error(mensagem)
                else:
                    # Calcular custo
                    rendimento_g = float(ficha_selecionada.rendimento_gramas) if ficha_selecionada.rendimento_gramas else 1.0
                    custo_por_grama = float(ficha_selecionada.custo_total) / rendimento_g if rendimento_g > 0 else 0
                    custo_item = custo_por_grama * float(quantidade_ficha)
                    
                    novo_item = ItemFichaTecnica(
                        ficha_tecnica_id=ficha_temp.id,
                        tipo_item='ficha',
                        ficha_ingrediente_id=ficha_selecionada.id,
                        quantidade=quantidade_ficha,
                        custo_item=custo_item,
                        custo_unitario_historico=custo_por_grama,
                        ordem=len(ficha_temp.itens)
                    )
                    db.add(novo_item)
                    db.commit()
                    st.success(f"✅ {ficha_selecionada.nome} adicionado!")
                    st.rerun()
        
        # Informação sobre a ficha selecionada
        if ficha_selecionada:
            st.info(f"ℹ️ **{ficha_selecionada.nome}**: Rendimento {ficha_selecionada.rendimento_gramas}g | Custo R$ {ficha_selecionada.custo_total:.2f}")
    
    else:
        st.warning("⚠️ Nenhuma ficha marcada como intermediária. Marque fichas como 'Pode ser usada como ingrediente' para aparecerem aqui.")

# ===== ADICIONAR AO FORMULÁRIO DE CRIAÇÃO =====
# Após o campo "rendimento", adicionar:

rendimento_gramas = st.number_input(
    "Rendimento em gramas:",
    min_value=0.0,
    value=0.0,
    step=10.0,
    help="Peso total da receita pronta (necessário para usar como ingrediente)"
)

eh_intermediaria = st.checkbox(
    "📋 Esta ficha pode ser usada como ingrediente em outras fichas",
    help="Marque se esta preparação será usada em outras receitas (ex: cremes, massas, recheios)"
)

# ===== MODIFICAR EXIBIÇÃO DE INGREDIENTES =====
# Substituir a tabela de ingredientes por:

if itens_ficha:
    st.markdown("### 📦 Ingredientes")
    
    from calculos_custos import obter_hierarquia_ingredientes
    
    # Obter hierarquia completa
    hierarquia = obter_hierarquia_ingredientes(db, ficha.id)
    
    for item_hierarquia in hierarquia:
        nivel = item_hierarquia['nivel']
        indent = "　" * nivel  # Espaço japonês para indentação
        prefixo = "└─ " if nivel > 0 else ""
        
        if item_hierarquia['eh_aninhado']:
            st.markdown(f"{indent}{prefixo}**{item_hierarquia['nome']}** - {item_hierarquia['quantidade']:.1f}{item_hierarquia['unidade']} - R$ {item_hierarquia['custo']:.2f}")
        else:
            st.markdown(f"{indent}{prefixo}{item_hierarquia['nome']} - {item_hierarquia['quantidade']:.1f}{item_hierarquia['unidade']} - R$ {item_hierarquia['custo']:.2f}")
    
    st.markdown(f"**CUSTO TOTAL:** R$ {ficha.custo_total:.2f}")
