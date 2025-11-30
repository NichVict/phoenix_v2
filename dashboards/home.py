import streamlit as st
from core.permissions import get_user_permissions

def render_home(user):
    st.title("🏠 Phoenix — Minhas Assinaturas")

    email = user.get("email") if isinstance(user, dict) else getattr(user, "email", None)

    permissoes = get_user_permissions(email)

    st.markdown("### 📦 Minhas Carteiras / Serviços")

    for item in permissoes:
        st.success(f"✔ {item} — Acessar")

    st.markdown("---")
    st.markdown("### 🛒 Outras Carteiras (Vitrine)")

    produtos = [
        "Carteira IBOV",
        "Carteira BDR",
        "Carteira SmallCaps",
        "Carteira Opções",
        "Scanner Ações",
        "Scanner Opções"
    ]

    for p in produtos:
        if p not in permissoes:
            st.info(f"{p} — Ver desempenho → Assinar")
