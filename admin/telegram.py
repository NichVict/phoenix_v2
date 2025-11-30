import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import os

# ======================================================
# CONFIGURAÇÕES
# ======================================================

def _get_secret(name: str, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)

SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")
TELEGRAM_TOKEN = _get_secret("TELEGRAM_TOKEN")  # token do milhao_crm_bot

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE_URL ou SUPABASE_KEY ausentes.")
    st.stop()

if not TELEGRAM_TOKEN:
    st.error("❌ TELEGRAM_TOKEN não configurado nos secrets.")
    st.stop()

BASE_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# ======================
# CHAT IDs DOS GRUPOS - oficiais Phoenix v2
# ======================
GROUP_CHAT_IDS = {
    "Carteira de Ações IBOV": -1002198655576,
    "Carteira de Small Caps": -1003251673981,
    "Carteira de BDRs":       -1002171530332,
    "Carteira de Opções":     -1003274356400,
}

# ======================================================
# SUPABASE HELPERS
# ======================================================

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def sb_get_all_clients():
    url = f"{SUPABASE_URL}/rest/v1/clientes"
    params = {
        "select": "*",
        "order": "created_at.desc",
    }
    r = requests.get(url, headers=sb_headers(), params=params, timeout=20)
    try:
        return r.json()
    except:
        return []

def sb_update_client(client_id, payload: dict):
    url = f"{SUPABASE_URL}/rest/v1/clientes?id=eq.{client_id}"
    return requests.patch(url, headers=sb_headers(), json=payload, timeout=20)

# ======================================================
# TELEGRAM HELPERS
# ======================================================

def tg_get_chat_member(chat_id, user_id):
    """Retorna informações do usuário no grupo."""
    url = BASE_API + "/getChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    try:
        resp = requests.post(url, json=payload, timeout=15).json()
        return resp
    except Exception as e:
        return {"ok": False, "error": str(e)}

def tg_kick(chat_id, user_id):
    """Expulsa usuário manualmente."""
    url = BASE_API + "/kickChatMember"
    payload = {"chat_id": chat_id, "user_id": user_id}
    try:
        resp = requests.post(url, json=payload, timeout=15).json()
        return resp.get("ok", False), resp
    except Exception as e:
        return False, {"error": str(e)}

# ======================================================
# LAYOUT
# ======================================================

st.set_page_config(page_title="Gerenciador do Telegram — Phoenix", layout="wide")
st.title("🤖 Gerenciador do Telegram — Phoenix CRM")
st.caption("Administração completa dos acessos via Telegram.")

st.markdown("---")

# ======================================================
# CARREGAR CLIENTES
# ======================================================

dados = sb_get_all_clients()
if not dados:
    st.warning("Nenhum cliente encontrado.")
    st.stop()

df = pd.DataFrame(dados)

# Normalizar campos
df["carteiras"] = df["carteiras"].apply(lambda x: x if isinstance(x, list) else [])
df["data_fim"] = pd.to_datetime(df["data_fim"], errors="coerce").dt.date

today = date.today()

# ======================================================
# KPIs
# ======================================================

def count_connected(df):
    return len(df[df["telegram_connected"] == True])

def count_disconnected(df):
    return len(df[df["telegram_connected"] == False])

def count_removed(df):
    return len(df[df["telegram_removed_at"].notnull()])

k1, k2, k3 = st.columns(3)
k1.metric("Conectados ao Telegram", count_connected(df))
k2.metric("Desconectados", count_disconnected(df))
k3.metric("Removidos", count_removed(df))

st.markdown("---")

# ======================================================
# FILTROS
# ======================================================

nome_filtro = st.text_input("🔍 Filtrar por nome/email:")
status_filtro = st.multiselect(
    "Status Telegram",
    ["Conectado", "Desconectado", "Removido"]
)

def filtrar(df):
    temp = df.copy()

    if nome_filtro:
        nf = nome_filtro.lower()
        temp = temp[
            temp["nome"].str.lower().str.contains(nf)
            | temp["email"].str.lower().str.contains(nf)
        ]

    if status_filtro:
        condicoes = []
        if "Conectado" in status_filtro:
            condicoes.append(temp["telegram_connected"] == True)
        if "Desconectado" in status_filtro:
            condicoes.append(temp["telegram_connected"] == False)
        if "Removido" in status_filtro:
            condicoes.append(temp["telegram_removed_at"].notnull())

        if condicoes:
            temp = temp[ pd.concat(condicoes, axis=1).any(axis=1) ]

    return temp

