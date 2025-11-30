import streamlit as st
from admin.CRM.clientes import listar_clientes

def render():
    st.title("📋 CRM — Phoenix")

    st.markdown("### Lista de clientes (vindo do Supabase)")

    clientes = listar_clientes()

    if not clientes:
        st.info("Nenhum cliente encontrado ou erro ao consultar a base.")
    else:
        st.dataframe(clientes, use_container_width=True)

    st.markdown("---")
    st.warning("⚠️ Esta é a interface inicial do CRM. A seguir vamos migrar TODO o seu CRM real aqui dentro.")
