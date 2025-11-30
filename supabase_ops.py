# supabase_ops.py — Phoenix v2
# Módulo central para operações de Opções no Supabase

import os
import requests
from datetime import datetime

# =======================================================
# SECRETS / CONFIG
# =======================================================

def _get_secret(name, default=None):
    """
    Lê tanto de st.secrets quanto de variáveis de ambiente.
    """
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except:
        pass

    return os.getenv(name, default)


SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY não configurados — verifique secrets.")


# REST endpoint padrão
REST_ENDPOINT = f"{SUPABASE_URL}/rest/v1/opcoes"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}


# =======================================================
# INSERIR OPERAÇÃO
# =======================================================

def inserir_operacao(dados: dict):
    """
    Insere operação de opções na tabela 'opcoes' do Supabase.
    Retorna o ID da operação.
    """
    url = REST_ENDPOINT

    resp = requests.post(
        url,
        headers=HEADERS,
        json=dados,
        params={"select": "id"},
        timeout=20
    )

    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list) and data:
        return data[0]["id"]

    return None


# =======================================================
# ATUALIZAR OPERAÇÃO (abertas / encerradas)
# =======================================================

def atualizar_operacao(op_id: str, dados: dict):
    url = REST_ENDPOINT
    params = {"id": f"eq.{op_id}"}

    resp = requests.patch(
        url,
        headers=HEADERS,
        params=params,
        json=dados,
        timeout=20
    )
    resp.raise_for_status()
    return True


# =======================================================
# CARREGAR OPERAÇÕES ABERTAS
# =======================================================

def carregar_abertas():
    params = {
        "select": "*",
        "status": "eq.aberta",
        "indice": "eq.OPCOES"
    }

    resp = requests.get(
        REST_ENDPOINT,
        headers=HEADERS,
        params=params,
        timeout=20
    )
    resp.raise_for_status()

    return resp.json()


# =======================================================
# CARREGAR OPERAÇÕES ENCERRADAS
# =======================================================

def carregar_encerradas():
    params = {
        "select": "*",
        "status": "eq.encerrada",
        "indice": "eq.OPCOES",
        "order": "created_at.desc"
    }

    resp = requests.get(
        REST_ENDPOINT,
        headers=HEADERS,
        params=params,
        timeout=20
    )
    resp.raise_for_status()

    return resp.json()


# =======================================================
# FUNÇÕES USADAS PELO SCANNER
# =======================================================

def _carregar_operacoes_abertas():
    """
    Compatível com Scanner29_11.py e scanner_opcoes.py
    """
    return carregar_abertas()


def _atualizar_operacao_supabase(op_id: str, dados: dict):
    dados["updated_at"] = datetime.utcnow().isoformat()
    return atualizar_operacao(op_id, dados)
