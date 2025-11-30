import streamlit as st
from core.db import get_client, get_all_clients, insert_client, update_client

def list_users():
    return get_all_clients()

def count_active_users():
    users = get_all_clients()
    return sum(1 for u in users if u.get("is_active"))

def count_expired_users():
    users = get_all_clients()
    return sum(1 for u in users if not u.get("is_active"))

def render():
    st.title("👤 Gerenciar Clientes")

    clientes = get_all_clients()

    st.markdown("### Clientes cadastrados")
    st.dataframe(clientes, use_container_width=True)

    with st.expander("➕ Cadastrar novo cliente"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        assinatura_ativa = st.checkbox("Assinatura ativa", value=True)

        if st.button("Salvar cliente"):
            insert_client({
                "name": nome,
                "email": email,
                "phone": telefone,
                "is_active": assinatura_ativa
            })
            st.success("Cliente cadastrado!")
            st.experimental_rerun()
