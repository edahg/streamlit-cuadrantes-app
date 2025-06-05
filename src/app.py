import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_data
import plotly.express as px
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

# Aggregate data for the chart
agg_data = (
    filtered_data
    .groupby(['Año_Mes', 'Cambio_cuadrante'], as_index=False)
    .agg({'TRAFOACTUAL': 'count'})  # or 'count' if you want counts
)

# Stacked bar chart with Plotly (using aggregated data)
fig = px.bar(
    agg_data,
    x="Año_Mes",
    y="TRAFOACTUAL",
    color="Cambio_cuadrante",
    title="Cuenta_Trafo por Año-Mes y Cambio de Cuadrante",
    labels={"Cuenta_Trafo": "Cuenta Trafo", "Año_Mes": "Año-Mes"},
)

# Show the chart and capture click event
selected_points = plotly_events(fig, click_event=True, select_event=False)

if selected_points:
    point = selected_points[0]
    clicked_date = point["x"]
    clicked_cambio = point["curveNumber"]

    # Get the actual Cambio_cuadrante value
    cambio_values = agg_data["Cambio_cuadrante"].unique()
    if 0 <= clicked_cambio < len(cambio_values):
        clicked_cambio_value = cambio_values[clicked_cambio]
        table_data = filtered_data[
            (filtered_data["Cambio_cuadrante"] == clicked_cambio_value) &
            (filtered_data["Año_Mes"] == pd.to_datetime(clicked_date))
        ]
        st.subheader(f"Detalle para {clicked_cambio_value} en {clicked_date}")
        st.dataframe(table_data)
    else:
        st.info("Haz clic en una barra para ver los detalles.")
else:
    st.info("Haz clic en una barra para ver los detalles.")