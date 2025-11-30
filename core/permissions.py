# core/permissions.py
# ============================================
# Gerenciamento simples de permissões do usuário
# ============================================

import streamlit as st

# Estrutura mínima (pode expandir depois se quiser)
DEFAULT_PERMISSIONS = {
    "admin": [
        "view_dashboard",
        "manage_users",
        "manage_access",
        "view_logs",
        "manage_crm",
        "manage_bot",
    ],
    "user": [
        "view_dashboard",
    ]
}

def get_role() -> str:
    """Retorna o papel do usuário logado (fixo por enquanto)."""
    return st.session_state.get("role", "admin")  # padrão: admin

def get_user_permissions() -> list:
    """Retorna permissões do usuário atual."""
    role = get_role()
    return DEFAULT_PERMISSIONS.get(role, [])

def set_user_permissions(role: str, permissions: list):
    """
    Atualiza permissões do papel especificado.
    Para ambiente real, isso deve ir para o Supabase.
    """
    DEFAULT_PERMISSIONS[role] = permissions
