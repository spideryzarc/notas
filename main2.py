import streamlit as st

from dash import page_dash_gastos
from utils import *

from manager import page_arquivos, page_tabela, page_delete, page_edit_notas, page_edit_fornecedores
from register import page_cadastro

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

if 'seq' not in st.session_state:
    st.session_state['seq'] = 0


def main():
    if not hasattr(st.session_state, 'page'):
        st.session_state.page = page_dash_gastos

    if st.sidebar.button("Adicionar Notas"):
        st.session_state.page = page_cadastro

    if st.sidebar.button("Deletar Notas"):
        st.session_state.page = page_delete

    if st.sidebar.button("Vizualizar Arquivos"):
        st.session_state.page = page_arquivos

    if st.sidebar.button("Vizualizar Tabela"):
        st.session_state.page = page_tabela

    if st.sidebar.button("Editar Tabela de Notas"):
        st.session_state.page = page_edit_notas

    if st.sidebar.button("Editar Tabela de Fornecedores"):
        st.session_state.page = page_edit_fornecedores

    if st.sidebar.button("Gráficos"):
        st.session_state.page = page_dash_gastos

    # if st.sidebar.button("fix outros"):
    #     df = pd.read_csv(notas_csv_file, parse_dates=['date'])[notas_cols_order]
    #     fornecedores = pd.read_csv(fornecedores_csv_file, index_col='nome')
    #     df.loc[df['item'] == 'Outros', 'item'] = df.loc[df['item'] == 'Outros', 'emissor'].map(fornecedores['classe'])
    #     df.to_csv(notas_csv_file, index=None)

    st.session_state.page()


# main()
lay = st.columns([4, 2, 4])
ph = lay[1].empty()
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
