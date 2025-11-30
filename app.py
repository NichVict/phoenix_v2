import streamlit as st

from core.auth import get_current_user, login_screen
from core.permissions import get_user_permissions

from dashboards.home import render_home
import dashboards.ibov as dash_ibov
import dashboards.bdr as dash_bdr
import dashboards.smallcaps as dash_small
import dashboards.opcoes as dash_opc
import dashboards.scanner_acoes as dash_scan_acoes
import dashboards.scanner_opcoes as dash_scan_opc

import admin.dashboard as admin_dash


# ---------------------------------------------------
# CONFIG GERAL DO APP
# ---------------------------------------------------
st.set_page_config(
    page_title="Phoenix v2",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------
# AUTENTICAÇÃO BÁSICA
# ---------------------------------------------------
user = get_current_user()

if user is None:
    # Nenhum usuário logado → mostra tela de login e para aqui
    login_screen()
    st.stop()

# Tentamos extrair o email do objeto user (pode ser dict ou objeto)
email = getattr(user, "email", None)
if email is None and isinstance(user, dict):
    email = user.get("email")

st.sidebar.markdown(f"**Usuário:** `{email or 'desconhecido'}`")


# ---------------------------------------------------
# PERMISSÕES DO USUÁRIO (VIA CRM - TABELA CLIENTES)
# ---------------------------------------------------
try:
    permissoes = get_user_permissions(email) if email else []
except Exception:
    permissoes = []


# ---------------------------------------------------
# DEFINIÇÃO DAS PÁGINAS
# (no futuro vamos filtrar pelo que o cliente assinou)
# ---------------------------------------------------
pages = {}

# Home sempre disponível
pages["🏠 Home"] = lambda: render_home(user)

# Demais dashboards – por enquanto todos visíveis;
# depois ajustamos para mostrar só se o cliente tiver a assinatura.
pages["📊 Carteira IBOV"] = dash_ibov.render
pages["💵 Carteira BDR"] = dash_bdr.render
pages["📈 Carteira SmallCaps"] = dash_small.render
pages["🟪 Carteira de Opções"] = dash_opc.render
pages["🔍 Scanner de Ações"] = dash_scan_acoes.render
pages["🔎 Scanner de Opções"] = dash_scan_opc.render


# ---------------------------------------------------
# VERIFICA SE USUÁRIO É ADMIN
# (vamos usar um secret: ADMIN_EMAILS = "seuemail@x.com,outro@x.com")
# ---------------------------------------------------
admin_emails_raw = st.secrets.get("ADMIN_EMAILS", "")
admin_emails = [e.strip().lower() for e in admin_emails_raw.split(",") if e.strip()]

is_admin = False
if email and admin_emails:
    is_admin = email.lower() in admin_emails

if is_admin:
    pages["🛠 Painel Admin"] = admin_dash.render


# ---------------------------------------------------
# MENU LATERAL
# ---------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### Navegação")

opcao = st.sidebar.radio("Selecione a página:", list(pages.keys()))

# Botão de logout
if st.sidebar.button("Sair"):
    st.session_state.pop("user", None)
    st.experimental_rerun()

# Render da página escolhida
pages[opcao]()
