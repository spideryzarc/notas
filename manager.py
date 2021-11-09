import os
import zipfile
import streamlit as st
from utils import download,csv_file_path
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder


def page_view():
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
            # st.table(db)
            gb = GridOptionsBuilder.from_dataframe(db)

            gb.configure_pagination()
            gb.configure_side_bar()
            gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
            gridOptions = gb.build()
            AgGrid(db, gridOptions=gridOptions, enable_enterprise_modules=True, height=800)
            # AgGrid(db)

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
