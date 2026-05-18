import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
@st.cache_data()
def giro():
    planilha = "GIROS COMODATOS.xlsx"
    abas = ["CAPITALI CRUZ","CAPITALI ITAPIPOCA"]
    meu_dfs = {}
    for nome_ab in abas:
     df = pd.read_excel(planilha, sheet_name=nome_ab)
     df.columns = df.columns.str.strip().str.upper()
     meu_dfs[nome_ab] = df

    return meu_dfs


meu_dfs = giro()
unidade = sorted(meu_dfs.keys())
# filtro por unidade
unidade_fil = st.sidebar.selectbox("Selecione a Unidade:", unidade)
df_geral = meu_dfs[unidade_fil]
# filtro por tipo de giro
inicio_mes = pd.to_numeric(df_geral["INICIO DO MÊS - HOJE"], errors="coerce").iloc[0]
# métricas

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



# filtro por gv
gv_ = sorted(df_geral["GV"].dropna().astype(str).unique())
gv_fil = st.sidebar.multiselect("GV:", options=gv_)
df_geral = df_geral[df_geral["GV"].astype(str).isin(gv_fil)]

tipo_giro = sorted(df_geral["TIPO GIRO MENSAL"].dropna().astype(str).unique())
giro_fil = st.sidebar.multiselect("Selecione o Tipo de Giro:", options=tipo_giro)
df_geral2 = df_geral[df_geral["TIPO GIRO MENSAL"].astype(str).isin(giro_fil)]
# filtro por setor
rn = sorted(df_geral2["SETOR"].dropna().astype(str).unique())
rn_fil = st.sidebar.multiselect("Setor:", options=rn)
df_geral3 = df_geral2[df_geral2["SETOR"].astype(str).isin(rn_fil)]


st.subheader(f"Análise por GV: {gv_fil}")
             
colunas_alvo = ["CLIENTE", "NOME FANTASIA", "SETOR", "TIPO DE VASILHAME", "CAIXAS COMODATAS","GV", "COMPROU", "FALTA COMPRAR", "META", "TENDÊNCIA"]
df_alvo = df_geral3[[c for c in colunas_alvo if c in df_geral3.columns]].copy()
col_real = next((c for c in df_alvo.columns if "TENDEN" in c), None)


col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Meta", value=f"{metas_dinamicas: .2f}%")
with col2:
    st.metric(label="Resultado Parcial", value=f"{resultado_parcial: .2f}%", delta=f"{resultado_parcial: .2f}%")
with col3:
    st.metric(label="Tendência", value=f"{tendencia: .2f}%", delta=f"{delta_tend: .2f}%")
st.divider()

st.subheader(f"Tipo de Giro: {giro_fil}")
st.dataframe(df_alvo, use_container_width=True)


