import streamlit as st
import admin.users as admin_users

st.set_page_config(
    page_title="Admin - Phoenix",
    layout="wide",
)

# ==================== ESTILO ====================
st.markdown("""
<style>
.card-admin {
    background: radial-gradient(circle at top, rgba(0,255,180,0.28), #121212);
    border: 1px solid rgba(0,255,180,0.35);
    padding: 22px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 0 14px rgba(0,255,180,0.20);
    transition: 0.25s ease;
}
.card-admin:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 22px rgba(0,255,200,0.40);
}
.card-admin h2 {
    margin: 0;
    font-size: 34px;
    color: #00E6A8;
}
.card-admin p {
    margin: 6px 0 0;
    color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.title("🛠 Painel Administrativo — Phoenix")
st.caption("Gestão centralizada — CRM, Telegram, Assinaturas e Logs")

# ==================== CARDS ====================
users = admin_users.list_users()          # <<<<<<<<<<<<<< ADICIONADO
ativos = admin_users.count_active_users()
vencidos = admin_users.count_expired_users()
total = len(users)

cols = st.columns(4)
cards = [
    ("🟢 Ativos", ativos),
    ("🔴 Vencidos", vencidos),
    ("👤 Total Cadastrados", total),
    ("🫂 Leads", len([u for u in users if "Leads" in (u.get("carteiras") or [])])),
]

for col, (titulo, valor) in zip(cols, cards):
    with col:
        st.markdown(f"""
        <div class='card-admin'>
            <h2>{valor}</h2>
            <p>{titulo}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ==================== LINKS ====================
st.subheader("Acessos Rápidos")

st.page_link("admin/users.py", label="👤 Gerenciar Clientes", icon="👤")
st.page_link("admin/access.py", label="🔐 Assinaturas / Permissões", icon="🔐")
st.page_link("admin/telegram.py", label="🤖 Gerenciar Telegram", icon="🤖")
st.page_link("admin/logs.py", label="📝 Logs do Sistema", icon="📝")

st.markdown("---")
st.caption("© Phoenix • Automação • Inteligência • Execução")
