import base64
import os
import pathlib
from pathlib import Path

from pdf2image import convert_from_bytes
import streamlit as st
import pandas as pd
import hashlib
import subprocess

notas_csv_file = 'csv/notas.csv'
fornecedores_csv_file = 'csv/fornecedores.csv'
docs_path = './pdfs/'
csv_path = './csv/'

notas_cols_order = ['id_nota', 'emissor', 'date', 'item', 'qtd', 'custo', 'danfe', 'arquivos']
fornecedores_cols_order = ['nome', 'tel', 'doc', 'classe']



STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / 'static'
DOWNLOADS_PATH = (STREAMLIT_STATIC_PATH / "downloads")


def static_symlink(path_target, name_link, package_name="streamlit"):
    # run show command to determine where package is (see https://stackoverflow.com/a/46071447)
    cmd_list = ["pip", "show", package_name]
    # modified for subprocess - https://stackoverflow.com/a/16516701 (5/27)
    proc = subprocess.Popen(cmd_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    list_results = []
    list_raw = []
    # Read line from stdout, break if EOF reached, append line to output
    for line in proc.stdout:
        line = line.decode().strip()
        if "Location" in line:
            line_parts = line.split(" ")
            if len(line_parts) == 2:  # slightly odd, but nested 'static' entries for true static hosting
                list_results.append(Path(line_parts[-1]).joinpath(package_name, 'static', 'static'))
        list_raw.append(line)
    if len(list_results) == 0:
        st.error(f"Error, could not find package location (source {list_raw})")
        return None

    # create target directory if it doesn't exist (all permissions)
    path_target = Path(path_target)
    if not path_target.exists():
        path_target.mkdir(parents=True)

    # create symlink directory to target with specific name
    path_link = list_results[0].joinpath(name_link)
    if path_link.exists():
        print(f"Symlink {str(path_link)} already exists, skipping recreate")
    else:
        path_link.symlink_to(path_target, True)
    return str(path_link)

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
    if os.path.isfile(notas_csv_file):
        df = pd.read_csv(notas_csv_file)
        try:
            df = df[df[field].str.len() > 0]
            return list(df[field].unique())
        except:
            return []
    else:
        return []


def lista_fornecedores():
    if os.path.isfile(fornecedores_csv_file):
        df = pd.read_csv(fornecedores_csv_file)
        try:
            df = df[df['nome'].str.len() > 0]
            return list(df['nome'].unique())
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
