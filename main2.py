import os
import zipfile

import pandas as pd
import streamlit as st
from streamlit_tags import st_tags, st_tags_sidebar
from pycpfcnpj import cpfcnpj

from utils import *

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

if 'seq' not in st.session_state:
    st.session_state['seq'] = 0


def cadastro():
    # keywords = st_tags(
    #     label='# Enter Keywords:',
    #     text='Press enter to add more',
    #     value=['Zero', 'One', 'Two'],
    #      =['five', 'six', 'seven',
    #                  'eight', 'nine', 'three',
    #                  'eleven', 'ten', 'four'],
    #     maxtags=4,
    #     key='1')

    cols = st.columns([2, 11, 5, 4])
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

    if files is not None and len(files) > 0:
        upload_placeholder.empty()
        check = []
        for i, file in enumerate(files):
            name, ext = os.path.splitext(file['name'])
            # name = (name[:10] + '..') if len(name) > 10 else name
            check.append(cols[0].checkbox(name, key=f'check{i}'))
        pass
        selected = False
        with cols[1]:
            preview_sufix = st.empty()
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
            with cols[2]:
                dados = {}
                # dados['emissor'] = st.text_input('Emissor', key=f"emissor{st.session_state['seq']}")
                tag = st_tags(label='Emissor', key=f"emissor{st.session_state['seq']}",
                              suggestions=lista_cadastrados(st.session_state['seq'], 'emissor'), maxtags=1)
                dados['emissor'] = tag[0] if tag is not None and len(tag) > 0 else ''

                # dados['doc'] = st.text_input('cpf / cnpj', key=f"doc{st.session_state['seq']}")
                tag = st_tags(label='cpf / cnpj', key=f"doc{st.session_state['seq']}",
                              suggestions=lista_cadastrados(st.session_state['seq'], 'doc'), maxtags=1)
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
            preview_sufix.write(update_prefix(dados))
            with ex:
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

                df = pd.DataFrame(data=items, columns=['item', 'qtd', 'custo'])
                total = df.custo.sum()
                if total < dados['valor']:
                    dif = dados['valor'] - total
                    df = df.append({'item': 'Outros', 'qtd': 1, 'custo': dif}, ignore_index=True)
                elif total > dados['valor']:
                    st.warning("Valor da total nota está menor do que o listado.")
            with cols[2]:
                st.write(df)
                if dados['doc'] is not None:
                    if not cpfcnpj.cpf.validate(dados['doc']) and not cpfcnpj.cnpj.validate(dados['doc']):
                        st.warning("cpf / cnpj inválido")
                if dados['emissor'] is None or dados['emissor'] == '':
                    st.warning("Emissor vazio")
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
                        count = 0
                        for i, file in enumerate(files):
                            if check[i]:
                                name, ext = os.path.splitext(file['name'])
                                save_file(docs_path, f"{prefix}_{i}{ext}", file['body'])
                                count += 1

                        for i in reversed(range(len(files))):
                            if check[i]:
                                del files[i]

                        for k, v in dados.items():
                            if k != 'valor':
                                df[k] = v
                        df['pdf_count'] = count
                        df['pdf_prefix'] = prefix
                        # st.write(df)

                        if os.path.isfile(csv_file_path):
                            db = pd.read_csv(csv_file_path)
                            db = pd.concat([db, df], ignore_index=True)
                            db.to_csv(csv_file_path, index=None)
                        else:
                            df.to_csv(csv_file_path, index=None)
                        # Delete all the items in Session state
                        st.session_state['seq'] += 1
                        ph.button('Próximo')

    pass


def view():
    if st.button('Baixar tudo'):
        ziph = zipfile.ZipFile('all.zip', 'w', zipfile.ZIP_DEFLATED)
        for path in ['pdfs/', 'csv']:
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(path, '..')))
        ziph.close()
        download('all.zip', 'all.zip', 'zip')

    lay_pdfs, lay_table = st.columns([2, 4])
    with lay_table:
        st.title('Tabela')
        if os.path.isfile(csv_file_path):
            db = pd.read_csv(csv_file_path)
            download(csv_file_path, 'tabela.csv', 'csv', 'Baixar tabela')
            st.table(db)

    with lay_pdfs:
        st.title('Arquivos')

        filelist = []
        for root, dirs, files in os.walk("pdfs/"):
            for file in files:
                filename = os.path.join(root, file)
                filelist.append(filename)
                if st.button(file):
                    download(filename, file, 'pdf', file)
    pass


def main():
    if not hasattr(st.session_state, 'page'):
        st.session_state.page = cadastro

    if st.sidebar.button("Adicionar Notas"):
        st.session_state.page = cadastro

    if st.sidebar.button("Visualizar"):
        st.session_state.page = view

    st.session_state.page()


ph = st.empty()
pw = ph.text_input('Senha', type="password")
if 'pass' not in st.session_state or st.session_state['pass'] != st.secrets['senha']:
    if pw is not None:
        st.session_state['pass'] = pw
    if st.session_state['pass'] == st.secrets['senha']:
        ph.empty()
        main()
else:
    ph.empty()
    main()
