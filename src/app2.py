import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.express as px

# --- LATERAL MENU ---
st.sidebar.title("Navegación")

if "page" not in st.session_state:
    st.session_state.page = "Cuadrantes"  # Default page

if st.sidebar.button("Cuadrantes Trafos"):
    st.session_state.page = "Cuadrantes"
if st.sidebar.button("Incremental"):
    st.session_state.page = "Incremental"

page = st.session_state.page


# --- PAGE 1: CUADRANTES ---
if page == "Cuadrantes":
    # Load data
    data = load_data('trafo_balance.xlsx')
    data['Año_Mes'] = pd.to_datetime(data['Año_Mes'], format='%Y-%m')

    st.title("Visualización de Transformadores por Cuadrante")

    # Filtro de Circuito
    circuitos = ["Todos"] + sorted(data['CIRCUITO'].dropna().unique().tolist())
    selected_circuito = st.selectbox("Selecciona un circuito:", circuitos)

    # Date selection
    start_date = st.date_input("Select Start Date", value=pd.to_datetime('2024/01/01').date())
    end_date = st.date_input("Select End Date", value=data['Año_Mes'].max().date())

    # Filter data based on selected dates
    filtered_data = data[(data['Año_Mes'] >= pd.to_datetime(start_date)) & (data['Año_Mes'] <= pd.to_datetime(end_date))]

    # Filtro por circuito (si no es "Todos")
    if selected_circuito != "Todos":
        filtered_data = filtered_data[filtered_data['CIRCUITO'] == selected_circuito]

    # --- SUBPLOTS DE BARRAS APILADAS POR CUADRANTE ---
    cuadrante_titles = {
        1: "Pérdida <10%",
        2: "Pérdida entre 10% y 80%",
        3: "Medida Inconsistente",
        4: "Sin Macromedidor"
    }
    cuadrantes = filtered_data['cuadrante'].unique()
    cuadrantes.sort()
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[cuadrante_titles.get(c, f"Cuadrante {c}") for c in cuadrantes]
    )

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

    st.markdown("### Comparación de Distribución de Pérdida")

    # Date selectors for comparing distributions
    col1, col2 = st.columns(2)
    with col1:
        compare_date_1 = st.date_input("Fecha 1", value=pd.to_datetime('2024/12/01').date(), key="comp1")
    with col2:
        compare_date_2 = st.date_input("Fecha 2", value=data['Año_Mes'].max().date(), key="comp2")

        
    # Cuadrantes 1 y 2 solamente
    cuadrante_1_2 = data[data['cuadrante'].isin([1, 2])]

    # Datos para cada fecha
    date1_data = cuadrante_1_2[cuadrante_1_2['Año_Mes'] == pd.to_datetime(compare_date_1)]
    date2_data = cuadrante_1_2[cuadrante_1_2['Año_Mes'] == pd.to_datetime(compare_date_2)]


    # Extraer 'perdida' y convertir a porcentaje sin decimales
    perdida_1 = (date1_data['%_Perdida'] * 100).dropna().round(0)
    perdida_2 = (date2_data['%_Perdida'] * 100).dropna().round(0)

    # Crear el KDE plot con bell curves
    fig0 = ff.create_distplot(
        [perdida_1, perdida_2],
        group_labels=[f"{compare_date_1}", f"{compare_date_2}"],
        show_hist=False,
        show_rug=False,
        bin_size=1
    )

    # Ajustar layout
    fig0.update_layout(
        title="Distribución de Pérdida (Curvas KDE)",
        xaxis_title="Pérdida (%)",
        yaxis_title="Densidad",
    )

    # Eje X sin decimales
    fig0.update_xaxes(tickformat=",d")

    # Mostrar gráfico
    st.plotly_chart(fig0, use_container_width=True)

    # Crear DataFrame combinado
    df_dist = pd.DataFrame({
        '%_Perdida': pd.concat([
            date1_data['%_Perdida'] * 100,
            date2_data['%_Perdida'] * 100
        ]),
        'fecha': ([str(compare_date_1)] * len(date1_data)) + ([str(compare_date_2)] * len(date2_data))
    })

    # Histograma superpuesto con transparencia
    fig = px.histogram(
        df_dist,
        x="%_Perdida",
        color="fecha",
        color_discrete_sequence=["blue", "red"],
        nbins=20,
        barmode="overlay",
        opacity=0.6,
        labels={"%_Perdida": "Pérdida (%)"},
        title="Distribución Comparada de Pérdida"
    )

    # Formatear eje x como entero sin decimales
    fig.update_xaxes(tickformat=",d")

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    pass

