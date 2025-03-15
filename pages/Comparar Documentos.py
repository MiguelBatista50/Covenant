import streamlit as st
import os
import back_comparar

st.set_page_config(layout="wide",
                   initial_sidebar_state="expanded",
                   page_title="Covenant")

# Atualiza o estado com os contratos disponíveis
if "versoes" not in st.session_state:
    st.session_state.versoes = back_comparar.atualizar_versoes()

# Permite o upload de múltiplos arquivos DOCX
arquivos = st.file_uploader("📂 Carregar contratos", type=["docx"], accept_multiple_files=True)
if arquivos:
    for novo_arquivo in arquivos:
        nome_final = back_comparar.salvar_arquivo(novo_arquivo)

        # Verifica se o arquivo já foi adicionado (opcional)
        if nome_final not in st.session_state.versoes:
            st.session_state.versoes = back_comparar.atualizar_versoes()
            st.success(f"✅ O contrato `{nome_final}` foi salvo com sucesso!")
        else:
            st.warning(f"⚠️ O contrato `{nome_final}` já foi carregado.")


# Botão para resetar os contratos
if st.button("Resetar Contratos"):
    back_comparar.resetar_contratos()
    st.session_state.versoes = back_comparar.atualizar_versoes()
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
        st.header("📊 Comparação Geral entre Contratos")
        col1, col2 = st.columns(2)
        with col1:
            versao_antiga = st.selectbox("📌 Versão Antiga:", st.session_state.versoes, index=0)
        with col2:
            versao_nova = st.selectbox("📌 Versão Nova:", st.session_state.versoes, index=len(st.session_state.versoes)-1)
        if st.button("🔍 Comparar"):
            caminho_antigo = os.path.join(back_comparar.CONTRATOS_DIR, versao_antiga)
            caminho_novo = os.path.join(back_comparar.CONTRATOS_DIR, versao_nova)

            # Extração dos comentários para cada versão
            comentarios_antigos = back_comparar.extrair_comentarios(caminho_antigo)
            comentarios_novos = back_comparar.extrair_comentarios(caminho_novo)

            # Extrai os parágrafos com associação de comentários (tooltip) para cada versão
            parags_antigos_tooltip = back_comparar.extrair_paragrafos_com_tooltip(caminho_antigo, comentarios_antigos)
            parags_novos_tooltip   = back_comparar.extrair_paragrafos_com_tooltip(caminho_novo, comentarios_novos)

            # Define o CSS da tabela
            css = """
            <style>
              :root {
                  --background-color: #ffffff;
                  --text-color: #000000;
                  --secondary-background-color: #f9f9f9;
                  --border-color: #ddd;
              }
              [data-theme="dark"] {
                  --background-color: #1e1e1e;
                  --text-color: #f1f1f1;
                  --secondary-background-color: #2a2a2a;
                  --border-color: #444;
              }
              table.diff-table {
                  width: 100%;
                  border-collapse: collapse;
                  font-family: 'Inter', sans-serif;
                  margin: 20px auto;
                  background-color: var(--background-color) !important;
                  color: var(--text-color) !important;
                  /* Removendo todas as bordas externas da tabela */
                  border: none !important;
              }
              table.diff-table th, table.diff-table td {
                  padding: 12px 15px;
                  text-align: left;
                  white-space: pre-wrap;
                  background-color: var(--background-color) !important;
                  color: var(--text-color) !important;
                  /* Remove as bordas laterais e inferior */
                  border-left: none !important;
                  border-right: none !important;
                  border-bottom: none !important;
                  /* Se quiser manter a borda superior, pode definir: */
                  border-top: 1px solid var(--border-color) !important;
              }
              table.diff-table thead {
                  background-color: var(--secondary-background-color) !important;
                  color: var(--text-color) !important;
                  font-weight: 600;
                  /* Remove todas as bordas do cabeçalho */
                  border: none !important;
              }
              table.diff-table tbody tr:nth-of-type(odd) {
                  background-color: var(--background-color) !important;
              }
              table.diff-table tbody tr:nth-of-type(even) {
                  background-color: var(--secondary-background-color) !important;
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

            # Monte a tabela HTML utilizando os parágrafos com tooltip
            # Aqui assumimos que a ordem em parags_antigos_tooltip e parags_novos_tooltip é consistente
            html_table = "<table class='diff-table'><thead><tr>"
            html_table += f"<th>{versao_antiga}</th><th>{versao_nova}</th></tr></thead><tbody>"

            n = max(len(parags_antigos_tooltip), len(parags_novos_tooltip))
            for i in range(n):

                # Cada item é uma tupla (paragrafo_html, tooltip)
                p_antigo, tooltip_antigo = parags_antigos_tooltip[i] if i < len(parags_antigos_tooltip) else ("", "")
                p_novo, tooltip_novo = parags_novos_tooltip[i] if i < len(parags_novos_tooltip) else ("", "")

                # Se os parágrafos são diferentes, aplica a comparação
                if p_antigo != p_novo:
                    highlighted_old, highlighted_new = back_comparar.highlight_differences(p_antigo, p_novo)

                    # Insere o resumo dos comentários abaixo do conteúdo comparado
                    if tooltip_antigo:
                        highlighted_old += f"<div class='comment-summary'>{tooltip_antigo}</div>"
                    if tooltip_novo:
                        highlighted_new += f"<div class='comment-summary'>{tooltip_novo}</div>"

                    html_table += f"<tr><td>{highlighted_old}</td><td>{highlighted_new}</td></tr>"

            html_table += "</tbody></table>"

            st.session_state.resultado_comparacao = html_table
            st.markdown(html_table, unsafe_allow_html=True)
        elif st.session_state.resultado_comparacao:
            st.markdown(st.session_state.resultado_comparacao, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Carregue pelo menos duas versões para comparar.")

# =============================================================================
# Comparação por Seções
# =============================================================================
elif modo_atual == "Comparação por Seções":
    if len(st.session_state.versoes) >= 2:
        st.header("🔎 Comparação por Seções")
        col1, col2 = st.columns(2)
        with col1:
            versao_antiga = st.selectbox("Versão Antiga:", st.session_state.versoes, index=0)
        with col2:
            versao_nova = st.selectbox("Versão Nova:", st.session_state.versoes,
                                       index=len(st.session_state.versoes) - 1)

        caminho_antigo = os.path.join(back_comparar.CONTRATOS_DIR, versao_antiga)
        caminho_novo = os.path.join(back_comparar.CONTRATOS_DIR, versao_nova)

        # Extração dos comentários para cada versão #
        comentarios_antigos = back_comparar.extrair_comentarios(caminho_antigo)
        comentarios_novos = back_comparar.extrair_comentarios(caminho_novo)

        # Extrai os parágrafos com associação de comentários (tooltip) para cada versão
        parags_antigos_tooltip = back_comparar.extrair_paragrafos_com_tooltip(caminho_antigo, comentarios_antigos)
        parags_novos_tooltip = back_comparar.extrair_paragrafos_com_tooltip(caminho_novo, comentarios_novos)

        secoes_antigas = back_comparar.extrair_secoes(caminho_antigo)
        secoes_novas = back_comparar.extrair_secoes(caminho_novo)

        common_sections = sorted(list(set(secoes_antigas.keys()) & set(secoes_novas.keys())))
        if common_sections:
            secao_escolhida = st.selectbox("📌 Escolha a Seção para Comparação:", common_sections)
            parags_antigos = secoes_antigas.get(secao_escolhida, [])
            parags_novos = secoes_novas.get(secao_escolhida, [])

            # Divide os parágrafos se houver itens concatenados com numeração
            parags_antigos = back_comparar.split_paragraphs(parags_antigos)
            parags_novos = back_comparar.split_paragraphs(parags_novos)

            if parags_antigos or parags_novos:
                html_table = """
                <style>
                  /* Estilos para a tabela de comparação (modo padrão, light) */
                  table.diff-table {
                      width: 100%;
                      border-collapse: collapse;
                      font-family: 'Inter', sans-serif;
                      margin: 20px auto;
                      background-color: #ffffff !important;
                      color: #000000 !important;
                  }
                  table.diff-table th, table.diff-table td {
                      border: 1px solid #ddd;
                      padding: 12px 15px;
                      text-align: left;
                      white-space: pre-wrap;
                      color: #000000 !important;
                  }
                  table.diff-table thead {
                      background-color: #333333 !important;
                      color: #ffffff !important;
                  }

                  /* Estilo para texto removido e adicionado no modo light */
                  .diff-removed {
                      background-color: #FF8282;
                      color: #000000;
                  }
                  .diff-added {
                      background-color: #ccffcc;
                      color: #000000;
                  }

                  /* Estilo zebra e outros ajustes */
                  table.diff-table tbody tr:nth-of-type(odd) {
                      background-color: #f9f9f9 !important;
                  }
                  table.diff-table tbody tr:nth-of-type(even) {
                      background-color: #ffffff !important;
                  }
                  table.diff-table tbody tr:hover {
                      background-color: inherit !important;
                  }

                  /* Adaptação para modo dark */
                  @media (prefers-color-scheme: dark) {
                      table.diff-table {
                          background-color: #1e1e1e !important;
                          color: #f1f1f1 !important;
                      }
                      table.diff-table th, table.diff-table td {
                          color: #f1f1f1 !important;
                      }
                      table.diff-table thead {
                          background-color: #333333 !important;
                          color: #ffffff !important;
                      }
                      table.diff-table tbody tr:nth-of-type(odd) {
                          background-color: #2a2a2a !important;
                      }
                      table.diff-table tbody tr:nth-of-type(even) {
                          background-color: #1e1e1e !important;
                      }
                      /* Ajustar as cores para as diferenças no modo dark */
                      .diff-removed {
                          background-color: #D73027;  /* Um vermelho mais saturado */
                          color: #ffffff;
                      }
                      .diff-added {
                          background-color: #1A9850;  /* Um verde mais vibrante */
                          color: #ffffff;
                      }
                  }
                </style>

                <style>
                    table.section-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-family: 'Inter', sans-serif;
                        margin: 20px auto;
                        background-color: var(--background-color) !important;
                        color: var(--text-color) !important;
                    }
                    table.section-table th,
                    table.section-table td {
                        border: 1px solid var(--secondary-background-color);
                        padding: 12px 15px;
                        text-align: left;
                        white-space: pre-wrap;
                        color: var(--text-color) !important;
                    }
                    table.section-table thead {
                        background-color: var(--secondary-background-color) !important;
                        color: var(--text-color) !important;
                    }
                    table.section-table tbody tr:nth-of-type(odd) {
                        background-color: var(--background-color);
                    }
                    table.section-table tbody tr:nth-of-type(even) {
                        background-color: var(--secondary-background-color);
                    }
                </style>
                """

                html_table += f"<table class='section-table'><thead><tr><th>{versao_antiga}</th><th>{versao_nova}</th></tr></thead><tbody>"

                max_rows = max(len(parags_antigos), len(parags_novos))
                for i in range(max_rows):

                    p_antiga = parags_antigos[i] if i < len(parags_antigos) else ""
                    p_novo = parags_novos[i] if i < len(parags_novos) else ""

                    # Inicializa as variáveis
                    highlighted_old = ""
                    highlighted_new = ""

                    if p_antiga != p_novo:
                        highlighted_old, highlighted_new = back_comparar.highlight_differences(p_antiga, p_novo)
                    else:
                        highlighted_old, highlighted_new = p_antiga, p_novo
                    html_table += f"<tr><td>{highlighted_old}</td><td>{highlighted_new}</td></tr>"


                html_table += "</tbody></table>"
                st.session_state.resultado_comparacao = html_table
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                st.warning("Nenhum texto encontrado para essa seção.")
        else:
            st.warning("⚠️ Não há seções comuns para comparar entre os dois contratos.")
    else:
        st.warning("⚠️ Carregue pelo menos duas versões para comparar.")
