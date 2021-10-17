# import locale
# locale.setlocale(locale.LC_NUMERIC, 'pt_BR')

import base64
import os
import shutil

from pycpfcnpj import cpfcnpj

import numpy as np
import streamlit as st
# from streamlit_tags import st_tags
import pandas as pd

if 'prods' not in st.session_state:
    st.session_state['prods'] = []

if 'seq' not in st.session_state:
    st.session_state['seq'] = 0

st.set_page_config(layout='wide')

print('reloaded')


def load_lista(path):
    with open(path, 'r') as file:
        return file.readlines()


def empty_dir(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def save_file(dir, name, file):
    with open(os.path.join(dir, name), "wb") as f:
        f.write(file.getbuffer())
    st.success(f"{name} salvo")


def update_prefix(dados):
    str = f"{dados['date']}"
    str += "_" + dados['doc']
    str += "_" + dados['tipo'].replace(' ', '_')
    if 'danf' in dados.keys():
        str += "_" + dados['danf']
    str += "_%.2f" % dados['valor']

    return str


def adicionaNotas():
    st.title('Cadastro de notas')
    lay_cols = st.columns([1, 2, 4])
    with lay_cols[0]:
        cont_form = st.container()
    with lay_cols[1]:
        cont_content = st.container()
    with lay_cols[2]:
        cont_view = st.container()

    uploaded = cont_view.file_uploader('Escolha um arquivo', key=f"up_key{st.session_state['seq']}", type=['pdf'],
                                       accept_multiple_files=True)
    if uploaded is not None and len(uploaded) > 0:
        with cont_form:
            dados = {}
            dados['tipo'] = st.selectbox('Tipologia', load_lista('dados/tipo.txt'))
            if dados['tipo'] is not None and dados['tipo'] == load_lista('dados/tipo.txt')[0]:
                dados['danf'] = st.text_input('DANF', key=f"danf{st.session_state['seq']}")
            dados['emissor'] = st.text_input('Emissor', key=f"emissor{st.session_state['seq']}")
            dados['doc'] = st.text_input('cpf / cnpj', key=f"doc{st.session_state['seq']}")
            if dados['doc'] is not None:
                if not cpfcnpj.cpf.validate(dados['doc']) and not cpfcnpj.cnpj.validate(dados['doc']):
                    st.error("Documento inválido")
            dados['classe'] = st.selectbox('Classificação', load_lista('dados/class.txt'))
            dados['valor'] = st.number_input('Valor Total', min_value=0.0, format='%.2f',
                                             key=f"valor{st.session_state['seq']}")
            dados['date'] = st.date_input('Data da compra', key='data')
        with cont_content:
            items_text = st.text_area("Itens da nota:", help="use ; para separar os campos", height=300,
                                      key=f"items{st.session_state['seq']}")
            st.write('Ex.:  <descrição> ; <quantidade> ; <valor total>')
            if items_text is not None:
                items = []
            for l in items_text.splitlines():
                if len(l.strip()) == 0:
                    continue
                token = l.split(';')
                if len(token) == 3:
                    fields = [token[0]]
                    try:
                        fields.append(int(token[1]))
                    except ValueError:
                        st.error(f'Valor não é um número inteiro: "{token[1]}"')
                    try:
                        fields.append(float(token[2]))
                    except ValueError:
                        st.error(f'Valor não é um número: "{token[2]}"')
                else:
                    st.error(f'Formato errado: "{l}"')
                items.append(fields)
            cols = ['item', 'qtd', 'custo']
            df = pd.DataFrame(data=items, columns=cols)
            total = df.custo.sum()
            if total < dados['valor']:
                dif = dados['valor'] - total
                df = df.append({'item': 'Outros', 'qtd': 1, 'custo': dif}, ignore_index=True)
            elif total > dados['valor']:
                st.error("Valor da total nota está menor do que o listado.")
            st.write(df)
            ph = st.empty()
            if ph.button('Finalizar'):
                ok = True
                if dados['valor'] <= 0:
                    st.error('Valor da nota está 0.')
                    ok = False
                if dados['emissor'] == '':
                    st.error('Emissor vazio')
                    ok = False
                # st.session_state['emissor_input'] = ''
                if ok:
                    prefix = update_prefix(dados)
                    for i, pdf_file in enumerate(uploaded):
                        save_file('pdfs', f"{prefix}_{i}.pdf", pdf_file)

                    for k,v in dados.items():
                        if k!='valor':
                            df[k] = v
                    df['pdf_count'] = len(uploaded)
                    df['pdf_prefix'] = prefix
                    # st.write(df)
                    csvpath = 'csv/notas.csv'
                    if os.path.isfile(csvpath):
                        db = pd.read_csv(csvpath)
                        db = pd.concat([db,df], ignore_index=True)
                        db.to_csv(csvpath,index=None)
                    else:
                        df.to_csv(csvpath,index=None)
                    # Delete all the items in Session state
                    st.session_state['seq'] += 1
                    ph.button('Próximo')
        #end loaded
    with cont_view:
        # st.title('view')
        if uploaded is not None:
            for i, pdf_file in enumerate(uploaded):
                ex = st.expander(pdf_file.name, expanded=True)
                with ex:
                    st.write(f"Será salvo como: {update_prefix(dados)}_{i}.pdf")
                    base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="90%" height="{800}" type="application/pdf">'
                    st.markdown(pdf_display, unsafe_allow_html=True)


def test():
    st.title('test')


# main
if not hasattr(st.session_state, 'page'):
    st.session_state.page = adicionaNotas

# if st.sidebar.button("Adicionar Notas"):
#     st.session_state.page = adicionaNotas
#
# if st.sidebar.button("Test"):
#     st.session_state.page = test

st.session_state.page()
