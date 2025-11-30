import streamlit as st
from core.db import get_logs

def render():
    st.title("📝 Logs do Sistema")
    logs = get_logs()
    st.dataframe(logs, use_container_width=True)
