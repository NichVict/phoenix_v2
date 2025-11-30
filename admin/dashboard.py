import streamlit as st

from admin.users import list_users, count_active_users, count_expired_users, render as render_users
from admin.telegram import render as render_telegram
from admin.logs import render as render_logs
from admin.CRM.CRM import render as render_crm


def render():
    st.title("🛠 Painel Administrativo — Phoenix")

    # =======================
    # MÉTRICAS RESUMO
    # =======================
    try:
        total_cadastrados = len(list_users())
    except Exception:
        total_cadastrados = 0

    try:
        ativos = count_active_users()
    except Exception:
        ativos = 0

    try:
        vencidos = count_expired_users()
    except Exception:
        vencidos = 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Clientes Ativos", ativos)
    with col2:
        st.metric("Clientes Vencidos", vencidos)
    with col3:
        st.metric("Total Cadastrados", total_cadastrados)

    st.markdown("---")

    # =======================
    # ABAS DO PAINEL ADMIN
    # =======================
    aba = st.tabs(
        [
            "📋 CRM",
            "👤 Clientes",
            "🤖 Telegram",
            "📝 Logs"
        ]
    )

    # Cada aba chama o respectivo módulo
    with aba[0]:
        render_crm()

    with aba[1]:
        render_users()

    with aba[2]:
        render_telegram()

    with aba[3]:
        render_logs()
