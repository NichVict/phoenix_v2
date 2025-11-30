import os
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ============================================================
# CONFIGURAÇÕES GERAIS / SECRETS
# ============================================================

def _get_secret(name: str, default=None):
    """
    Prioriza st.secrets; em dev local usa variável de ambiente.
    NÃO dá st.stop() aqui para não quebrar o import em outras páginas.
    """
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name, default)


SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")

EMAIL_USER = _get_secret("email_sender")
EMAIL_PASS = _get_secret("gmail_app_password")
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

_supabase_client: Optional[Client] = None


def get_supabase() -> Optional[Client]:
    """Lazy init do client Supabase – não quebra o app se faltar config."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    try:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Falha ao inicializar Supabase no módulo admin.users: {e}")
        _supabase_client = None
    return _supabase_client


# ============================================================
# CONSTANTES / CONFIG DO CRM
# ============================================================

PAISES = {
    "🇧🇷 Brasil (+55)": "+55",
    "🇵🇹 Portugal (+351)": "+351",
    "🇺🇸 EUA (+1)": "+1",
    "🇪🇸 Espanha (+34)": "+34",
    "🌍 Outro": ""
}

# Novo padrão de carteiras Phoenix
CARTEIRAS_OPCOES = [
    "Carteira de Ações IBOV",
    "Carteira de BDRs",
    "Carteira de Opções",
    "Leads",
    "Estratégias Phoenix",
]

PAGAMENTOS = ["PIX", "PAYPAL", "Infinite"]

# ============================ LINKS GOOGLE GROUPS ============================
DASHBOARD_LINK = "https://fenixproject.streamlit.app/Dashboard"
LINK_GG_ACOES  = "https://groups.google.com/g/estrategias-phoenix"
LINK_GG_BDRS   = "https://groups.google.com/g/estrategiasbdr-phoenix"
LINK_GG_OPCOES = "https://groups.google.com/g/estrategiasopcoes-phoenix"

# ============================ BOTÕES EMAIL ============================
def _botao_google(texto: str, link: str) -> str:
    return f'''
<p style="text-align:left;margin:10px 0 18px;">
  <a href="{link}" target="_blank" style="
    border:2px solid #25D366;
    color:#25D366;
    padding:12px 20px;
    border-radius:8px;
    text-decoration:none;
    font-weight:700;
    display:inline-block;">
    {texto}
  </a>
</p>
'''


def _botao_telegram(texto: str, link: str) -> str:
    return f'''
<p style="text-align:left;margin:10px 0 18px;">
  <a href="{link}" target="_blank" style="
    border:2px solid #7D3C98;
    color:#7D3C98;
    padding:12px 20px;
    border-radius:8px;
    text-decoration:none;
    font-weight:700;
    display:inline-block;">
    {texto}
  </a>
</p>
'''


WHATSAPP_BTN = """
<p style="text-align:left;margin-top:18px;">
  <a href="https://wa.me/351915323219" target="_blank" style="
    background-color:#25D366;
    color:white;
    padding:12px 20px;
    border-radius:8px;
    text-decoration:none;
    font-weight:600;
    display:inline-block;">
    💬 Falar com Suporte
  </a>
</p>
"""

AULAS_TXT_HTML = """
<!--
Bloco de aulas pode ser habilitado depois se quiser.
-->
"""

# ============================ TEMPLATES DE EMAIL POR CARTEIRA ============================

EMAIL_CORPOS = {
    "Carteira de Ações IBOV": f"""
<h2>📈 Olá {{nome}}!</h2>
<p>Bem-vindo(a) à <b>Carteira de Ações IBOV — Projeto Phoenix</b>.</p>

<p><b>Período da assinatura:</b> {{inicio}} a {{fim}}</p>

<h3>🔥 O que você recebe</h3>
<ul>
  <li><b>Análises automatizadas</b> com algoritmos proprietários</li>
  <li><b>Alertas automáticos</b> de entrada, saída e gestão</li>
  <li><b>Métricas exclusivas Phoenix</b> (momentum, volatilidade, força setorial, score Phoenix)</li>
  <li><b>Dashboard exclusivo</b> para acompanhamento:
    <br><a href="{DASHBOARD_LINK}" target="_blank">{DASHBOARD_LINK}</a>
  </li>
  <li><b>StopATR inteligente</b>: ajusta stops dinamicamente conforme volatilidade</li>
</ul>