df_filtrado = filtrar(df)

# ======================================================
# TABELA PRINCIPAL COM AÇÕES
# ======================================================

st.subheader("📋 Tabela de Clientes")

for _, row in df_filtrado.iterrows():
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])

        with c1:
            st.markdown(f"**{row['nome']}**  \n{row['email']}")
            st.caption(f"📞 {row.get('telefone','')}")

            carteiras = row["carteiras"]
            st.write("Carteiras:", ", ".join(carteiras) if carteiras else "Nenhuma")

            fim = row["data_fim"]
            st.write(f"Vigência: **{fim}**")

            # Status Telegram
            status_txt = (
                "🟢 Conectado" if row["telegram_connected"]
                else "🔴 Desconectado"
            )
            if row.get("telegram_removed_at"):
                status_txt = "⚫ Removido"

            st.write("Status Telegram:", status_txt)

            if row.get("telegram_username"):
                st.caption(f"@{row['telegram_username']} (id {row['telegram_id']})")

        with c2:
            st.write("")

            # --------------------------
            # 🔄 BOTÃO RESYNC
            # --------------------------
            if st.button("🔄 Re-sync", key=f"sync_{row['id']}"):
                sb_update_client(row["id"], {
                    "telegram_last_sync": datetime.utcnow().isoformat()
                })
                st.success("Sincronizado com sucesso.")
                st.experimental_rerun()

            # --------------------------
            # 🚫 BOTÃO EXPULSAR MANUAL
            # --------------------------
            if st.button("⛔ Expulsar", key=f"expulsar_{row['id']}"):
                if not row.get("telegram_id"):
                    st.error("Cliente não possui telegram_id salvo.")
                else:
                    expelled_list = []
                    for cart in row["carteiras"]:
                        chat = GROUP_CHAT_IDS.get(cart)
                        if not chat:
                            continue
                        ok, resp = tg_kick(chat, row["telegram_id"])
                        expelled_list.append(f"{cart}: {ok}")

                    # Marca como removido no Supabase
                    sb_update_client(row["id"], {
                        "telegram_connected": False,
                        "telegram_removed_at": datetime.utcnow().isoformat()
                    })

                    st.success("Removido dos grupos: " + ", ".join(expelled_list))
                    st.experimental_rerun()

            # --------------------------
            # ♻ BOTÃO RESETAR STATUS TELEGRAM
            # --------------------------
            if st.button("♻ Resetar", key=f"reset_{row['id']}"):
                sb_update_client(row["id"], {
                    "telegram_connected": False,
                    "telegram_removed_at": None
                })
                st.info("Status resetado.")
                st.experimental_rerun()

st.markdown("---")

# ======================================================
# SEÇÃO: REMOVIDOS
# ======================================================

st.subheader("🚫 Clientes Removidos (Log Phoenix)")

df_removed = df[df["telegram_removed_at"].notnull()]
if df_removed.empty:
    st.info("Nenhum cliente foi removido ainda.")
else:
    st.dataframe(
        df_removed[
            ["id", "nome", "email", "carteiras",
             "telegram_id", "telegram_username", "telegram_removed_at"]
        ],
        use_container_width=True
    )

st.markdown("---")

# ======================================================
# AÇÃO MANUAL: RODAR LIMPEZA AUTOMÁTICA
# ======================================================

st.subheader("🧹 Rodar limpeza automática de vencidos (manual)")
st.caption("Use apenas para testes. O bot oficial já roda isso automaticamente.")

if st.button("🚨 Rodar limpeza agora"):
    from datetime import datetime
    # esta função imita o bot:
    def cleanup():
        clientes = sb_get_all_clients()
        hoje = date.today()
        removidos = 0

        for cli in clientes:
            if not cli.get("telegram_id"):
                continue
            if not cli.get("telegram_connected"):
                continue

            # data fim
            try:
                fim = datetime.fromisoformat(cli["data_fim"]).date()
            except:
                continue

            if fim >= hoje:
                continue

            # expulsar
            for cart in cli["carteiras"]:
                chat = GROUP_CHAT_IDS.get(cart)
                if chat:
                    ok, resp = tg_kick(chat, cli["telegram_id"])

            # marcar como removido
            sb_update_client(cli["id"], {
                "telegram_connected": False,
                "telegram_removed_at": datetime.utcnow().isoformat()
            })
            removidos += 1

        return removidos

    qt = cleanup()
    st.success(f"Limpeza concluída. Clientes removidos: {qt}")
