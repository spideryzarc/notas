import hashlib

import numpy as np
import streamlit as st
from streamlit.script_runner import RerunException
from streamlit_tags import st_tags, st_tags_sidebar
from pycpfcnpj import cpfcnpj
from utils import list_hash_docs, show_pdf, update_prefix, lista_cadastrados, load_lista, save_file, csv_file_path, \
    docs_path, rerun
import os
import pandas as pd


def page_cadastro():
    cols = st.columns([2, 11, 5, 4])
    # uploaded files manage
    upload_placeholder = cols[1].empty()
    uploaded = upload_placeholder.file_uploader('Selecione todos os arquivos', key=f"up_key{st.session_state['seq']}",
                                                type=['pdf', 'jpg', 'jpeg', 'png'],
                                                accept_multiple_files=True)
    if not hasattr(st.session_state, 'files') or len(st.session_state['files']) == 0:
        if uploaded is not None and len(uploaded) > 0:
            hash_list = list_hash_docs()
            files = [{'name': u.name, 'body': u.read()} for u in uploaded]
            for f in files:
                h = hashlib.sha256()
                h.update(f['body'])
                f['hash'] = h.hexdigest()
                # print(f['hash'])
            for i in reversed(range(len(files))):
                if files[i]['hash'] in hash_list:
                    cols[0].warning(f'Arquivo: {files[i]["name"]} já foi cadastrado.')
                    del files[i]
            files.sort(key=lambda a: a['name'])
            st.session_state['files'] = files
        else:
            files = None
    else:
        files = st.session_state['files']

    # visualização dos selecionados
    if files is not None and len(files) > 0:
        upload_placeholder.empty()
        check = []
        for i, file in enumerate(files):
            name, ext = os.path.splitext(file['name'])
            # name = (name[:10] + '..') if len(name) > 10 else name
            check.append(cols[0].checkbox(name, key=f'check{i}'))

        selected = False
        with cols[1]:
            # preview_sufix = st.empty()
            with st.spinner('carregando...'):
                for i, c in enumerate(check):
                    if c:
                        selected = True
                        file = files[i]
                        name, ext = os.path.splitext(file['name'])
                        ex = st.expander(name, expanded=True)
                        with ex:
                            show_pdf(file['body'], ext)

        if selected:
            if cols[0].button("Remover"):
                for i in reversed(range(len(check))):
                    if check[i]:
                        del check[i]
                        del files[i]
                st.experimental_rerun()
            with cols[2]:
                dados = {}
                # dados['emissor'] = st.text_input('Emissor', key=f"emissor{st.session_state['seq']}")
                tag = st_tags(label='Emissor', text='', key=f"emissor{st.session_state['seq']}",
                              suggestions=lista_cadastrados('emissor'), maxtags=1)
                dados['emissor'] = tag[0].strip().title() if tag is not None and len(tag) > 0 else ''

                # dados['doc'] = st.text_input('cpf / cnpj', key=f"doc{st.session_state['seq']}")
                tag = st_tags(label='cpf / cnpj', text='', key=f"doc{st.session_state['seq']}",
                              suggestions=lista_cadastrados('doc'), maxtags=1)
                dados['doc'] = tag[0] if tag is not None and len(tag) > 0 else ''

                dados['classe'] = st.selectbox('Classificação', load_lista('dados/class.txt'))
            with cols[3]:

                dados['date'] = st.date_input('Data da compra', key='data')
                dados['valor'] = st.number_input('Valor Total', min_value=0.0, format='%.2f',
                                                 key=f"valor{st.session_state['seq']}")
                dados['tipo'] = st.selectbox('Tipologia', load_lista('dados/tipo.txt'))
                if dados['tipo'] is not None and dados['tipo'] == load_lista('dados/tipo.txt')[2]:
                    dados['danf'] = cols[2].text_input('DANF', key=f"danf{st.session_state['seq']}")
                elif 'danf' not in dados.keys():
                    dados['danf'] = ''

            ex = cols[2].expander('Detalhar', expanded=False)

            with ex:
                items_text = st.text_area("Itens da nota:", help="use ; para separar os campos", height=130,
                                          key=f"items{st.session_state['seq']}")
                st.write('Ex.:  <descrição> ; <quantidade> ; <valor total>')
                if items_text is not None:
                    items = []
                for l in items_text.splitlines():
                    if len(l.strip()) == 0:
                        continue
                    token = l.split(';')
                    if len(token) == 3:
                        fields = [token[0].strip().title()]
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

                df = pd.DataFrame(data=items, columns=['item', 'qtd', 'custo'])
                total = df.custo.sum()
                if total < dados['valor']:
                    dif = round(dados['valor'] - total, 2)
                    df = df.append({'item': 'Outros', 'qtd': 1, 'custo': dif}, ignore_index=True)
                elif total > dados['valor']:
                    st.warning("Valor da total nota está menor do que o listado.")
            cols[3].write(df)
            with cols[2]:

                if dados['doc'] is not None:
                    if not cpfcnpj.cpf.validate(dados['doc']) and not cpfcnpj.cnpj.validate(dados['doc']):
                        st.warning("cpf / cnpj inválido")
                if dados['emissor'] is None or dados['emissor'] == '':
                    st.warning("Emissor vazio")
                st.write(update_prefix(dados))
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
                        # count = 0
                        arquivos = []
                        for i, file in enumerate(files):
                            if check[i]:
                                name, ext = os.path.splitext(file['name'])
                                doc_name = f"{prefix}_{i}{ext}"
                                save_file(docs_path, doc_name, file['body'])
                                # count += 1
                                arquivos.append(doc_name)

                        for i in reversed(range(len(files))):
                            if check[i]:
                                del files[i]

                        for k, v in dados.items():
                            if k != 'valor':
                                df[k] = v
                        df['arquivos'] = str(arquivos)
                        # df['pdf_count'] = count
                        # df['pdf_prefix'] = prefix
                        # st.write(df)

                        if os.path.isfile(csv_file_path):
                            db = pd.read_csv(csv_file_path)
                            df['id_nota'] = db['id_nota'].max() + 1
                            db = pd.concat([db, df], ignore_index=True)
                            db.to_csv(csv_file_path, index=None)
                        else:
                            df['id_nota'] = 1
                            df.to_csv(csv_file_path, index=None)
                        # Delete all the items in Session state
                        st.session_state['seq'] += 1
                        # ph.button('Próximo')
                        st.experimental_rerun()

    pass
