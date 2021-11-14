import os
import zipfile
import streamlit as st
from utils import download, notas_csv_file, show_pdf, docs_path, notas_cols_order
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import ast


def page_arquivos():
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

    lay_pdfs, lay_view = st.columns([2, 4])

    with lay_pdfs:
        st.title('Arquivos')
        filelist = []
        for root, dirs, files in os.walk("pdfs/"):
            for file in files:
                filename = os.path.join(root, file)
                filelist.append(filename)
                if st.button(file):
                    with lay_view:
                        download(filename, file, 'pdf')
                        name, ext = os.path.splitext(file)
                        with open(filename, 'rb') as f:
                            show_pdf(f.read(), ext)
    pass


def page_tabela():
    st.markdown('## Tabela')
    if os.path.isfile(notas_csv_file):
        df = pd.read_csv(notas_csv_file)[notas_cols_order]
        download(notas_csv_file, 'tabela.csv', 'csv')

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_column('custo', valueFormatter="'R$\t' + data.custo.toFixed(2)", aggFunc='sum')
        gb.configure_columns(['emissor', 'date', 'classe', 'arquivos'], aggFunc='first')
        # gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        # gb.configure_side_bar()
        gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=False)
        data = AgGrid(df, gridOptions=gb.build(), enable_enterprise_modules=True, height=600,
                      update_mode=GridUpdateMode.SELECTION_CHANGED)
    else:
        st.error("Arquivo não encontrado.")


def page_delete():
    if os.path.isfile(notas_csv_file):
        df = pd.read_csv(notas_csv_file)
        df = df[['id_nota', 'emissor', 'custo', 'date', 'arquivos']].groupby('id_nota', as_index=False).agg(
            {'emissor': 'first', 'date': 'first', 'custo': 'sum', 'arquivos': 'first'})
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination()
        gb.configure_column('custo', valueFormatter="'R$\t' + data.custo.toFixed(2)", aggFunc='sum')
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        # gb.configure_side_bar()
        # gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
        st.markdown("## Selecione notas para sua remoção do cadastro.")
        data = AgGrid(df, gridOptions=gb.build(), enable_enterprise_modules=True, height=600,
                      update_mode=GridUpdateMode.SELECTION_CHANGED)
        if st.button("deletar"):
            selected_rows = data['selected_rows']
            if len(selected_rows) > 0:
                id_rm_list = [selected_rows[i]["id_nota"] for i in range(len(selected_rows))]
                df = pd.read_csv(notas_csv_file)
                df = df[~df['id_nota'].isin(id_rm_list)]
                df.to_csv(notas_csv_file, index=None)
                for row in selected_rows:
                    arquivos = ast.literal_eval(row['arquivos'])
                    for arq in arquivos:
                        file_path = os.path.join(docs_path, arq)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        else:
                            st.error(f'Erro ao deletar arquivo. {file_path} não existe.')
                st.experimental_rerun()
            else:
                st.warning("Nenhuma linha foi selecionada.")


def page_edit_notas():
    st.markdown('## Tabela em modo de edição')
    if os.path.isfile(notas_csv_file):
        df = pd.read_csv(notas_csv_file)
        gb = GridOptionsBuilder.from_dataframe(df[notas_cols_order])
        gb.configure_pagination()
        gb.configure_columns(['arquivos', 'id_nota'], editable=False)
        gb.configure_column('custo', valueFormatter="'R$\t' + data.custo.toFixed(2)", aggFunc='sum')
        # gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        # gb.configure_side_bar()
        gb.configure_default_column(groupable=False, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
        data = AgGrid(df, gridOptions=gb.build(), enable_enterprise_modules=True, height=600,
                      update_mode=GridUpdateMode.MODEL_CHANGED, key=f"{st.session_state['seq']}")
        if st.button('Salvar alterações'):
            df = data['data']
            df.to_csv(notas_csv_file, index=None)
            st.success('Tabela atualizada com sucesso')
            # st.session_state['seq'] += 1
            # st.experimental_rerun()
        if st.button('Descartar alterações'):
            st.session_state['seq'] += 1
            st.experimental_rerun()

    else:
        st.error("Arquivo não encontrado.")
