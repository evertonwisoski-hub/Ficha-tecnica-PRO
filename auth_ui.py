"""
Interface de Autenticação para Streamlit
Integração com Sistema Ficha Técnica PRO
"""

import streamlit as st
from auth import AuthSystem, login_user, logout, get_current_user, is_admin, check_authentication


def verificar_autenticacao():
    """
    Verifica se usuário está autenticado.
    Se não estiver, mostra tela de login.
    Retorna True se autenticado, False caso contrário.
    """
    # Inicializa session_state se necessário
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    # Se não está autenticado, mostra tela de login
    if not st.session_state.authenticated:
        mostrar_tela_login()
        return False
    
    return True


def mostrar_tela_login():
    """Exibe tela de login ou setup inicial"""
    auth = AuthSystem()
    
    # CSS customizado para tela de login
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .login-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Se não tem usuários, mostra setup inicial
    if not auth.has_users():
        mostrar_setup_inicial(auth)
        return
    
    # Tela de login normal
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🔐 Ficha Técnica PRO</h1>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
        password = st.text_input("🔑 Senha", type="password", placeholder="Digite sua senha")
        submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("⚠️ Preencha usuário e senha!")
            else:
                success, user, message = auth.authenticate(username, password)
                
                if success:
                    login_user(user)
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    st.caption("💡 **Primeiro acesso?** Entre em contato com o administrador.")
    st.markdown('</div>', unsafe_allow_html=True)


