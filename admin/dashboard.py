import streamlit as st
from admin.users import list_users
from admin.users import count_active_users
from admin.users import count_expired_users

def render():
    st.title("🛠 Painel Administrativo — Phoenix")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Clientes Ativos", count_active_users())
    with col2:
        st.metric("Clientes Vencidos", count_expired_users())
    with col3:
        st.metric("Total Cadastrados", len(list_users()))

    st.markdown("---")
    st.subheader("Gerenciamento")

    st.page_link("admin/users.py", label="👤 Gerenciar Clientes", icon="👤")
    st.page_link("admin/access.py", label="🔐 Permissões / Assinaturas", icon="🔐")
    st.page_link("admin/telegram.py", label="🤖 Telegram Bots", icon="🤖")
    st.page_link("admin/logs.py", label="📝 Logs do Sistema", icon="📝")
