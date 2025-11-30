import streamlit as st
import requests
from core.supabase_client import get_supabase

def login_screen():
    st.title("🔐 Login Phoenix v2")

    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar", type="primary"):
        # Carrega credenciais do secrets
        supabase_url = st.secrets.get("SUPABASE_URL")
        supabase_key = st.secrets.get("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            st.error("Erro: SUPABASE_URL ou SUPABASE_KEY ausentes no secrets.")
            return

        # Endpoint REST de autenticação
        url = f"{supabase_url}/auth/v1/token?grant_type=password"

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "email": email,
            "password": password
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()

            if response.status_code != 200:
                st.error("Email ou senha inválidos.")
                return

            # User autenticado – salva na session_state
            st.session_state["user"] = {
                "email": data.get("user", {}).get("email"),
                "id": data.get("user", {}).get("id"),
                "access_token": data.get("access_token"),
            }

            st.success("Login realizado com sucesso!")
            st.rerun()

        except Exception as e:
            st.error(f"Erro inesperado: {e}")


def get_current_user():
    """
    Apenas retorna o usuário salvo na sessão.
    """
    return st.session_state.get("user")