def mostrar_setup_inicial(auth):
    """Tela de configuração inicial - primeiro admin"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-title">🎉 Bem-vindo!</h1>', unsafe_allow_html=True)
    st.info("📋 Nenhum usuário cadastrado. Vamos criar o primeiro usuário **ADMINISTRADOR**.")
    
    with st.form("setup_form"):
        st.markdown("#### Dados do Administrador")
        
        username = st.text_input(
            "👤 Usuário",
            placeholder="Ex: admin, everton, etc.",
            help="Nome de usuário para login"
        )
        
        email = st.text_input(
            "📧 Email",
            placeholder="seu@email.com",
            help="Email para contato"
        )
        
        password = st.text_input(
            "🔑 Senha",
            type="password",
            placeholder="Mínimo 6 caracteres",
            help="Escolha uma senha forte"
        )
        
        password_confirm = st.text_input(
            "🔑 Confirmar Senha",
            type="password",
            placeholder="Digite a senha novamente"
        )
        
        submit = st.form_submit_button("🚀 Criar Administrador", use_container_width=True)
        
        if submit:
            # Validações
            if not username or not email or not password:
                st.error("⚠️ Preencha todos os campos!")
            elif len(password) < 6:
                st.error("⚠️ Senha deve ter no mínimo 6 caracteres!")
            elif password != password_confirm:
                st.error("⚠️ Senhas não conferem!")
            else:
                # Cria primeiro admin
                success, message = auth.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='admin'
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.success("🎉 Sistema configurado! Faça login para continuar.")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def mostrar_info_usuario_sidebar():
    """Mostra informações do usuário logado na sidebar"""
    if not check_authentication():
        return
    
    user = get_current_user()
    if not user:
        return
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### 👤 {user['username']}")
    st.sidebar.markdown(f"**Tipo:** {'🔑 Admin' if user['role'] == 'admin' else '👤 Usuário'}")
    st.sidebar.markdown(f"**Email:** {user['email']}")
    
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        logout()


def mostrar_painel_usuarios():
    """Painel de gerenciamento de usuários (só admin)"""
    if not is_admin():
        st.error("⛔ Acesso negado! Apenas administradores podem acessar esta área.")
        return
    
    auth = AuthSystem()
    current_user = get_current_user()
    
    st.title("👥 Gerenciamento de Usuários")
    
    # Tabs
    tab1, tab2 = st.tabs(["📋 Usuários Cadastrados", "➕ Novo Usuário"])
    
    # TAB 1: Lista de usuários
    with tab1:
        users = auth.get_all_users()
        
        if not users:
            st.info("📭 Nenhum usuário cadastrado.")
        else:
            st.markdown(f"**Total:** {len(users)} usuários")
            
            for user in users:
                with st.expander(
                    f"{'🔑' if user.role == 'admin' else '👤'} {user.username} "
                    f"{'✅' if user.is_active else '❌'}",
                    expanded=False
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {user.id}")
                        st.write(f"**Usuário:** {user.username}")
                        st.write(f"**Email:** {user.email}")
                    
                    with col2:
                        st.write(f"**Tipo:** {'🔑 Administrador' if user.role == 'admin' else '👤 Usuário'}")
                        st.write(f"**Status:** {'✅ Ativo' if user.is_active else '❌ Inativo'}")
                        st.write(f"**Criado:** {user.created_at.strftime('%d/%m/%Y')}")
                    
                    if user.last_login:
                        st.write(f"**Último login:** {user.last_login.strftime('%d/%m/%Y %H:%M')}")
                    
                    # Ações
                    st.markdown("---")
                    col_a, col_b = st.columns(2)
                    
                    # Não pode desativar a si mesmo
                    if user.id != current_user['id']:
                        with col_a:
                            if user.is_active:
                                if st.button(f"❌ Desativar", key=f"deactivate_{user.id}"):
                                    success, msg = auth.deactivate_user(user.id)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                            else:
                                if st.button(f"✅ Ativar", key=f"activate_{user.id}"):
                                    success, msg = auth.activate_user(user.id)
                                    if success:
                                        st.success(msg)
                                        st.rerun()
                                    else:
                                        st.error(msg)
                        
                        with col_b:
                            if st.button(f"🔑 Resetar Senha", key=f"reset_{user.id}"):
                                st.session_state[f'reset_password_{user.id}'] = True
                        
                        # Form de reset de senha
                        if st.session_state.get(f'reset_password_{user.id}', False):
                            with st.form(f"reset_form_{user.id}"):
                                new_password = st.text_input("Nova senha", type="password", key=f"new_pass_{user.id}")
                                confirm_password = st.text_input("Confirmar senha", type="password", key=f"confirm_pass_{user.id}")
                                
                                col_submit, col_cancel = st.columns(2)
                                with col_submit:
                                    submit_reset = st.form_submit_button("✅ Confirmar")
                                with col_cancel:
                                    cancel_reset = st.form_submit_button("❌ Cancelar")
                                
                                if submit_reset:
                                    if new_password and new_password == confirm_password and len(new_password) >= 6:
                                        success, msg = auth.update_user(user.id, password=new_password)
                                        if success:
                                            st.success("✅ Senha atualizada!")
                                            st.session_state[f'reset_password_{user.id}'] = False
                                            st.rerun()
                                        else:
                                            st.error(msg)
                                    else:
                                        st.error("⚠️ Senhas não conferem ou são muito curtas!")
                                
                                if cancel_reset:
                                    st.session_state[f'reset_password_{user.id}'] = False
                                    st.rerun()
                    else:
                        st.info("ℹ️ Você não pode desativar sua própria conta.")
    
    # TAB 2: Criar novo usuário
    with tab2:
        with st.form("create_user_form"):
            st.markdown("### Criar Novo Usuário")
            
            new_username = st.text_input("👤 Usuário", placeholder="Nome de usuário")
            new_email = st.text_input("📧 Email", placeholder="email@exemplo.com")
            new_password = st.text_input("🔑 Senha", type="password", placeholder="Mínimo 6 caracteres")
            new_password_confirm = st.text_input("🔑 Confirmar Senha", type="password")
            new_role = st.selectbox("🎭 Tipo de Usuário", ['user', 'admin'], 
                                   format_func=lambda x: '🔑 Administrador' if x == 'admin' else '👤 Usuário')
            
            submit_new = st.form_submit_button("➕ Criar Usuário", use_container_width=True)
            
            if submit_new:
                if not new_username or not new_email or not new_password:
                    st.error("⚠️ Preencha todos os campos!")
                elif len(new_password) < 6:
                    st.error("⚠️ Senha deve ter no mínimo 6 caracteres!")
                elif new_password != new_password_confirm:
                    st.error("⚠️ Senhas não conferem!")
                else:
                    success, message = auth.create_user(
                        username=new_username,
                        email=new_email,
                        password=new_password,
                        role=new_role
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")


def mostrar_alterar_senha():
    """Permite usuário alterar sua própria senha"""
    if not check_authentication():
        return
    
    auth = AuthSystem()
    user = get_current_user()
    
    st.title("🔑 Alterar Senha")
    
    with st.form("change_password_form"):
        current_password = st.text_input("🔒 Senha Atual", type="password")
        new_password = st.text_input("🔑 Nova Senha", type="password", placeholder="Mínimo 6 caracteres")
        confirm_password = st.text_input("🔑 Confirmar Nova Senha", type="password")
        
        submit = st.form_submit_button("✅ Alterar Senha", use_container_width=True)
        
        if submit:
            if not current_password or not new_password:
                st.error("⚠️ Preencha todos os campos!")
            elif len(new_password) < 6:
                st.error("⚠️ Nova senha deve ter no mínimo 6 caracteres!")
            elif new_password != confirm_password:
                st.error("⚠️ Senhas não conferem!")
            else:
                # Verifica senha atual
                success, _, message = auth.authenticate(user['username'], current_password)
                
                if not success:
                    st.error("❌ Senha atual incorreta!")
                else:
                    # Atualiza senha
                    success, msg = auth.update_user(user['id'], password=new_password)
                    if success:
                        st.success("✅ Senha alterada com sucesso!")
                        st.balloons()
                    else:
                        st.error(f"❌ {msg}")
