import os
import streamlit as st
import back_analisar
import utils

# --- Configuração da página ---
st.set_page_config(layout="wide",
                   initial_sidebar_state="expanded",
                   page_title="Covenant")

st.logo(image='https://i.imgur.com/yqw0XYW.png')

# --- Diretórios ---
CONTRATOS_DIR = "contratos"
os.makedirs(CONTRATOS_DIR, exist_ok=True)
# Se a pasta não existir, cria
if not os.path.exists(CONTRATOS_DIR):
    os.makedirs(CONTRATOS_DIR)

def exibir_lista(titulo, itens):
    if itens:
        st.markdown(f"#### {titulo} ({len(itens)})")
        for item in itens:
            st.markdown(f"- {item}")
    else:
        st.markdown(f"#### {titulo} (0)")
        st.markdown("_Nenhum encontrado._")

# --- Função principal ---
def main():
    st.title("Analisar Contratos")

    if "versoes" not in st.session_state:
        st.session_state.versoes = utils.atualizar_versoes()

    arquivos = st.file_uploader("📂 Carregar contratos", type=["docx"], accept_multiple_files=True)
    if arquivos:
        for novo_arquivo in arquivos:
            nome_final = utils.salvar_arquivo(novo_arquivo)
            if nome_final not in st.session_state.versoes:
                st.session_state.versoes = utils.atualizar_versoes()
                st.success(f"✅ Contrato `{nome_final}` salvo com sucesso!")
            else:
                st.warning(f"⚠️ Contrato `{nome_final}` já havia sido carregado.")

    if st.button("Resetar Contratos"):
        utils.resetar_contratos()
        st.session_state.versoes = utils.atualizar_versoes()
        st.warning("Todos os contratos foram apagados!")
        st.stop()

    arquivos_salvos = [f for f in utils.atualizar_versoes() if not f.startswith('.') and f.lower().endswith('.docx')]
    if arquivos_salvos:
        arquivo_escolhido = st.selectbox("Selecione um contrato para análise:", arquivos_salvos)

        if arquivo_escolhido:
            caminho_arquivo = os.path.join(CONTRATOS_DIR, arquivo_escolhido)
            texto = back_analisar.extrair_texto_docx(caminho_arquivo)
            entidades_local, locais_detectados = back_analisar.analisar_ner_local(texto)

            st.subheader("🔍 Entidades Reconhecidas")

            # Pessoas
            st.markdown(f"#### Pessoas ({len(entidades_local['PESSOAS'])})")
            if entidades_local["PESSOAS"]:
                pessoas_texto = "\n".join([f"- {p}" for p in entidades_local["PESSOAS"]])
                st.markdown(pessoas_texto)
            else:
                st.markdown("_Nenhuma pessoa encontrada._")

            # Organizações
            st.markdown(f"#### Organizações ({len(entidades_local['ORGANIZACOES'])})")
            if entidades_local["ORGANIZACOES"]:
                orgs_texto = "\n".join([f"- {o}" for o in entidades_local["ORGANIZACOES"]])
                st.markdown(orgs_texto)
            else:
                st.markdown("_Nenhuma organização encontrada._")

            # Datas
            st.markdown(f"#### Datas ({len(entidades_local['DATAS'])})")
            if entidades_local["DATAS"]:
                datas_texto = "\n".join([f"- {d}" for d in entidades_local["DATAS"]])
                st.markdown(datas_texto)
            else:
                st.markdown("_Nenhuma data encontrada._")

            # Valores
            st.markdown(f"#### Valores ({len(entidades_local['VALORES'])})")
            if entidades_local["VALORES"]:
                valores_texto = "\n".join([f"- {v}" for v in entidades_local["VALORES"]])
                st.markdown(valores_texto)
            else:
                st.markdown("_Nenhum valor encontrado._")

            # Outros
            st.markdown(f"#### Outros ({len(entidades_local['OUTROS'])})")
            if entidades_local["OUTROS"]:
                outros_texto = "\n".join([f"- {o}" for o in entidades_local["OUTROS"]])
                st.markdown(outros_texto)
            else:
                st.markdown("_Nenhuma entidade extra encontrada._")

# --- Executar ---
if __name__ == "__main__":
    main()
