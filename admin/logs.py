import os
from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

# =======================================================
# CONFIGURAÇÕES SUPABASE
# =======================================================

def _get_secret(name: str, default=None):
    """Busca primeiro em st.secrets e cai para variável de ambiente."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE_URL ou SUPABASE_KEY não configurados.")
    st.stop()


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


LOGS_ENDPOINT = f"{SUPABASE_URL}/rest/v1/logs"


# =======================================================
# FUNÇÃO PÚBLICA: REGISTRAR LOG
# =======================================================

def registrar_log(
    evento: str,
    descricao: str,
    cliente_id: str | None = None,
    origem: str | None = None,
    extra: dict | None = None,
):
    """
    Insere um registro na tabela logs (via REST).

    Uso típico:
        registrar_log(
            evento="cliente_excluido",
            descricao="Cliente removido do CRM",
            cliente_id="123"
        )
    """
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "evento": evento,
        "descricao": descricao,
        "cliente_id": cliente_id,
        "origem": origem or "phoenix_app",
        "extra": extra or {},
    }

    try:
        r = requests.post(
            LOGS_ENDPOINT,
            headers=_headers(),
            json=payload,
            params={"return": "representation"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list) and data:
            return data[0]
        return data
    except Exception as e:
        # Como é função utilitária, não vamos quebrar o app inteiro por causa disso
        print("Erro ao registrar_log:", e)
        return None


# =======================================================
# UI: PÁGINA DE LOGS (ADMIN)
# =======================================================

def _buscar_logs(
    dias: int = 7,
    evento: str | None = None,
    cliente_id: str | None = None,
) -> pd.DataFrame:
    """Busca logs recentes da API do Supabase."""

    params = {
        "select": "id,timestamp,evento,descricao,cliente_id,origem,extra",
        "order": "timestamp.desc",
        "limit": "500",
    }

    # Filtro por data mínima
    dt_min = (datetime.utcnow() - timedelta(days=dias)).isoformat()
    params["timestamp"] = f"gte.{dt_min}"

    if evento:
        params["evento"] = f"eq.{evento}"
    if cliente_id:
        params["cliente_id"] = f"eq.{cliente_id}"

    try:
        r = requests.get(LOGS_ENDPOINT, headers=_headers(), params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"Erro ao buscar logs: {e}")
        return pd.DataFrame()


def render():
    """Renderiza a página de Logs do Sistema no painel admin."""
    st.title("📝 Logs do Sistema — Phoenix CRM")
    st.caption("Monitoramento completo do ecossistema (CRM + Telegram + Bot).")

    st.markdown("---")

    # ---------------------- FILTROS ----------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        dias = st.number_input("Dias para trás", 1, 90, 7)

    with col2:
        evento = st.text_input("Filtrar por evento (opcional)", placeholder="ex.: cliente_excluido")

    with col3:
        cliente_id = st.text_input("Filtrar por Cliente ID (opcional)")

    if st.button("🔍 Atualizar", use_container_width=True):
        st.session_state["_logs_reload"] = True

    # Recarrega automaticamente na primeira abertura
    if "_logs_reload" not in st.session_state:
        st.session_state["_logs_reload"] = True

    if not st.session_state["_logs_reload"]:
        st.info("Clique em **Atualizar** para carregar os logs.")
        return

    # ---------------------- BUSCA ----------------------
    df = _buscar_logs(dias=dias, evento=evento or None, cliente_id=cliente_id or None)

    if df.empty:
        st.info("Nenhum log registrado ainda.")
        return

    # Ordena
    df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)

    # ---------------------- TABELA RESUMO ----------------------
    with st.expander("📊 Visão em tabela", expanded=False):
        st.dataframe(
            df[
                [
                    "timestamp",
                    "evento",
                    "descricao",
                    "cliente_id",
                    "origem",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.subheader("📋 Resultados detalhados")

    # ---------------------- CARDS ----------------------
    st.markdown(
        """
        <style>
        .card-log {
            background: #0f172a;
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 10px;
            border: 1px solid rgba(148, 163, 184, 0.4);
            font-size: 0.9rem;
        }
        .card-log b {
            color: #e5e7eb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    for _, row in df.iterrows():
        extra = row.get("extra") or {}
        if isinstance(extra, dict):
            extra_txt = ", ".join(f"{k}: {v}" for k, v in extra.items())
        else:
            extra_txt = str(extra)

        st.markdown(
            f"""
            <div class='card-log'>
                <b>📌 Evento:</b> {row['evento']}<br>
                <b>🕒 Data:</b> {row['timestamp']}<br>
                <b>👤 Cliente ID:</b> {row['cliente_id'] or '—'}<br>
                <b>📍 Origem:</b> {row.get('origem') or '—'}<br>
                <b>📝 Descrição:</b> {row['descricao'] or '—'}<br>
                <b>🔍 Extra:</b> {extra_txt or '—'}
            </div>
            """,
            unsafe_allow_html=True,
        )
