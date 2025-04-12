import streamlit as st
import os
import back_comparar
import utils

st.set_page_config(layout="wide",
                   initial_sidebar_state="expanded",
                   page_title="Covenant")

st.logo(image='https://i.imgur.com/yqw0XYW.png')

# Diretório onde os contratos serão armazenados (constante de módulo)
CONTRATOS_DIR = "contratos"
os.makedirs(CONTRATOS_DIR, exist_ok=True)
# Se a pasta não existir, cria
if not os.path.exists(CONTRATOS_DIR):
    os.makedirs(CONTRATOS_DIR)

# Atualiza o estado com os contratos disponíveis
if "versoes" not in st.session_state:
    st.session_state.versoes = utils.atualizar_versoes()

st.title('📑 Comparar Versões')

# Permite o upload de múltiplos arquivos DOCX
arquivos = st.file_uploader("📂 Carregar contratos", type=["docx"], accept_multiple_files=True)
if arquivos:
    for novo_arquivo in arquivos:
        nome_final = utils.salvar_arquivo(novo_arquivo)

        # Verifica se o arquivo já foi adicionado (opcional)
        if nome_final not in st.session_state.versoes:
            st.session_state.versoes = utils.atualizar_versoes()
            st.success(f"✅ O contrato `{nome_final}` foi salvo com sucesso!")
        else:
            st.warning(f"⚠️ O contrato `{nome_final}` já foi carregado.")

# Botão para resetar os contratos
if st.button("Resetar Contratos"):
    utils.resetar_contratos()
    st.session_state.versoes = utils.atualizar_versoes()
    st.warning("Todos os contratos foram apagados!")
    st.stop()

# Filtro de Modo de Comparação
st.markdown("### Filtro de Modo de Comparação")
modo_atual = st.radio("Selecione o modo", ("Comparação Geral", "Comparação por Seções"))

if st.session_state.get("modo_comparacao") != modo_atual:
    st.session_state.resultado_comparacao = ""
st.session_state.modo_comparacao = modo_atual

# =============================================================================
# Comparação Geral
# =============================================================================
if modo_atual == "Comparação Geral":
    if len(st.session_state.versoes) >= 2:
        st.header("📊 Comparação Geral")
        versoes_validas = [f for f in st.session_state.versoes if not f.startswith('.') and f.lower().endswith('.docx')]
        col1, col2 = st.columns(2)
        with col1:
            versao_antiga = st.selectbox("📌 Versão Antiga:", versoes_validas, key="versao_antiga")
        with col2:
            versao_nova = st.selectbox("📌 Versão Nova:", versoes_validas, key="versao_nova")

            # Define o CSS da tabela
            css = """
            <style>
                  :root {
                      --background-color: transparent;
                      --text-color: #000000;
                  }
                  [data-theme="dark"] {
                      --background-color: #1e1e1e;
                      --text-color: #ffffff !important; 
                  }
                  table.diff-table {
                      width: 100%;
                      font-family: 'Inter', sans-serif;    
                  }
                  table.diff-table th, table.diff-table td {
                      padding: 12px 15px;
                      white-space: pre-wrap;
                      /* Remove as bordas laterais e inferior */
                      border-left: none !important;
                      border-right: none !important;
                      border-bottom: none !important;
                  }
                  table.diff-table thead {
                      font-weight: 600;                
                  }
                  .diff-removed {
                      background-color: #FFEBEE !important;
                      color: #B71C1C !important;
                  }
                  .diff-added {
                      background-color: #E8F5E9 !important;
                      color: #1B5E20 !important;
                  }
                  [data-theme="dark"] .diff-removed {
                      background-color: #330000 !important;
                      color: #FF6666 !important;
                  }
                  [data-theme="dark"] .diff-added {
                      background-color: #002200 !important;
                      color: #66FF66 !important;
                  }
                  .comment-summary {
                    font-size: 0.8em;
                    opacity: 0.5;
                    margin-top: 4px;
                    padding-top: 4px;
                    border-top: 1px solid var(--border-color);
                  }
                </style>
                """
            st.markdown(css, unsafe_allow_html=True)

        if st.button("🔍 Comparar"):
            caminho_antigo = os.path.join(back_comparar.CONTRATOS_DIR, versao_antiga)
            caminho_novo = os.path.join(back_comparar.CONTRATOS_DIR, versao_nova)

            # Extração dos comentários para cada versão
            comentarios_antigos = back_comparar.extrair_comentarios(caminho_antigo)
            comentarios_novos = back_comparar.extrair_comentarios(caminho_novo)

            # Extrai os parágrafos com associação de comentários (tooltip) para cada versão
            parags_antigos_tooltip = back_comparar.extrair_paragrafos_com_tooltip(caminho_antigo, comentarios_antigos)
            parags_novos_tooltip = back_comparar.extrair_paragrafos_com_tooltip(caminho_novo, comentarios_novos)

            # Chama a função do backend que gera a tabela HTML com o diff
            html_table = back_comparar.gerar_tabela_com_diff_somente_diferencas(parags_antigos_tooltip, parags_novos_tooltip)

            st.session_state.resultado_comparacao = html_table
            st.markdown(html_table, unsafe_allow_html=True)
        elif st.session_state.resultado_comparacao:
            st.markdown(st.session_state.resultado_comparacao, unsafe_allow_html=True)

