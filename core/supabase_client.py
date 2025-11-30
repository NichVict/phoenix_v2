import os
import streamlit as st
import requests

# ============================================================
# CONFIGURAÇÃO BÁSICA DO SUPABASE (REST API)
# ============================================================

@st.cache_resource
def get_supabase():
    """
    Retorna um objeto simples com funções REST
    compatíveis com o Supabase, sem depender do supabase-py.
    """

    url = st.secrets.get("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY não definidos no st.secrets.")

    # Pequena mini-API REST que devolvemos para o app
    class SupabaseREST:
        def __init__(self, url, key):
            self.url = url.rstrip("/")
            self.key = key

        def headers(self):
            return {
                "apikey": self.key,
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json",
            }

        # -------------------------
        # SELECT
        # -------------------------
        def select(self, table, query="*"):
            endpoint = f"{self.url}/rest/v1/{table}"
            params = {"select": query}
            r = requests.get(endpoint, headers=self.headers(), params=params)
            r.raise_for_status()
            return r.json()

        # -------------------------
        # INSERT
        # -------------------------
        def insert(self, table, data):
            endpoint = f"{self.url}/rest/v1/{table}"
            r = requests.post(endpoint, headers=self.headers(), json=data)
            r.raise_for_status()
            return r.json()

        # -------------------------
        # UPDATE
        # -------------------------
        def update(self, table, match, data):
            endpoint = f"{self.url}/rest/v1/{table}"
            r = requests.patch(
                endpoint, headers=self.headers(), params=match, json=data
            )
            r.raise_for_status()
            return r.json()

        # -------------------------
        # DELETE
        # -------------------------
        def delete(self, table, match):
            endpoint = f"{self.url}/rest/v1/{table}"
            r = requests.delete(
                endpoint, headers=self.headers(), params=match
            )
            r.raise_for_status()
            return r.json()

    return SupabaseREST(url, key)
