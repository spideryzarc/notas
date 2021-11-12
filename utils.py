import base64
import os

from pdf2image import convert_from_bytes
import streamlit as st
import pandas as pd
import hashlib

csv_file_path = 'csv/notas.csv'
docs_path = './pdfs/'


def show_pdf(file_body, ext='.pdf'):
    if ext == '.pdf':
        images = convert_from_bytes(file_body)
        st.image(images)
    else:
        st.image(file_body)


def load_lista(path):
    with open(path, 'r') as file:
        return file.readlines()


def update_prefix(dados):
    str = f"{dados['date']}"
    # str += "_" + dados['doc']
    if len(dados['emissor'].strip()) > 0:
        str += "_" + dados['emissor'].strip().title().replace(' ', '-')
    str += "_" + dados['tipo'].strip().replace(' ', '-')
    if 'danf' in dados.keys() and len(dados['danf']) > 0:
        str += "_" + dados['danf'].strip()
    str += "_%.2f" % dados['valor']

    return str.replace('/', '_')


def save_file(dir, name, file_body):
    with open(os.path.join(dir, name), "wb") as f:
        f.write(file_body)
    st.success(f"{name} salvo")


def download(file_path, filename, ext, texto='Download'):
    with open(file_path, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/{ext};base64,{b64}" download=\'{filename}\'>\
            {texto}\
        </a>'
    st.markdown(href, unsafe_allow_html=True)


def lista_cadastrados(field):
    if os.path.isfile(csv_file_path):
        df = pd.read_csv(csv_file_path)
        try:
            df = df[df[field].str.len() > 0]
            return list(df[field].unique())
        except:
            return []
    else:
        return []


def get_digest(file_path):
    h = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()


def list_hash_docs():
    hash_list = []
    for root, dirs, files in os.walk(docs_path):
        for file in files:
            hash_list.append(get_digest(os.path.join(root, file)))
    # print(hash_list)
    return hash_list
