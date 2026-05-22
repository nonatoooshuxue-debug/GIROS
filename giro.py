import streamlit as st
import pandas as pd
import pygsheets
from google.oauth2 import service_account

st.set_page_config(layout="wide")
@st.cache_data(ttl=30)
def giro():
    escopos = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    info_dict = {
        "type": st.secrets["giros"]["type"],
        "project_id": st.secrets["giros"]["project_id"],
        "private_key_id": st.secrets["giros"]["private_key_id"],
        "private_key": st.secrets["giros"]["private_key"].replace(
            "\\n", "\n"
        ),
        "client_email": st.secrets["giros"]["client_email"],
        "client_id": st.secrets["giros"]["client_id"],
        "auth_uri": st.secrets["giros"]["auth_uri"],
        "token_uri": st.secrets["giros"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["giros"][
            "auth_provider_x509_cert_url"
        ],
        "client_x509_cert_url": st.secrets["giros"]["client_x509_cert_url"],
        "universe_domain": st.secrets.get("giros", {}).get(
            "universe_domain", "googleapis.com"
        ),
    }

    creds = service_account.Credentials.from_service_account_info(
        info_dict, scopes=escopos
    )
    client = pygsheets.client.Client(creds)

    sheet_id = "1rr_3GJ6eg1Whd1NkdiHbObyhWD7L6Z7Bh2ZZ_UR8b1Q"

    abas = ["CAPITALI CRUZ", "CAPITALI ITAPIPOCA"]
    meu_dfs = {}

    try:
        arquivo = client.open_by_key(sheet_id)

        for nome_ab in abas:
            aba = arquivo.worksheet_by_title(nome_ab)

            df = aba.get_as_df()

            df.columns = df.columns.str.strip().str.upper()

            meu_dfs[nome_ab] = df

        return meu_dfs

    except Exception as e:
        st.error(f"Erro ao acessar a planilha no Google Drive: {e}")
        return None


meu_dfs = giro()
unidade = sorted(meu_dfs.keys())
# filtro por unidade
unidade_fil = st.sidebar.selectbox("Selecione a Unidade:", unidade)
df_geral = meu_dfs[unidade_fil]
# filtro por tipo de giro
inicio_mes = pd.to_numeric(df_geral["INICIO DO MÊS - HOJE"], errors="coerce").iloc[0]
# métricas
gv_ = sorted(df_geral["GV"].dropna().astype(str).unique())
gv_fil = st.sidebar.multiselect("GV:", options=gv_)
df_geral = df_geral[df_geral["GV"].astype(str).isin(gv_fil)]


metas_unidade = {"CAPITALI CRUZ": 30.0, "CAPITALI ITAPIPOCA": 66.0
                 }
metas_dinamicas = metas_unidade.get(unidade_fil, 30.0)
df_cal = df_geral.copy()
df_cal["QUANTIDADE"] = pd.to_numeric(df_cal["QUANTIDADE"], errors="coerce")
df_cal["QUANTIDADE"] = df_cal["QUANTIDADE"].fillna(0)
df_cal["TIPO GIRO MENSAL"] = df_cal["TIPO GIRO MENSAL"].astype(str).str.strip()
soma_ok = df_cal.loc[df_cal["TIPO GIRO MENSAL"] == "OK", "QUANTIDADE"].sum()
soma_quant = df_cal["QUANTIDADE"].sum()
resultado_parcial = (soma_ok / soma_quant * 100) if soma_quant > 0 else 0
tendencia = (resultado_parcial/inicio_mes)*31
delta_parcial =  metas_dinamicas - resultado_parcial
delta_tend=  tendencia - metas_dinamicas
distancia = resultado_parcial - metas_dinamicas


tipo_giro = sorted(df_geral["TIPO GIRO MENSAL"].dropna().astype(str).unique())
giro_fil = st.sidebar.multiselect("Selecione o Tipo de Giro:", options=tipo_giro)
df_geral2 = df_geral[df_geral["TIPO GIRO MENSAL"].astype(str).isin(giro_fil)]
# filtro por setor
rn = sorted(df_geral2["SETOR"].dropna().astype(str).unique())
rn_fil = st.sidebar.multiselect("Setor:", options=rn)
df_geral3 = df_geral2[df_geral2["SETOR"].astype(str).isin(rn_fil)]


st.subheader(f"Análise por GV: {gv_fil}")
             
colunas_alvo = ["CLIENTE", "NOME FANTASIA", "SETOR", "TIPO DE VASILHAME", "CAIXAS COMODATAS","GV", "CAIXAS COMODATADAS", "COMPROU", "FALTA COMPRAR", "META", "TENDÊNCIA"]
df_alvo = df_geral3[[c for c in colunas_alvo if c in df_geral3.columns]].copy()
col_real = next((c for c in df_alvo.columns if "TENDEN" in c), None)


col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Meta", value=f"{metas_dinamicas: .2f}%")
with col2:
    st.metric(label="Resultado Parcial", value=f"{resultado_parcial: .2f}%", delta=f"{distancia: .2f}%")
with col3:
    st.metric(label="Tendência", value=f"{tendencia: .2f}%", delta=f"{delta_tend: .2f}%")
st.divider()

st.subheader(f"Tipo de Giro: {giro_fil}")
st.dataframe(df_alvo, use_container_width=True)


