# notificacoes.py — Phoenix v2
# Módulo único para envio de mensagens (Telegram + Email)
# Usado por: Scanner de Opções, Scanner de Ações, Carteiras, Robôs, CRM…

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ======================================================
# 🔧 Carregar secrets automaticamente
# ======================================================
def _get_secret(name, default=None):
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except:
        pass
    return os.getenv(name, default)


# ======================================================
# 🔥 Telegram Config
# ======================================================
TELEGRAM_TOKEN = _get_secret("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN não configurado nos secrets.")


# ======================================================
# 🟦 IDs dos grupos / carteiras
# ======================================================
GROUP_CHAT_IDS = {
    "Carteira de Ações IBOV": -1002198655576,
    "Carteira de Small Caps": -1003251673981,
    "Carteira de BDRs":       -1002171530332,
    "Carteira de Opções":     -1003274356400,
}

# Default: enviar para grupo de opções (mais usado por robôs)
DEFAULT_CHAT_ID = GROUP_CHAT_IDS["Carteira de Opções"]


# ======================================================
# 📤 Função para enviar Telegram
# ======================================================
def enviar_telegram(mensagem: str, chat_id: int = None):
    """
    Envia mensagem HTML para qualquer chat_id.
    Se chat_id for None → usa grupo padrão de Opções.
    """
    if chat_id is None:
        chat_id = DEFAULT_CHAT_ID

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": mensagem,
        "parse_mode": "HTML"
    }

    r = requests.post(url, json=payload, timeout=15)

    if r.status_code not in (200, 201):
        raise RuntimeError(f"Erro ao enviar Telegram: {r.text}")

    return True


# ======================================================
# 💌 Funções de EMAIL (caso queira ativar)
# ======================================================
EMAIL_HOST = _get_secret("EMAIL_HOST")
EMAIL_PORT = int(_get_secret("EMAIL_PORT", 587))
EMAIL_USER = _get_secret("EMAIL_USER")
EMAIL_PASS = _get_secret("EMAIL_PASS")


def email_configurado() -> bool:
    return all([EMAIL_HOST, EMAIL_USER, EMAIL_PASS])


def enviar_email(assunto: str, corpo_html: str, destinatario: str = None):
    """
    Envia email com HTML.
    Se destinatário não for passado → envia para EMAIL_USER.
    """
    if not email_configurado():
        raise RuntimeError("Email não configurado nos secrets.")

    if destinatario is None:
        destinatario = EMAIL_USER

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario

    msg.attach(MIMEText(corpo_html, "html"))

    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, destinatario, msg.as_string())
    server.quit()

    return True
