import streamlit as st
from core.supabase_client import get_supabase

def login_screen():
    st.title("🔐 Login Phoenix v2")
    email = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        supabase = get_supabase()
        try:
            auth = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            st.session_state["user"] = auth.user
            st.rerun()
        except Exception:
            st.error("Email ou senha inválidos.")

def get_current_user():
    return st.session_state.get("user")