<h3>🚀 Próximos passos</h3>
<ol>
  <li>Leia o documento anexo e responda <b>ACEITE</b></li>
  <li>Acesse o Grupo Google e valide sua entrada</li>
  <li>Entre no canal do Telegram (link personalizado)</li>
</ol>

{_botao_google("Entrar no Grupo Google", LINK_GG_ACOES)}

<hr>

<p>
O Projeto Phoenix é construído sobre automação, disciplina e métricas inteligentes.<br>
Conte conosco para elevar seu nível como investidor(a)!
</p>

{AULAS_TXT_HTML}
{WHATSAPP_BTN}
""",
    "Carteira de BDRs": f"""
<h2>🌎 Olá {{nome}}!</h2>
<p>Você agora faz parte da <b>Carteira de BDRs — Projeto Phoenix</b>.</p>

<p><b>Período da assinatura:</b> {{inicio}} a {{fim}}</p>

<h3>🔥 O que você recebe</h3>
<ul>
  <li><b>Análises automatizadas</b> com enfoque internacional</li>
  <li><b>Alertas automáticos</b> de compra, venda e risco</li>
  <li><b>Métricas Phoenix</b> aplicadas a BDRs (momentum global, volatilidade, força setorial)</li>
  <li><b>Dashboard exclusivo</b> para acompanhamento:
    <br><a href="{DASHBOARD_LINK}" target="_blank">{DASHBOARD_LINK}</a>
  </li>
  <li><b>StopATR automático</b> ajustado ao comportamento dos ativos globais</li>
</ul>

<h3>🚀 Próximos passos</h3>
<ol>
  <li>Leia o documento em anexo e responda <b>ACEITE</b></li>
  <li>Entre no Grupo Google da carteira</li>
  <li>Entre no canal do Telegram (link personalizado)</li>
</ol>

{_botao_google("Entrar no Grupo Google", LINK_GG_BDRS)}

<hr>

<p>
Estamos juntos dentro do ecossistema Phoenix — tecnologia, análise e execução com precisão.
</p>

{AULAS_TXT_HTML}
{WHATSAPP_BTN}
""",
    "Carteira de Opções": f"""
<h2>🔥 Olá {{nome}}!</h2>
<p>Seja bem-vindo(a) à <b>Carteira de Opções — Projeto Phoenix</b>.</p>

<p><b>Período da assinatura:</b> {{inicio}} a {{fim}}</p>

<h3>🔥 O que você recebe</h3>
<ul>
  <li><b>Operações estruturadas</b> com critérios objetivos</li>
  <li><b>Alertas automáticos</b> com ticker, strike, vencimento e preço</li>
  <li><b>Sistema Phoenix</b> com métricas exclusivas (IV, volatilidade, posição dos players, momentum)</li>
  <li><b>Atualizações contínuas</b> de gestão e ajustes</li>
  <li><b>StopATR inteligente</b> para proteção dinâmica</li>
</ul>

<h3>📌 Importante</h3>
<p>
Opções possuem maior volatilidade — siga os alertas do Phoenix para não perder o timing.
</p>

<h3>🚀 Próximos passos</h3>
<ol>
  <li>Leia o documento em anexo e responda <b>ACEITE</b></li>
  <li>Valide sua entrada no Grupo Google</li>
  <li>Acesse o canal do Telegram (link abaixo)</li>
</ol>

{_botao_google("Entrar no Grupo Google", LINK_GG_OPCOES)}

<hr>

<p>
Vamos buscar precisão, gestão e estratégia — pilares que definem o Projeto Phoenix.
</p>

{AULAS_TXT_HTML}
{WHATSAPP_BTN}
""",
}

# ============================ EMAILS DE RENOVAÇÃO ============================

EMAIL_RENOVACAO_30 = f"""
<h2>⚠️ Sua assinatura está a 30 dias do vencimento, {{nome}}</h2>

<p>Sua carteira <b>{{carteira}}</b> do Projeto Phoenix está próxima de vencer.</p>

<p><b>Período atual:</b> {{inicio}} → {{fim}}</p>

<p>Para manter acesso às análises automatizadas, alertas e métricas Phoenix, responda:</p>

<p><b>RENOVAR</b></p>

{WHATSAPP_BTN}

<p>Equipe Phoenix 💚</p>
"""

EMAIL_RENOVACAO_15 = f"""
<h2>📈 Renovação — faltam 15 dias</h2>

