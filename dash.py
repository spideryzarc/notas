import streamlit as st
import pandas as pd
import plotly.express as plotly
import statsmodels.api as sm

from utils import notas_csv_file, notas_cols_order, fornecedores_csv_file


def plot_cost_grouped(df, field, title, alias=None):
    data = df[[field, 'custo']].groupby(field).sum()
    data.index = data.index.str[:30]
    data.sort_values('custo', ascending=True, inplace=True)
    fig = plotly.bar(data.tail(15), orientation='h', height=600, labels={field: field if alias is None else alias})
    fig.update_layout(showlegend=False)
    fig.update_layout(title=title)
    # if alias is not None:
    #     fig.update_layout(labels={field: alias})
    st.plotly_chart(fig, use_container_width=True)


def page_dash_gastos():
    st.markdown('## Gastos')
    col = st.columns([1, 1])
    df = pd.read_csv(notas_csv_file, parse_dates=['date'])[notas_cols_order]
    fornecedores = pd.read_csv(fornecedores_csv_file, index_col='nome')
    df['classe'] = df['emissor'].map(fornecedores['classe'])

    ## custo acumulado
    data = df[['date', 'custo']].groupby('date').sum().sort_index()
    data['acc'] = data['custo'].cumsum()
    fig = plotly.line(x=data.index, y=data['acc'], height=600)
    fig.update_layout(title="Gastos Acumulados")
    col[0].plotly_chart(fig, use_container_width=True)

    ## custo por fornecedor
    with col[1]:
        plot_cost_grouped(df, 'emissor', 'Gasto x Fornecedor', 'Fornecedores')
        plot_cost_grouped(df, 'classe', 'Gasto x Classe', 'Classes')
    with col[0]:
        plot_cost_grouped(df, 'item', 'Gasto x Produto', 'Produto')
