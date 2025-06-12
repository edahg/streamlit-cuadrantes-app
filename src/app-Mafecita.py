import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_plotly_events import plotly_events

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

# Keep track of trace order for mapping clicks
trace_cuadrante = []
trace_cambio = []

for idx, cuadrante in enumerate(cuadrantes):
    row = idx // 2 + 1
    col = idx % 2 + 1
    df_cuad = filtered_data[filtered_data['cuadrante'] == cuadrante]
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
                name=f"{cambio}",
                showlegend=(idx == 0)
            ),
            row=row, col=col
        )
        trace_cuadrante.append(cuadrante)
        trace_cambio.append(cambio)

fig.update_layout(
    title="Transformadores por Cuadrante y Cambio de Cuadrante",
    barmode='stack',
    height=700
)

selected_points = plotly_events(fig, click_event=True, select_event=False)

if selected_points:
    point = selected_points[0]
    clicked_trace = point["curveNumber"]
    clicked_date = point["x"]

    # Map trace to cuadrante and cambio_cuadrante
    if 0 <= clicked_trace < len(trace_cuadrante):
        clicked_cuadrante = trace_cuadrante[clicked_trace]
        clicked_cambio = trace_cambio[clicked_trace]
        table_data = filtered_data[
            (filtered_data["cuadrante"] == clicked_cuadrante) &
            (filtered_data["Cambio_cuadrante"] == clicked_cambio) &
            (filtered_data["Año_Mes"] == pd.to_datetime(clicked_date))
        ]
        st.subheader(f"Detalle para Cuadrante {clicked_cuadrante}, Cambio {clicked_cambio} en {clicked_date}")
        st.dataframe(table_data)
    else:
        st.info("Haz clic en una barra para ver los detalles.")
else:
    st.info("Haz clic en una barra para ver los detalles.")