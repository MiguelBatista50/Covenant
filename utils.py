import os
from pathlib import Path

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório onde os contratos serão armazenados
CONTRATOS_DIR = os.path.join(BASE_DIR, 'contratos')

# Garante que a pasta de contratos exista
os.makedirs(CONTRATOS_DIR, exist_ok=True)

def atualizar_versoes():
    """
    Retorna uma lista ordenada dos arquivos .docx presentes no diretório de contratos,
    ignorando arquivos ocultos como .gitkeep.
    """
    arquivos = [
        f for f in os.listdir(CONTRATOS_DIR)
        if not f.startswith('.') and f.lower().endswith('.docx')
    ]
    return sorted(arquivos)

def salvar_arquivo(uploaded_file):
    """
    Salva o arquivo enviado no diretório de contratos.

    Parâmetros:
      uploaded_file: objeto file-like (por exemplo, retornado pelo Streamlit).

    Retorna:
      O nome final do arquivo salvo.
    """
    nome_original = Path(uploaded_file.name).stem
    extensao = Path(uploaded_file.name).suffix
    nome_final = f"{nome_original}{extensao}"
    caminho_destino = os.path.join(CONTRATOS_DIR, nome_final)
    with open(caminho_destino, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return nome_final

def resetar_contratos():
    """
    Remove todos os arquivos .docx no diretório de contratos.
    """
    for arquivo in os.listdir(CONTRATOS_DIR):
        caminho_arquivo = os.path.join(CONTRATOS_DIR, arquivo)
        if os.path.isfile(caminho_arquivo) and arquivo.lower().endswith('.docx'):
            os.remove(caminho_arquivo)
