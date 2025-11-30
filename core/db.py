# core/db.py
# ================================================
# Módulo central de acesso ao banco de dados Supabase
# Projeto Phoenix — by Maikinho
# ================================================

import os
import requests
from datetime import datetime
import streamlit as st


# ===============================
# CONFIG
# ===============================

def _get_secret(name: str, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except:
        pass
    return os.getenv(name, default)


SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY ausentes.")


BASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}


# ===============================
# CLIENTES
# ===============================

def get_all_clients():
    """Retorna todos os clientes (lista de dicts)."""
    url = f"{SUPABASE_URL}/rest/v1/clientes?select=*"
    r = requests.get(url, headers=BASE_HEADERS, timeout=20)
    r.raise_for_status()
    return r.json() or []


def get_client_by_id(cliente_id: str):
    """Retorna um cliente específico pelo ID."""
    url = f"{SUPABASE_URL}/rest/v1/clientes?select=*&id=eq.{cliente_id}"
    r = requests.get(url, headers=BASE_HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()
    return data[0] if data else None


def update_client_fields(cliente_id: str, fields: dict):
    """Atualiza campos arbitrários do cliente."""
    url = f"{SUPABASE_URL}/rest/v1/clientes?id=eq.{cliente_id}"
    r = requests.patch(url, headers=BASE_HEADERS, json=fields)
    r.raise_for_status()
    return r.json()


# ===============================
# PERMISSÕES / ASSINATURAS
# ===============================
# Tabela: clientes (campo: carteiras)

def set_client_permissions(cliente_id: str, carteiras: list):
    """Define diretamente as carteiras do cliente."""
    fields = {"carteiras": carteiras}
    return update_client_fields(cliente_id, fields)


# ===============================
# LOGS (opcional: integrado)
# ===============================

def registrar_log(evento: str, descricao: str, cliente_id: str = None):
    """Envia log para tabela logs, se existir."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/logs"
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "evento": evento,
            "descricao": descricao,
            "cliente_id": cliente_id
        }
        requests.post(url, headers=BASE_HEADERS, json=payload, timeout=10)
    except:
        pass
