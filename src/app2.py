import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load data
data = load_data('trafo_balance.xlsx')
data['Año_Mes'] = pd.to_datetime(data['Año_Mes'], format='%Y-%m')

st.title("Visualización de Transformadores por Cuadrante")

# Date selection
start_date = st.date_input("Select Start Date", value=data['Año_Mes'].min().date())
end_date = st.date_input("Select End Date", value=data['Año_Mes'].max().date())

# Filter data based on selected dates
filtered_data = data[(data['Año_Mes'] >= pd.to_datetime(start_date)) & (data['Año_Mes'] <= pd.to_datetime(end_date))]

# --- SUBPLOTS DE BARRAS APILADAS POR CUADRANTE ---
cuadrantes = filtered_data['cuadrante'].unique()
cuadrantes.sort()
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[f"Cuadrante {c}" for c in cuadrantes]
)

for idx, cuadrante in enumerate(cuadrantes):
    row = idx // 2 + 1
    col = idx % 2 + 1
    df_cuad = filtered_data[filtered_data['Cuadrante'] == cuadrante]
    agg = (
        df_cuad.groupby(['Año_Mes', 'Cambio_cuadrante'], as_index=False)
        .agg({'TRAFOACTUAL': 'count'})
    )
    for cambio in agg['Cambio_cuadrante'].unique():
        df_cambio = agg[agg['Cambio_cuadrante'] == cambio]
        fig.add_trace(
            go.Bar(
                x=df_cambio['Año_Mes'],
                y=df_cambio['TRAFOACTUAL'],
                name=str(cambio),
                showlegend=(idx == 0)
            ),
            row=row, col=col
        )

fig.update_layout(
    title="Transformadores por Cuadrante y Cambio de Cuadrante",
    barmode='stack',
    height=700
)

st.plotly_chart(fig)