import base64
import os

from pdf2image import convert_from_bytes
import streamlit as st

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
    str += "_" + dados['doc']
    str += "_" + dados['tipo'].replace(' ', '_')
    if 'danf' in dados.keys():
        str += "_" + dados['danf']
    str += "_%.2f" % dados['valor']

    return str.replace('/', '_')


def save_file(dir, name, file_body):
    with open(os.path.join(dir, name), "wb") as f:
        f.write(file_body)
    st.success(f"{name} salvo")


def download(file_path, filename, ext, texto='download'):
    with open(file_path, 'rb') as f:
        bytes = f.read()
        b64 = base64.b64encode(bytes).decode()
        href = f'<a href="data:file/{ext};base64,{b64}" download=\'{filename}\'>\
            {texto}\
        </a>'
    st.markdown(href, unsafe_allow_html=True)