# --- PAGE 2: INCREMENTALES ---
elif page == "Incremental":
    st.title("Incrementales por Línea y Tipo Incremental")

    # --- Load and filter incremental data ---
    data_inc = load_data('incremental_clasificado_2025_04.xlsx')
    data_inc['FECHA_DE_EJECUCION'] = pd.to_datetime(data_inc['FECHA_DE_EJECUCION'])
    data_inc['Año_Mes'] = data_inc['FECHA_DE_EJECUCION'].dt.to_period('M').dt.to_timestamp()

    # --- Load and filter no incremental data ---
    data_noinc = load_data('no_incremental_2025_04_1.xlsx')
    data_noinc['FECHA_DE_EJECUCION'] = pd.to_datetime(data_noinc['FECHA_DE_EJECUCION'])
    data_noinc['Año_Mes'] = data_noinc['FECHA_DE_EJECUCION'].dt.to_period('M').dt.to_timestamp()

    # --- IRREGULARIDAD filter (shared) ---
    irregularidades = sorted(
        set(data_inc['IRREGULARIDAD'].dropna().unique()).union(
            set(data_noinc['IRREGULARIDAD'].dropna().unique())
        )
    )
    irregularidad_sel = st.selectbox("Filtrar por IRREGULARIDAD", options=["Todas"] + irregularidades)

    if irregularidad_sel != "Todas":
        data_inc = data_inc[data_inc['IRREGULARIDAD'] == irregularidad_sel]
        data_noinc = data_noinc[data_noinc['IRREGULARIDAD'] == irregularidad_sel]

    # --- LINEA filter (shared) ---
    lineas = sorted(
        set(data_inc['LINEA'].dropna().unique()).union(
            set(data_noinc['LINEA'].dropna().unique())
        )
    )
    lineas_options = ["Todas"] + list(lineas)
    linea_sel = st.selectbox("Filtrar por LINEA", options=lineas_options)

    if linea_sel != "Todas":
        data_inc = data_inc[data_inc['LINEA'] == linea_sel]
        data_noinc = data_noinc[data_noinc['LINEA'] == linea_sel]

    # --- Incrementales plot ---
    filtered_inc = data_inc[data_inc['total_periodos'] >= 6]

    agg_inc = (
        filtered_inc.groupby(['Año_Mes', 'tipo_incremento'], as_index=False)
        .agg({'PRODUCTO': 'count'})
        .rename(columns={'PRODUCTO': 'Cantidad'})
    )
    total_per_mes = agg_inc.groupby('Año_Mes')['Cantidad'].transform('sum')
    agg_inc['Porcentaje'] = agg_inc['Cantidad'] / total_per_mes * 100

    fig2 = go.Figure()
    for tipo in agg_inc['tipo_incremento'].unique():
        df_tipo = agg_inc[agg_inc['tipo_incremento'] == tipo]
        fig2.add_trace(go.Bar(
            x=df_tipo['Año_Mes'],
            y=df_tipo['Cantidad'],
            name=str(tipo),
            customdata=df_tipo['Porcentaje'].round(1),
            hovertemplate=(
                'Año-Mes: %{x}<br>'
                'Cantidad: %{y}<br>'
                'Porcentaje: %{customdata}%<extra></extra>'
            )
        ))

    fig2.update_layout(
        barmode='stack',
        title=f"Cantidad de PRODUCTOs Incrementales por Mes y Tipo Incremental" + (f" para LINEA {linea_sel}" if linea_sel != "Todas" else ""),
        xaxis_title="Año-Mes",
        yaxis_title="Cantidad"
    )
    st.plotly_chart(fig2)

    # --- No Incrementales plot ---
    st.title("No Incrementales por Categoría")

    #category renaming
    data_noinc['Categoría'] = data_noinc['Categoría'].replace({
        'Verde(<25%)': '<25%',
        'Amarillo(25%-80%)': '25%-80%',
        'Rojo(>80%)': '>80%'
    })

    # Update category order and colors as needed
    categoria_order = ["<25%", "25%-80%",">80%"]
    categoria_colors = {
        "<25%": "#99c140",
        "25%-80%": "#e7b416",
        ">80%": "#cc3232"
    }

    agg_noinc = (
        data_noinc.groupby(['Año_Mes', 'Categoría'], as_index=False)
        .agg({'PRODUCTO': 'count'})
        .rename(columns={'PRODUCTO': 'Cantidad'})
    )
    total_per_mes_noinc = agg_noinc.groupby('Año_Mes')['Cantidad'].transform('sum')
    agg_noinc['Porcentaje'] = agg_noinc['Cantidad'] / total_per_mes_noinc * 100

    fig3 = go.Figure()
    for cat in categoria_order:
        df_cat = agg_noinc[agg_noinc['Categoría'] == cat]
        fig3.add_trace(go.Bar(
            x=df_cat['Año_Mes'],
            y=df_cat['Cantidad'],
            name=str(cat),
            marker_color=categoria_colors.get(cat, None),
            customdata=df_cat['Porcentaje'].round(1),
            hovertemplate=(
                'Año-Mes: %{x}<br>'
                'Cantidad: %{y}<br>'
                'Porcentaje: %{customdata}%<extra></extra>'
            )
        ))

    fig3.update_layout(
        barmode='stack',
        title="Cantidad de No Incrementales por Mes y Categoría" + (f" para LINEA {linea_sel}" if linea_sel != "Todas" else ""),
        xaxis_title="Año-Mes",
        yaxis_title="Cantidad"
        )
    st.plotly_chart(fig3)
    pass