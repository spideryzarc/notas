import os
import zipfile
import streamlit as st
from utils import download, csv_file_path, show_pdf
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


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
    st.title('Tabela')
    if os.path.isfile(csv_file_path):
        db = pd.read_csv(csv_file_path)
        download(csv_file_path, 'tabela.csv', 'csv')
        # st.table(db)
        gb = GridOptionsBuilder.from_dataframe(db)

        gb.configure_pagination()
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        # gb.configure_side_bar()
        # gb.configure_default_column(groupable=True, value=True, enableRowGroup=True, aggFunc="sum", editable=True)
        gridOptions = gb.build()
        data = AgGrid(db, gridOptions=gridOptions, enable_enterprise_modules=True, height=800,
                      update_mode=GridUpdateMode.SELECTION_CHANGED)
        if len(data['selected_rows']) > 0:
            st.button("deletar")