# =============================================================================
# Comparação por Seções
# =============================================================================
elif modo_atual == "Comparação por Seções":
    if len(st.session_state.versoes) >= 2:
        st.header("🔎 Comparação por Seções")
        versoes_validas = [f for f in st.session_state.versoes if not f.startswith('.') and f.lower().endswith('.docx')]
        col1, col2 = st.columns(2)
        with col1:
            versao_antiga = st.selectbox("Versão Antiga:", versoes_validas, key="versao_antiga")
        with col2:
            versao_nova = st.selectbox("Versão Nova:", versoes_validas, key="versao_nova")
            # Define o CSS da tabela
            css = """
                <style>
                      :root {
                          --background-color: transparent;
                          --text-color: #000000;
                      }
                      [data-theme="dark"] {
                          --background-color: #1e1e1e;
                          --text-color: #ffffff !important; 
                      }
                      table.diff-table {
                          width: 100%;
                          font-family: 'Inter', sans-serif;    
                      }
                      table.diff-table th, table.diff-table td {
                          padding: 12px 15px;
                          white-space: pre-wrap;
                          /* Remove as bordas laterais e inferior */
                          border-left: none !important;
                          border-right: none !important;
                          border-bottom: none !important;
                      }
                      table.diff-table thead {
                          font-weight: 600;                
                      }
                      .diff-removed {
                          background-color: #FFEBEE !important;
                          color: #B71C1C !important;
                      }
                      .diff-added {
                          background-color: #E8F5E9 !important;
                          color: #1B5E20 !important;
                      }
                      [data-theme="dark"] .diff-removed {
                          background-color: #330000 !important;
                          color: #FF6666 !important;
                      }
                      [data-theme="dark"] .diff-added {
                          background-color: #002200 !important;
                          color: #66FF66 !important;
                      }
                      .comment-summary {
                        font-size: 0.8em;
                        opacity: 0.5;
                        margin-top: 4px;
                        padding-top: 4px;
                        border-top: 1px solid var(--border-color);
                      }
                    </style>
                    """
            st.markdown(css, unsafe_allow_html=True)

        # Define os caminhos para as versões
        caminho_antigo = os.path.join(back_comparar.CONTRATOS_DIR, versao_antiga)
        caminho_novo = os.path.join(back_comparar.CONTRATOS_DIR, versao_nova)

        # (Opcional) Extração dos comentários, se necessário
        comentarios_antigos = back_comparar.extrair_comentarios(caminho_antigo)
        comentarios_novos = back_comparar.extrair_comentarios(caminho_novo)

        # Extrai as seções dos dois contratos
        secoes_antigas = back_comparar.extrair_secoes(caminho_antigo)
        secoes_novas = back_comparar.extrair_secoes(caminho_novo)

        # Determina as seções comuns
        common_sections = sorted(list(set(secoes_antigas.keys()) & set(secoes_novas.keys())))
        if common_sections:
            secao_escolhida = st.selectbox("📌 Escolha a Seção para Comparação:", common_sections)

            # Pega os parágrafos da seção selecionada para cada versão
            parags_antigos = secoes_antigas.get(secao_escolhida, [])
            parags_novos = secoes_novas.get(secao_escolhida, [])

            # Caso alguns parágrafos estejam concatenados com numeração, divida-os
            parags_antigos = back_comparar.split_paragraphs(parags_antigos)
            parags_novos = back_comparar.split_paragraphs(parags_novos)

            # Cria listas de tuplas (parágrafo, tooltip). Se não houver tooltips, passa string vazia.
            parags_antigos_tooltip = [(p, "") for p in parags_antigos]
            parags_novos_tooltip = [(p, "") for p in parags_novos]

            if parags_antigos_tooltip or parags_novos_tooltip:
                # Chama a função do back-end que gera o diff somente com as diferenças
                html_table = back_comparar.gerar_tabela_com_diff_somente_diferencas(
                    parags_antigos_tooltip, parags_novos_tooltip
                )
                st.session_state.resultado_comparacao = html_table
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                st.warning("Nenhum texto encontrado para essa seção.")
        else:
            st.warning("⚠️ Não há seções comuns para comparar entre os dois contratos.")
    else:
        st.warning("⚠️ Carregue pelo menos duas versões para comparar.")

