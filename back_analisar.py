import zipfile
from lxml import etree
from transformers import pipeline
import os
import re

# Diretório base do projeto (local onde o back_analisar.py está)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório onde os contratos serão armazenados
CONTRATOS_DIR = os.path.join(BASE_DIR, 'contratos')
os.makedirs(CONTRATOS_DIR, exist_ok=True)

# --- Carregar o modelo Hugging Face ---
ner_pipeline = pipeline(
    "ner",
    model="Babelscape/wikineural-multilingual-ner",
    aggregation_strategy="simple"
)

# --- Funções auxiliares (Regex) ---

def extrair_valores_monetarios(texto):
    padrao_valor = r'(?:R\$|US\$|\u20ac)\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?'
    valores = re.findall(padrao_valor, texto)
    return valores

def extrair_datas(texto):
    padrao_data = r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b|\b\d{1,2}\s+de\s+[a-zA-Z]+\s+de\s+\d{4}\b'
    datas = re.findall(padrao_data, texto)
    return datas

def extrair_localizacoes(texto):
    padrao_localizacao = r'(?:Setor|Quadra|Lote|Bloco|CEP|Brasília\/DF|CRS|Rua|Avenida)\s+[\w\s,\/ªº-]+'
    locais = re.findall(padrao_localizacao, texto)
    return locais

# --- Funções principais ---

def extrair_texto_docx(caminho_arquivo):
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    with zipfile.ZipFile(caminho_arquivo, 'r') as z:
        xml_content = z.read('word/document.xml')
    root = etree.fromstring(xml_content)
    texto = " ".join(root.xpath("//w:t/text()", namespaces=ns))
    return texto

def analisar_ner_local(texto):
    resultados = ner_pipeline(texto)

    entidades = {
        "PESSOAS": [],
        "ORGANIZACOES": [],
        "DATAS": [],
        "VALORES": [],
        "OUTROS": []
    }

    for ent in resultados:
        entidade = ent['word'].replace("##", "").strip()
        tipo = ent['entity_group'].upper()

        if len(entidade.replace(" ", "")) > 2:
            if tipo == "PER":
                entidades["PESSOAS"].append(entidade)
            elif tipo == "ORG":
                entidades["ORGANIZACOES"].append(entidade)
            elif tipo == "MISC":
                entidades["OUTROS"].append(entidade)
            elif tipo == "DATE":
                entidades["DATAS"].append(entidade)
            elif tipo == "MONEY":
                entidades["VALORES"].append(entidade)
            else:
                entidades["OUTROS"].append(entidade)

    valores_regex = extrair_valores_monetarios(texto)
    datas_regex = extrair_datas(texto)
    locais_regex = extrair_localizacoes(texto)

    if valores_regex:
        entidades["VALORES"].extend(valores_regex)

    if datas_regex:
        entidades["DATAS"].extend(datas_regex)

    entidades["DATAS"] = list(set(entidades["DATAS"]))
    entidades["VALORES"] = list(set(entidades["VALORES"]))

    return entidades, locais_regex
