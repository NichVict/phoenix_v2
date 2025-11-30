import streamlit as st
from core.telegram import sync_telegram_ids, remove_from_group
from core.db import get_all_clients

def render():
    st.title("🤖 Telegram Manager")

    st.markdown("### 📌 Sincronizar IDs do Telegram")
    if st.button("Sincronizar agora"):
        sync_telegram_ids()
        st.success("IDs sincronizados com sucesso!")

    st.markdown("---")

    st.markdown("### ❌ Remover cliente do grupo")
    clientes = get_all_clients()
    emails = [c["email"] for c in clientes]

    cliente_sel = st.selectbox("Selecione o cliente", emails)

    if st.button("Remover do grupo Telegram"):
        remove_from_group(cliente_sel)
        st.success("Cliente removido!")