<p>Olá {{nome}}, sua assinatura da carteira <b>{{carteira}}</b> está próxima do vencimento.</p>

<p><b>Período atual:</b> {{inicio}} → {{fim}}</p>

<p>Deseja renovar? Basta responder este e-mail com:</p>

<p><b>Quero renovar</b></p>

{WHATSAPP_BTN}
"""

EMAIL_RENOVACAO_7 = f"""
<h2>⏳ Atenção — sua assinatura vence em 7 dias</h2>

<p>{{nome}}, sua carteira <b>{{carteira}}</b> está quase no fim.</p>

<p><b>Período atual:</b> {{inicio}} → {{fim}}</p>

<p>Responda <b>RENOVAR</b> para não perder o acesso ao Phoenix.</p>

{WHATSAPP_BTN}

<p>Obrigado pela confiança! 💪</p>
"""


# ============================================================
# FUNÇÕES AUXILIARES (COMPARTILHADAS)
# ============================================================

def _format_date_br(d: date) -> str:
    try:
        return d.strftime("%d/%m/%Y")
    except Exception:
        try:
            return pd.to_datetime(d).strftime("%d/%m/%Y")
        except Exception:
            return str(d)


def _montar_telefone(cod: str, numero: str) -> str:
    numero = (numero or "").strip()
    cod = (cod or "").strip()
    if cod and not numero.startswith(cod):
        return f"{cod} {numero}"
    return numero


def _status_cor_data_fim(data_fim: date) -> str:
    """
    - vermelho: data atual > data_fim
    - amarelo: faltam <= 30 dias
    - verde: faltam > 30 dias
    """
    hoje = date.today()
    if not data_fim:
        return "background-color: lightgray"
    if data_fim < hoje:
        return "background-color: #ff4d4f; color:white;"
    dias = (data_fim - hoje).days
    if dias <= 30:
        return "background-color: #faad14; color:black;"
    return "background-color: #52c41a; color:white;"


def _carteiras_to_list(v) -> List[str]:
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        v = v.replace("[", "").replace("]", "").replace("'", '"')
        parts = [p.strip().strip('"') for p in v.split(",") if p.strip()]
        return parts
    if v is None:
        return []
    return [str(v)]


# ============================================================
# SUPABASE HELPERS – USO EM OUTROS MÓDULOS (DASHBOARD ADMIN)
# ============================================================

def list_users() -> List[Dict[str, Any]]:
    """
    Retorna lista de clientes (dicts) do Supabase.
    Usado pelo painel admin para contagem rápida.
    """
    sb = get_supabase()
    if not sb:
        return []
    try:
        resp = sb.table("clientes").select("*").execute()
        return resp.data or []
    except Exception:
        return []


def _users_df() -> pd.DataFrame:
    data = list_users()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if "data_fim" in df.columns:
        df["data_fim"] = pd.to_datetime(df["data_fim"], errors="coerce").dt.date
    df["carteiras"] = df["carteiras"].apply(_carteiras_to_list)
    return df


def count_active_users() -> int:
    df = _users_df()
    if df.empty:
        return 0
    today = date.today()
    clientes = df[df["carteiras"].apply(lambda x: "Leads" not in x)]
    ativos = clientes[clientes["data_fim"] >= today]
    return int(len(ativos))


def count_expired_users() -> int:
    df = _users_df()
    if df.empty:
        return 0
    today = date.today()
    clientes = df[df["carteiras"].apply(lambda x: "Leads" not in x)]
    vencidos = clientes[clientes["data_fim"] < today]
    return int(len(vencidos))


# ============================================================
# ENVIO DE EMAILS (BOAS-VINDAS + RENOVAÇÃO)
# ============================================================
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import smtplib


def _enviar_email(
    nome: str,
    email_destino: str,
    assunto: str,
    corpo: str,
    anexar_pdf: bool = False,
) -> tuple[bool, str]:
    if not EMAIL_USER or not EMAIL_PASS:
        return False, "Configuração de e-mail ausente."

    try:
        msg = MIMEMultipart()
        msg["Subject"] = assunto
        msg["From"] = EMAIL_USER
        msg["To"] = email_destino

        msg.attach(MIMEText(corpo, "html", "utf-8"))

        if anexar_pdf:
            try:
                with open("contrato_Aurinvest.pdf", "rb") as f:
                    part = MIMEApplication(f.read(), _subtype="pdf")
                    part.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename="Contrato_Aurinvest.pdf",
                    )
                    msg.attach(part)
            except Exception as e:
                # Não quebra se faltar o PDF; apenas informa
                return False, f"Falha ao anexar contrato: {e}"

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, [email_destino], msg.as_string())
        server.quit()
        return True, "OK"
    except Exception as e:
        return False, str(e)


def enviar_emails_por_carteira(
    nome: str,
    email_destino: str,
    carteiras: list,
    inicio: date,
    fim: date,
    cliente_id: Optional[str] = None,
):
    resultados = []
    inicio_br = _format_date_br(inicio)
    fim_br = _format_date_br(fim)

    telegram_link = None
    if cliente_id:
        # Bot Phoenix CRM (ajuste se mudar o username do bot)
        telegram_link = f"https://t.me/milhao_crm_bot?start={cliente_id}"

    for c in carteiras:
        corpo = EMAIL_CORPOS.get(c, "")
        if not corpo:
            resultados.append((c, False, "Sem template configurado"))
            continue

        corpo = corpo.format(nome=nome, inicio=inicio_br, fim=fim_br)

        botao_telegram_html = ""
        if telegram_link:
            botao_telegram_html = _botao_telegram("Entrar no Telegram", telegram_link)

        anchor = "<hr>"
        if anchor in corpo:
            partes = corpo.split(anchor)
            corpo = partes[0] + botao_telegram_html + anchor + partes[1]
        else:
            corpo += botao_telegram_html

        # Regra: anexa contrato para todas as carteiras exceto Leads
        anexar_pdf = c != "Leads"
        assunto = f"Bem-vindo(a) — {c}"

        ok, msg = _enviar_email(nome, email_destino, assunto, corpo, anexar_pdf)
        resultados.append((c, ok, msg))

    return resultados


def enviar_email_renovacao(
    nome: str,
    email_destino: str,
    carteira: str,
    inicio: date,
    fim: date,
    dias: int,
):
    inicio_br = _format_date_br(inicio)
    fim_br = _format_date_br(fim)

    mapping = {30: EMAIL_RENOVACAO_30, 15: EMAIL_RENOVACAO_15, 7: EMAIL_RENOVACAO_7}
    corpo_tpl = mapping.get(dias)
    if not corpo_tpl:
        return False, "Template não encontrado"

    corpo = corpo_tpl.format(
        nome=nome, carteira=carteira, inicio=inicio_br, fim=fim_br
    )
    assunto = f"Renovação — {carteira} ({dias} dias)"

    return _enviar_email(nome, email_destino, assunto, corpo, anexar_pdf=False)


# ============================================================
# UI PRINCIPAL – PÁGINA "👤 Gerenciar Clientes"
# ============================================================

# CSS de cards Phoenix
st.markdown(
    """
