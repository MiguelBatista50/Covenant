import os
import shutil
import zipfile
import difflib
import re
import html
from lxml import etree
from pathlib import Path

# Diretório onde os contratos serão armazenados (constante de módulo)
CONTRATOS_DIR = "../contratos"
os.makedirs(CONTRATOS_DIR, exist_ok=True)


def atualizar_versoes():
    """
    Retorna a lista ordenada de arquivos presentes no diretório de contratos.
    """
    return sorted(os.listdir(CONTRATOS_DIR))


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
    Remove o diretório de contratos e o recria, apagando todos os arquivos.
    """
    shutil.rmtree(CONTRATOS_DIR)
    os.makedirs(CONTRATOS_DIR, exist_ok=True)


def extrair_comentarios(caminho_arquivo):
    """
    Extrai os comentários do documento DOCX (do arquivo word/comments.xml).

    Retorna:
      Um dicionário onde a chave é o id do comentário e o valor é o texto formatado.
    """
    comentarios = {}
    with zipfile.ZipFile(caminho_arquivo) as docx_zip:
        if "word/comments.xml" in docx_zip.namelist():
            xml_content = docx_zip.read("word/comments.xml")
            tree = etree.fromstring(xml_content)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            for comment in tree.xpath("//w:comment", namespaces=ns):
                comment_id = comment.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")
                autor = comment.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author",
                                    "desconhecido")
                texto_comentario = "".join(comment.itertext()).strip()
                comentarios[comment_id] = f"💬 {autor}: {texto_comentario}"
    return comentarios


def extrair_paragrafos_com_tooltip(caminho_arquivo, comentarios):
    """
    Extrai os parágrafos do DOCX (word/document.xml) e acumula os comentários que
    estão associados a cada parágrafo, retornando uma lista de tuplas:
      (paragrafo_html, tooltip_summary)
    """
    # Se comentários for None, usa um dicionário vazio
    if comentarios is None:
        comentarios = {}

    paragraphs = []
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(caminho_arquivo) as z:
        xml_content = z.read("word/document.xml")
    tree = etree.fromstring(xml_content)

    # Itera por cada parágrafo
    for para in tree.xpath("//w:p", namespaces=ns):
        para_html = ""
        tooltip_list = []  # acumula os comentários encontrados neste parágrafo
        active_comment_ids = []  # IDs dos comentários "ativos" no parágrafo
        for elem in para.iter():
            tag = etree.QName(elem).localname
            if tag == "t":
                text = elem.text if elem.text else ""
                para_html += text
            elif tag == "br":
                para_html += "<br>"
            elif tag == "commentRangeStart":
                cid = elem.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")
                if cid:
                    active_comment_ids.append(cid)
            elif tag == "commentRangeEnd":
                if active_comment_ids:
                    active_comment_ids.pop()
            # Opcional: se houver elementos de referência de comentário:
            elif tag == "commentReference":
                cid = elem.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")
                if cid:
                    active_comment_ids.append(cid)
        # Para este parágrafo, combina os comentários (se houver)
        if active_comment_ids:
            tooltip_texts = [comentarios.get(cid, "") for cid in active_comment_ids if cid in comentarios]
            tooltip_summary = "<br>".join([html.escape(tt) for tt in tooltip_texts])
        else:
            tooltip_summary = ""
        # Se o parágrafo tiver quebras, podemos separar em blocos
        blocks = [block.strip() for block in para_html.split("<br>") if block.strip()]
        if blocks:
            for block in blocks:
                paragraphs.append((block, tooltip_summary))
        else:
            paragraphs.append((para_html, tooltip_summary))
    return paragraphs

def highlight_differences(old_text, new_text):
    """
    Compara dois textos e destaca as diferenças.

    Retorna:
      Uma tupla (highlighted_old, highlighted_new) onde:
        - highlighted_old: trechos do texto antigo com marcação HTML para as alterações.
        - highlighted_new: trechos do texto novo com marcação HTML para as alterações.
    """
    old_words = old_text.split()
    new_words = new_text.split()
    sm = difflib.SequenceMatcher(None, old_words, new_words)
    highlighted_old = []
    highlighted_new = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            highlighted_old.append(" ".join(old_words[i1:i2]))
            highlighted_new.append(" ".join(new_words[j1:j2]))
        elif tag == 'delete':
            segment = " ".join(old_words[i1:i2])
            # Use uma classe para indicar remoção
            highlighted_old.append(f"<span class='diff-removed'>{segment}</span>")
        elif tag == 'insert':
            segment = " ".join(new_words[j1:j2])
            # Use uma classe para indicar inserção
            highlighted_new.append(f"<span class='diff-added'>{segment}</span>")
        elif tag == 'replace':
            segment_old = " ".join(old_words[i1:i2])
            segment_new = " ".join(new_words[j1:j2])
            highlighted_old.append(f"<span class='diff-removed'>{segment_old}</span>")
            highlighted_new.append(f"<span class='diff-added'>{segment_new}</span>")
    return " ".join(highlighted_old), " ".join(highlighted_new)


def extrair_secoes(caminho_arquivo):
    """
    Extrai seções do documento DOCX com base em estilos de cabeçalho.

    Retorna:
      Um dicionário onde as chaves são os nomes das seções e os valores são listas de parágrafos pertencentes à seção.
    """
    secoes = {}
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(caminho_arquivo) as z:
        xml_content = z.read("word/document.xml")
    tree = etree.fromstring(xml_content)

    current_secao = "sem seção"
    secoes[current_secao] = []
    for para in tree.xpath("//w:p", namespaces=ns):
        pPr = para.find(".//w:pPr", namespaces=ns)
        is_heading = False
        if pPr is not None:
            pStyle = pPr.find(".//w:pStyle", namespaces=ns)
            if pStyle is not None:
                style_val = pStyle.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")
                if style_val and style_val.lower().startswith("heading"):
                    is_heading = True
        para_text = "".join(para.xpath(".//w:t/text()", namespaces=ns)).strip()
        if is_heading and para_text:
            current_secao = para_text
            if current_secao not in secoes:
                secoes[current_secao] = []
        else:
            if para_text:
                secoes[current_secao].append(para_text)
    return secoes

def split_paragraphs(text_list):
    """
    Recebe uma lista de strings e, se algum elemento contiver múltiplos itens numerados
    (ex.: "1.2 - ..." ou "1.2.1 ..."), divide esse elemento em uma lista de sub-parágrafos.

    Retorna:
      Uma lista onde cada item é um sub-parágrafo extraído.
    """
    result = []
    for text in text_list:
        parts = re.split(r'(?=\d+(?:\.\d+)+\s*)', text)
        parts = [part.strip() for part in parts if part.strip()]
        result.extend(parts)
    return result