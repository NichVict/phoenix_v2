import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import os

# =======================================================
# CONFIGURAÇÕES SUPABASE
# =======================================================

def _get_secret(name, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except:
        pass
    return os.getenv(name, default)

SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE_URL ou SUPABASE_KEY não configurados.")
    st.stop()

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


# =======================================================
# FUNÇÃO GLOBAL: registrar_log
# =======================================================

def registrar_log(evento: str, descricao: str, cliente_id=None, extra: dict = None):
    """
    Registra um log universal no Supabase.
    Pode ser usado pelo CRM, Telegram Manager e Bot.
    """
    payload = {
        "evento": evento,
        "descricao": descricao,
        "cliente_id": cliente_id,
        "extra": extra or {},
    }

    url = f"{SUPABASE_URL}/rest/v1/logs"
    try:
        requests.post(url, headers=sb_headers(), json=payload, timeout=15)
    except Exception as e:
        print("Erro ao registrar log:", e)


# =======================================================
# USADO PELO PAINEL: Carregar logs
# =======================================================

def carregar_logs():
    url = f"{SUPABASE_URL}/rest/v1/logs"
    params = {
        "select": "*",
        "order": "timestamp.desc"
    }
    try:
        r = requests.get(url, headers=sb_headers(), params=params, timeout=20)
        data = r.json()
        if isinstance(data, list):
            return data
        return []
    except:
        return []


# =======================================================
# LAYOUT PHOENIX DARK
# =======================================================

st.set_page_config(page_title="Logs — Phoenix", layout="wide")
st.title("📝 Logs do Sistema — Phoenix CRM")
st.caption("Monitoramento completo do ecossistema (CRM + Telegram + Bot).")

st.markdown("""
<style>
.card-log {
    background: rgba(0,255,180,0.06);
    border-left: 4px solid #00E6A8;
    padding: 12px 18px;
    margin-bottom: 12px;
    border-radius: 8px;
}
.card-log:hover {
    background: rgba(0,255,180,0.10);
}
</style>
""", unsafe_allow_html=True)


# =======================================================
# FILTROS
# =======================================================

dados = carregar_logs()

if not dados:
    st.info("Nenhum log registrado ainda.")
    st.stop()

df = pd.DataFrame(dados)
df["timestamp"] = pd.to_datetime(df["timestamp"])

col1, col2, col3 = st.columns(3)

with col1:
    evento_filtro = st.multiselect(
        "Filtrar por evento",
        sorted(df["evento"].unique())
    )

with col2:
    cliente_filtro = st.text_input("Filtrar por Cliente ID:")

with col3:
    dias = st.number_input("Últimos X dias:", min_value=1, max_value=365, value=30)


# =======================================================
# APLICAR FILTROS
# =======================================================

df_filtrado = df.copy()

if evento_filtro:
    df_filtrado = df_filtrado[df_filtrado["evento"].isin(evento_filtro)]

if cliente_filtro:
    df_filtrado = df_filtrado[df_filtrado["cliente_id"].astype(str) == cliente_filtro]

limite_data = datetime.utcnow() - timedelta(days=dias)
df_filtrado = df_filtrado[df_filtrado["timestamp"] >= limite_data]


# =======================================================
# EXIBIR LOGS
# =======================================================

st.subheader("📋 Resultados")

for _, row in df_filtrado.iterrows():
    with st.container():
        st.markdown(f"""
        <div class='card-log'>
            <b>📌 Evento:</b> {row['evento']}  
            <br><b>🕒 Data:</b> {row['timestamp']}  
            <br><b>👤 Cliente ID:</b> {row['cliente_id'] if row['cliente_id'] else '—'}  
            <br><b>📝 Descrição:</b> {row['descricao']}  
            <br><b>🔍 Extra:</b> {row.get('extra', {})}
        </div>
        """, unsafe_allow_html=True)