<style>
.card-kpi {
    background: radial-gradient(circle at top, rgba(0,255,180,0.28), #121212);
    border: 1px solid rgba(0,255,180,0.35);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    transition: 0.25s ease;
    box-shadow: 0 0 14px rgba(0,255,180,0.20);
}
.card-kpi:hover {
    transform: translateY(-3px);
    box-shadow: 0 0 20px rgba(0,255,200,0.35);
}
.card-kpi h3 {
    font-size: 32px;
    margin: 0;
    color: #00E6A8;
    font-weight: 700;
}
.card-kpi p {
    margin: 6px 0 0;
    font-size: 14px;
    color: #e0e0e0;
}
.badge-tag {
    display:inline-block;
    padding:2px 8px;
    border-radius:999px;
    font-size:11px;
    margin:0 3px 3px 0;
    border:1px solid rgba(0,255,180,0.45);
    color:#bfffea;
}
</style>
""",
    unsafe_allow_html=True,
)


def _disparar_renovacoes_automaticas(dados: List[Dict[str, Any]]):
    """
    Faz o disparo automático de e-mails de renovação
    dentro da própria página, sem thread separada.
    """
    sb = get_supabase()
    if not sb or not dados:
        return

    today = date.today()
    avisos = {30: "aviso_30", 15: "aviso_15", 7: "aviso_7"}

    for cli in dados:
        try:
            fim = pd.to_datetime(cli.get("data_fim")).date()
        except Exception:
            continue

        dias = (fim - today).days
        if dias not in avisos:
            continue

        campo_flag = avisos[dias]
        if cli.get(campo_flag, False):
            continue  # já avisado

        carteiras = cli.get("carteiras", [])
        if isinstance(carteiras, str):
            carteiras = _carteiras_to_list(carteiras)

        # Leads não recebem aviso
        if "Leads" in carteiras:
            continue

        for cart in carteiras:
            ok, _ = enviar_email_renovacao(
                nome=cli["nome"],
                email_destino=cli["email"],
                carteira=cart,
                inicio=pd.to_datetime(cli["data_inicio"]).date(),
                fim=fim,
                dias=dias,
            )
            # se pelo menos 1 email enviado, marca flag
            if ok:
                try:
                    sb.table("clientes").update({campo_flag: True}).eq(
                        "id", cli["id"]
                    ).execute()
                except Exception:
                    pass


def render():
    """
    Entry point da página de CRM dentro do Phoenix v2.
    Chamado pelo roteador admin (ex.: admin/dashboard chamando st.page_link).
    """
    sb = get_supabase()
    if not sb:
        st.error("Configuração do Supabase ausente. Defina SUPABASE_URL e SUPABASE_KEY.")
        return

    st.title("👤 Gestão de Clientes — Phoenix CRM")
    st.caption("Cadastro, vigência, comunicação e automações do Projeto Phoenix.")

    # ==============================
    # 1) CARREGAR DADOS
    # ==============================
    try:
        query = sb.table("clientes").select("*").order("created_at", desc=True).execute()
        dados = query.data or []
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {e}")
        dados = []

    df_kpi = pd.DataFrame(dados) if dados else pd.DataFrame()

    if not df_kpi.empty and "data_fim" in df_kpi.columns:
        df_kpi["data_fim"] = pd.to_datetime(df_kpi["data_fim"], errors="coerce").dt.date
        df_kpi["carteiras"] = df_kpi["carteiras"].apply(_carteiras_to_list)
        today = date.today()

        leads_df = df_kpi[df_kpi["carteiras"].apply(lambda x: "Leads" in x)]
        clientes_df = df_kpi[df_kpi["carteiras"].apply(lambda x: "Leads" not in x)]

        ativos_df = clientes_df[clientes_df["data_fim"] >= today]
        vencendo_df = clientes_df[
            (clientes_df["data_fim"] >= today)
            & (clientes_df["data_fim"] <= today + timedelta(days=30))
        ]
        vencidos_df = clientes_df[clientes_df["data_fim"] < today]
    else:
        leads_df = ativos_df = vencendo_df = vencidos_df = pd.DataFrame()

    # ==============================
    # 2) CARDS KPI
    # ==============================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"<div class='card-kpi'><h3>🟢 {len(ativos_df)}</h3><p>Clientes Ativos</p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='card-kpi'><h3>🟡 {len(vencendo_df)}</h3><p>≤ 30 dias para vencer</p></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='card-kpi'><h3>🔴 {len(vencidos_df)}</h3><p>Vencidos</p></div>",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"<div class='card-kpi'><h3>⚪ {len(leads_df)}</h3><p>Leads</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Dispara renovação automática (não bloqueia a UI)
    if dados:
        _disparar_renovacoes_automaticas(dados)

    # ==============================
    # 3) FORMULÁRIO DE CADASTRO/EDIÇÃO
    # ==============================
    st.markdown(
        "<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(0,255,180,0.35),transparent);'></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🆕 Cadastro e Edição de Clientes")

    is_edit = st.session_state.get("edit_mode", False)
    edit_data = st.session_state.get("edit_data") or {}

    with st.expander("Formulário", expanded=is_edit):
        with st.form("form_cadastro", clear_on_submit=not is_edit):

            c1, c2 = st.columns([2, 2])
            with c1:
                nome = st.text_input(
                    "Nome Completo",
                    value=edit_data.get("nome", ""),
                    placeholder="Ex.: Maria Silva",
                )
            with c2:
                email = st.text_input(
                    "Email",
                    value=edit_data.get("email", ""),
                    placeholder="exemplo@dominio.com",
                )

            c3, c4, c5 = st.columns([1.2, 1.2, 1.6])
            with c3:
                pais_label = st.selectbox(
                    "País (bandeira + código)",
                    options=list(PAISES.keys()),
                    index=0,
                )
            with c4:
                numero = st.text_input(
                    "Telefone",
                    value=edit_data.get("telefone", ""),
                    placeholder="(00) 00000-0000",
                )
            with c5:
                raw_carteiras = edit_data.get("carteiras", [])
                carteiras_val = _carteiras_to_list(raw_carteiras)
                # garante que só valores válidos entrem
                carteiras_val = [c for c in carteiras_val if c in CARTEIRAS_OPCOES]

                carteiras = st.multiselect(
                    "Carteiras", CARTEIRAS_OPCOES, default=carteiras_val
                )

            c6, c7, c8 = st.columns([1, 1, 1])
            with c6:
                inicio_default = edit_data.get("data_inicio", date.today())
                inicio = st.date_input(
                    "Início da Vigência",
                    value=inicio_default,
                    format="DD/MM/YYYY",
                )
            with c7:
                fim_default = edit_data.get(
                    "data_fim", date.today() + timedelta(days=180)
                )
                fim = st.date_input(
                    "Final da Vigência",
                    value=fim_default,
                    format="DD/MM/YYYY",
                )
            with c8:
                pagamento_index = 0
                if is_edit and edit_data.get("pagamento") in PAGAMENTOS:
                    pagamento_index = PAGAMENTOS.index(edit_data["pagamento"])
                pagamento = st.selectbox(
                    "Forma de Pagamento",
                    PAGAMENTOS,
                    index=pagamento_index,
                )

            c9, c10 = st.columns([1, 2])
            with c9:
                valor = st.number_input(
                    "Valor líquido",
                    min_value=0.0,
                    value=float(edit_data.get("valor", 0)),
                    step=100.0,
                    format="%.2f",
                )
            with c10:
                observacao = st.text_area(
                    "Observação (opcional)",
                    value=edit_data.get("observacao", ""),
                    placeholder="Notas internas...",
                )

            salvar = st.form_submit_button("Salvar", use_container_width=True)

        if salvar:
            telefone = _montar_telefone(PAISES.get(pais_label, ""), numero)
            if not nome or not email:
                st.error("Preencha ao menos **Nome Completo** e **Email**.")
            else:
                payload = {
                    "nome": nome,
                    "telefone": telefone,
                    "email": email,
                    "carteiras": list(carteiras) if carteiras else [],
                    "data_inicio": str(inicio),
                    "data_fim": str(fim),
                    "pagamento": pagamento,
                    "valor": float(valor),
                    "observacao": observacao or None,
                }

                # UPDATE
                if is_edit:
                    try:
                        edit_id = str(st.session_state.get("selected_client_id"))
                        sb.table("clientes").update(payload).eq("id", edit_id).execute()

                        telegram_link = f"https://t.me/milhao_crm_bot?start={edit_id}"

                        st.session_state["last_cadastro"] = {
                            "id": edit_id,
                            "nome": nome,
                            "email": email,
                            "carteiras": payload.get("carteiras", []),
                            "inicio": inicio,
                            "fim": fim,
                            "telegram_link": telegram_link,
                        }

                        st.success("✅ Cliente atualizado com sucesso!")
                        st.session_state["edit_mode"] = False
                        st.session_state["edit_id"] = None
                        st.session_state["edit_data"] = None
                        st.session_state["selected_client_id"] = None
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao atualizar: {e}")

                # INSERT
                else:
                    try:
                        res = sb.table("clientes").insert(payload).execute()
                        cliente_id = res.data[0]["id"]
                        telegram_link = (
                            f"https://t.me/milhao_crm_bot?start={cliente_id}"
                        )

                        st.success("✅ Cliente cadastrado com sucesso!")

                        st.session_state["last_cadastro"] = {
                            "id": cliente_id,
                            "nome": nome,
                            "email": email,
                            "carteiras": list(carteiras) if carteiras else [],
                            "inicio": inicio,
                            "fim": fim,
                            "telegram_link": telegram_link,
                        }
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao salvar no Supabase: {e}")

    # ==============================
    # 4) AÇÃO: ENVIAR PACK DE BOAS-VINDAS
    # ==============================
    if "last_cadastro" in st.session_state and st.session_state["last_cadastro"]:
        lc = st.session_state["last_cadastro"]
        lista = (
            ", ".join(lc.get("carteiras", []))
            if lc.get("carteiras")
            else "Nenhuma carteira selecionada"
        )
        st.info(
            f"Enviar e-mail de boas-vindas para **{lc['email']}** — carteiras: **{lista}**?"
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button(
                "✉️ Enviar e-mails com Pack boas-vindas",
                use_container_width=True,
            ):
                if not lc.get("carteiras"):
                    st.warning("Nenhuma carteira selecionada. Nada foi enviado.")
                else:
                    resultados = enviar_emails_por_carteira(
                        nome=lc["nome"],
                        email_destino=lc["email"],
                        carteiras=lc["carteiras"],
                        inicio=lc["inicio"],
                        fim=lc["fim"],
                        cliente_id=lc["id"],
                    )
                    ok_all = True
                    for carteira, ok, msg in resultados:
                        if ok:
                            st.success(f"✅ {carteira}: enviado")
                        else:
                            ok_all = False
                            st.error(f"❌ {carteira}: falhou — {msg}")
                    if ok_all:
                        st.toast(
                            "Todos os e-mails foram enviados com sucesso.", icon="✅"
                        )
                st.session_state["last_cadastro"] = None
        with c2:
            if st.button("❌ Não enviar e-mails", use_container_width=True):
                st.session_state["last_cadastro"] = None
                st.toast("Cadastro concluído sem envio de e-mails.", icon="✅")

    # ==============================
    # 5) LISTAGEM / TABELA
    # ==============================
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(0,255,180,0.35),transparent);'></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("🧑‍🤝‍🧑 Clientes Cadastrados")
    st.markdown("<br>", unsafe_allow_html=True)

    # Filtros básicos
    nome_filtro = st.text_input("Filtrar por nome/email", "")
    carteira_filtro = st.multiselect("Filtrar por carteira", CARTEIRAS_OPCOES)
    status_filtro = st.multiselect(
        "Status de vigência",
        ["Ativo", "Vencendo ≤ 30d", "Vencido", "Lead"],
    )

    df_list = pd.DataFrame(dados) if dados else pd.DataFrame()
    if df_list.empty:
        st.info("Nenhum cliente encontrado.")
        return

    df_list["data_inicio"] = pd.to_datetime(
        df_list["data_inicio"], errors="coerce"
    ).dt.date
    df_list["data_fim"] = pd.to_datetime(
        df_list["data_fim"], errors="coerce"
    ).dt.date
    df_list["carteiras"] = df_list["carteiras"].apply(_carteiras_to_list)

    today = date.today()

    def class_status(row):
        c = row["carteiras"]
        if "Leads" in c:
            return "Lead"
        if row["data_fim"] < today:
            return "Vencido"
        dias = (row["data_fim"] - today).days
        if dias <= 30:
            return "Vencendo ≤ 30d"
        return "Ativo"

    df_list["status"] = df_list.apply(class_status, axis=1)

    # Aplica filtros
    if nome_filtro:
        nf = nome_filtro.lower()
        df_list = df_list[
            df_list["nome"].str.lower().str.contains(nf)
            | df_list["email"].str.lower().str.contains(nf)
        ]

    if carteira_filtro:
        df_list = df_list[
            df_list["carteiras"].apply(
                lambda cs: any(c in cs for c in carteira_filtro)
            )
        ]

    if status_filtro:
        df_list = df_list[df_list["status"].isin(status_filtro)]

    if df_list.empty:
        st.warning("Nenhum cliente encontrado com os filtros aplicados.")
        return

    # Exibição com botões de ação
    for _, row in df_list.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(
                    f"**{row['nome']}**  \n"
                    f"{row['email']}  \n"
                    f"📞 {row.get('telefone', '')}"
                )
                carteiras_html = "".join(
                    f"<span class='badge-tag'>{c}</span>"
                    for c in row["carteiras"]
                )
                st.markdown(
                    f"Carteiras: {carteiras_html}",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"Vigência: **{_format_date_br(row['data_inicio'])} → {_format_date_br(row['data_fim'])}**"
                )
                st.markdown(f"Status: **{row['status']}**")
                if row.get("observacao"):
                    st.caption(f"📝 {row['observacao']}")
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✏️ Editar", key=f"edit_{row['id']}"):
                    st.session_state["edit_mode"] = True
                    st.session_state["edit_data"] = dict(row)
                    st.session_state["selected_client_id"] = row["id"]
                    st.experimental_rerun()

                if st.button("🗑️ Excluir", key=f"del_{row['id']}"):
                    try:
                        sb.table("clientes").delete().eq("id", row["id"]).execute()
                        st.success("Cliente removido.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
