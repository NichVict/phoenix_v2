import streamlit as st

from core.auth import get_current_user, login_screen
from core.permissions import get_user_permissions

from dashboards.home import render_home
import dashboards.ibov as dash_ibov
import dashboards.bdr as dash_bdr
import dashboards.smallcaps as dash_small
import dashboards.opcoes as dash_opc
import dashboards.scanner_acoes as dash_scan_acoes
#import dashboards.scanner_opcoes as dash_scan_opc

# Admin pages

import admin.users as admin_users
import admin.access as admin_access
import admin.telegram as admin_telegram
import admin.logs as admin_logs


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
# ======================================================
# 🔓 MODO DESENVOLVEDOR — LOGIN DESATIVADO TEMPORARIAMENTE
# ======================================================
# Em produção, basta remover esse bloco e voltar ao login normal.

user = {"email": "dev@local"}
email = "dev@local"

# pular completamente o sistema de login:
# user = get_current_user()
# if user is None:
#     login_screen()
#     st.stop()


# Extrai email
email = getattr(user, "email", None)
if email is None and isinstance(user, dict):
    email = user.get("email")

st.sidebar.markdown(f"**Usuário:** `{email or 'desconhecido'}``")


# ---------------------------------------------------
# PERMISSÕES DO USUÁRIO
# ---------------------------------------------------
try:
    permissoes = get_user_permissions(email) if email else []
except Exception:
    permissoes = []


# ---------------------------------------------------
# DEFINIÇÃO DAS PÁGINAS (NAVEGAÇÃO)
# ---------------------------------------------------
pages = {}

# Home sempre disponível
pages["🏠 Home"] = lambda: render_home(user)

# Dashboards principais
pages["📊 Carteira IBOV"] = dash_ibov.render
pages["💵 Carteira BDR"] = dash_bdr.render
pages["📈 Carteira SmallCaps"] = dash_small.render
pages["🟪 Carteira de Opções"] = dash_opc.render
pages["🔍 Scanner de Ações"] = dash_scan_acoes.render
#pages["🔎 Scanner de Opções"] = dash_scan_opc.render


# ---------------------------------------------------
# DEFINIÇÃO DO BLOCO ADMIN (se o usuário for admin)
# ---------------------------------------------------
admin_emails_raw = st.secrets.get("ADMIN_EMAILS", "")
admin_emails = [e.strip().lower() for e in admin_emails_raw.split(",") if e.strip()]

is_admin = False
if email and admin_emails:
    is_admin = email.lower() in admin_emails

# Sistema de seções: None indica TÍTULO DE SESSÃO
if is_admin:
    pages["--- 🛠 Administração ---"] = None
    pages["👤 Clientes"] = admin_users.render
    pages["🔐 Assinaturas"] = admin_access.render
    pages["🤖 Telegram"] = admin_telegram.render
    pages["📝 Logs do Sistema"] = admin_logs.render


# ---------------------------------------------------
# SIDEBAR / MENU LATERAL
# ---------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Navegação")

# Gerar lista de labels para exibir no radio()
labels = []
for nome, func in pages.items():
    if func is None:
        labels.append(nome)  # título de seção
    else:
        labels.append(nome)

opcao = st.sidebar.radio("Selecione a página:", labels)

# Botão de logout
if st.sidebar.button("Sair"):
    st.session_state.pop("user", None)
    st.experimental_rerun()

# ---------------------------------------------------
# RENDER DA PÁGINA ESCOLHIDA
# ---------------------------------------------------
# Se for um título de seção (None), apenas exibe o cabeçalho
if pages.get(opcao) is None:
    st.write(f"### {opcao.replace('-', '').strip()}")
else:
    pages[opcao]()
