import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# Layout full-width
st.set_page_config(page_title="Registro de Entregas", layout="wide")

# Botão no cabeçalho
col1, col2 = st.columns([9, 1])
with col1:
    st.title("📝 Registro de Entregas")
with col2:
    st.markdown(
        """<a href="https://docs.google.com/spreadsheets/d/1_4f0JIGKFQ7sJz00ESkuhFXbZaV4hByYfHitbtAmcwQ/edit#gid=0"
             target="_blank"
             style="background-color:#4285F4;color:white;padding:8px 12px;
                    border-radius:4px;text-decoration:none;font-weight:bold;">
            📒 Abrir Planilha
        </a>""",
        unsafe_allow_html=True,
    )

# Autenticação via variável de ambiente
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
try:
    creds_json = os.environ["GOOGLE_CREDENTIALS"]
except KeyError:
    st.error(
        "❌ Variável de ambiente GOOGLE_CREDENTIALS não definida.\n\n"
        "1. Abra as Settings → Secrets do seu repositório no GitHub.\n"
        "2. Crie um secret chamado GOOGLE_CREDENTIALS com o JSON da conta de serviço.\n"
        "3. No seu ambiente local, exporte:\n"
        "   export GOOGLE_CREDENTIALS='{\"type\":\"service_account\",...}'\n"
    )
    st.stop()

creds_json = st.secrets["GOOGLE_CREDENTIALS"]
st.write("DEBUG: length of secret =", len(creds_json))
# se quiser ver o começo:
st.write("DEBUG: first 200 chars:", repr(creds_json[:200]))
info = json.loads(creds_json)
info = json.loads(creds_json)
creds = Credentials.from_service_account_info(info, scopes=SCOPES)
client = gspread.authorize(creds)

# Abre a planilha
SHEET_ID = "1_4f0JIGKFQ7sJz00ESkuhFXbZaV4hByYfHitbtAmcwQ"
try:
    sheet = client.open_by_key(SHEET_ID).sheet1
except Exception:
    st.error("❌ Não foi possível abrir a planilha. Verifique o ID e o compartilhamento.")
    st.stop()

# Gerenciamento de cabeçalho
header = ["Data", "Entrega", "Trabalho Realizado", "Resumo para o Petrvs", "Preenchido por"]
first = sheet.row_values(1)
if first != header:
    sheet.insert_row(header, index=1, value_input_option="USER_ENTERED")
sheet.format("1:1", {"textFormat": {"bold": True}})
try:
    if sheet.row_values(2) == header:
        sheet.delete_rows(2)
except:
    pass

# Inputs do usuário
USUARIOS = ["Selecione o nome do preenchedor", "Antônio Azambuja", "Pedro Reckziegel", "Ricardo Zomer", "Tólio Ribeiro"]
usuario = st.selectbox("Quem está preenchendo?", USUARIOS)
data_atividade = st.date_input("Data da atividade", format="DD/MM/YYYY")
ENTREGAS = [
    "Pleitos de alteração tarifária e alteração de NCM/TEC",
    "Análise de Projetos de Lei e proposições normativas",
    "Acompanhamento da política de depreciação acelerada",
    "Subsídios para participação de autoridades em audiências e eventos",
    "Desenvolvimento e revisão de códigos (Python, R, Power BI)",
    "Análise de demandas atribuídas à CGIM",
    "Subsídios e análises para a ASINT",
]
entrega = st.selectbox("Tipo de Entrega", ENTREGAS)
atividade = st.text_area("Trabalho Realizado")

# Função de gravação
def salvar(data, tipo, texto, quem):
    full = data.strftime("%d/%m/%Y")
    short = data.strftime("%d/%m")
    resumo = f"{short} - {texto}"
    sheet.append_row([full, tipo, texto, resumo, quem], value_input_option="USER_ENTERED")

if st.button("Salvar Registro"):
    if usuario == USUARIOS[0]:
        st.error("Selecione o nome do preenchedor.")
    elif not atividade.strip():
        st.error("Descreva o trabalho realizado.")
    else:
        salvar(data_atividade, entrega, atividade, usuario)
        st.success("✅ Registro salvo com sucesso!")
        st.experimental_rerun()

# Exibição e edição
st.subheader("Registros Recentes")
records = sheet.get_all_records()
df = pd.DataFrame(records)
if df.empty:
    st.info("Ainda não há registros.")
else:
    df = df[header]
    edited_df = st.data_editor(df, hide_index=True, use_container_width=True)
    if st.button("Atualizar Planilha com Edições"):
        sheet.resize(rows=1)
        if not edited_df.empty:
            sheet.append_rows(edited_df.values.tolist(), value_input_option="USER_ENTERED")
        st.success("Planilha atualizada com as edições!")
        st.experimental_rerun()








