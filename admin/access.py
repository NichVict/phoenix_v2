# admin/access.py
# ============================================================
# Gestão de permissões / assinaturas dos clientes — Phoenix
# ============================================================

import streamlit as st
import pandas as pd

from core.db import (
    get_all_clients,
    get_client_by_id,
    set_client_permissions,
    registrar_log
)


# ============================================================
# Página
# ============================================================

def render():
    st.title("🔐 Permissões / Assinaturas — Phoenix CRM")
    st.caption("Gerencie quais carteiras cada cliente tem acesso.")

    st.markdown("---")

    # ===============================
    # Carregar clientes
    # ===============================
    try:
        clientes = get_all_clients()
    except Exception as e:
        st.error(f"Erro ao carregar clientes: {e}")
        return

    if not clientes:
        st.info("Nenhum cliente encontrado.")
        return

    df = pd.DataFrame(clientes)

    # ===============================
    # Seleção do cliente
    # ===============================
    lista_nomes = {f"{c['nome']} — ({c['email']})": c["id"] for c in clientes}

    escolha = st.selectbox("Selecione o cliente", list(lista_nomes.keys()))

    cliente_id = lista_nomes[escolha]
    cliente = get_client_by_id(cliente_id)

    if not cliente:
        st.error("Cliente não encontrado.")
        return

    nome = cliente["nome"]
    email = cliente["email"]
    carteiras_atuais = cliente.get("carteiras", [])

    st.subheader(f"👤 Cliente selecionado: {nome}")
    st.write(f"📧 **Email:** {email}")

    st.markdown("---")

    # ===============================
    # Editar carteiras
    # ===============================

    CART_OPCOES = [
        "Carteira de Ações IBOV",
        "Carteira de BDRs",
        "Carteira de Opções",
        "Leads",
        "Estratégias Phoenix",
    ]

    novas = st.multiselect(
        "Carteiras permitidas",
        CART_OPCOES,
        default=carteiras_atuais if isinstance(carteiras_atuais, list) else [],
    )

    if st.button("💾 Salvar alterações", use_container_width=True):
        try:
            set_client_permissions(cliente_id, novas)

            registrar_log(
                "update_carteiras",
                f"Alterou carteiras: {novas}",
                cliente_id=cliente_id
            )

            st.success("Permissões atualizadas com sucesso!")
            st.rerun()

        except Exception as e:
            st.error(f"Erro ao atualizar: {e}")

    st.markdown("---")

    # ===============================
    # Exibir tabela resumida
    # ===============================
    st.subheader("📋 Tabela de clientes")

    tabela = df[["id", "nome", "email", "carteiras"]]
    st.dataframe(tabela, hide_index=True, use_container_width=True)
