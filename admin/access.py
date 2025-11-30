import streamlit as st
from core.permissions import get_user_permissions, set_user_permissions
from core.db import get_all_clients

def render():
    st.title("🔐 Permissões / Assinaturas")

    clientes = get_all_clients()

    for cliente in clientes:
        st.markdown(f"### {cliente['name']} — {cliente['email']}")
        
        permissoes = get_user_permissions(cliente["email"])

        novas = st.multiselect(
            "Acessos liberados",
            options=[
                "IBOV",
                "BDR",
                "SmallCaps",
                "Opções",
                "Scanner Ações",
                "Scanner Opções"
            ],
            default=permissoes,
            key=f"perm_{cliente['email']}"
        )

        if st.button(f"Salvar {cliente['email']}"):
            set_user_permissions(cliente["email"], novas)
            st.success("Atualizado!")
