# import pandas as pd
import streamlit as st

from utils import *

from manager import page_view
from register import page_cadastro

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

if 'seq' not in st.session_state:
    st.session_state['seq'] = 0


def main():
    if not hasattr(st.session_state, 'page'):
        st.session_state.page = page_cadastro

    if st.sidebar.button("Adicionar Notas"):
        st.session_state.page = page_cadastro

    if st.sidebar.button("Visualizar"):
        st.session_state.page = page_view

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
