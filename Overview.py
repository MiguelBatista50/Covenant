import streamlit as st
import os
import plotly.express as px
import datetime
import pandas as pd
import utils

st.set_page_config(layout="wide",
                   initial_sidebar_state="expanded",
                   page_title="Covenant")

st.logo(image='https://i.imgur.com/yqw0XYW.png')
st.title('👋🏻 Seja Bem-Vindo!')

# Atualiza o estado com os contratos disponíveis
if "versoes" not in st.session_state:
    st.session_state.versoes = utils.atualizar_versoes()

contrato_files = [f for f in os.listdir(utils.CONTRATOS_DIR) if not f.startswith('.') and f.lower().endswith('.docx')]
quantidade_contratos = len(contrato_files)

st.markdown(
    """
    Bem-vindo ao **Covenant** - Seu novo Gestor de Contratos.
    
    Esta aplicação foi desenvolvida como uma solução prática para a gestão eficiente de contratos jurídicos.
    Com funcionalidades de análise e comparação de documentos, oferece uma visão clara e organizada dos contratos,
    ajudando escritórios de advocacia e empresas a tomarem decisões mais informadas e rápidas.
    Explore as funcionalidades e veja como a inteligência de dados pode impulsionar a gestão jurídica.
    """
    )

st.write("")

# Cria 3 colunas para os cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total de Contratos", value=quantidade_contratos, delta="1.2")

with col2:
    st.metric(label="Contratos Ativos", value=quantidade_contratos, delta="1.2")

with col3:
    st.metric(label="Próximos a Vencer", value=quantidade_contratos, delta="1.2")

st.write("")
st.write("")

# =============================================================================
# Gráfico
# =============================================================================

files = [f for f in os.listdir(utils.CONTRATOS_DIR) if not f.startswith('.') and f.lower().endswith('.docx')]
data_list = []
for f in files:
    file_path = os.path.join(utils.CONTRATOS_DIR, f)
    mod_time = os.path.getmtime(file_path)
    mod_date = datetime.datetime.fromtimestamp(mod_time)
    file_size = os.path.getsize(file_path)
    data_list.append({
        "Nome do Arquivo": f,
        "Data de Modificação": mod_date,
        "Tamanho": file_size
    })

# Cria o DataFrame com os dados dos arquivos
df_contratos = pd.DataFrame(data_list)

# Exibe o DataFrame
st.subheader("📂 Contratos Recentes")

st.dataframe(df_contratos)

# Botão para resetar os contratos
if st.button("Resetar Contratos"):
    utils.resetar_contratos()
    st.session_state.versoes = utils.atualizar_versoes()
    st.warning("Todos os contratos foram apagados!")
    st.stop()

# Para o gráfico de evolução mensal, cria uma coluna para agrupar por Ano-Mês
if not df_contratos.empty:
    df_contratos["Data"] = df_contratos["Data de Modificação"].dt.date
    # Agrupar os contratos por data e contar quantos foram modificados em cada dia
    df_daily = df_contratos.groupby("Data").size().reset_index(name="Contratos")
    # Converter a coluna 'Data' para datetime para o Plotly tratar como data
    df_daily["Data"] = pd.to_datetime(df_daily["Data"])
else:
    df_daily = pd.DataFrame(columns=["Data", "Contratos"])

st.subheader("📈 Dashboard")

# Criar o gráfico de evolução diária utilizando Plotly Express (sem título)
fig = px.line(
    df_daily,
    x="Data",
    y="Contratos",
    markers=True,
    labels={"Data": "Data", "Contratos": "Quantidade de Contratos"}
)

# Atualizar o formato dos ticks do eixo x para mostrar a data no formato dd/mm/aaaa e fixar os eixos
fig.update_xaxes(tickformat="%d/%m/%Y", fixedrange=True)
fig.update_yaxes(fixedrange=True)

# Configurações: desabilitar a barra de modo, mantendo interatividade (tooltips)
config = {
    'displayModeBar': False,
    'staticPlot': False
}

st.plotly_chart(fig, use_container_width=True, config=config)

