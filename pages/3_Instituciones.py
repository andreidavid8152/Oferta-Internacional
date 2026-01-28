import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Instituciones", page_icon="🏫", layout="wide"
)


# Función para cargar datos
@st.cache_data
def load_data():
    file_path = os.path.join("db", "base.xlsx")
    try:
        df = pd.read_excel(file_path)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None


# Cargar datos
df = load_data()

if df is not None:
    # Título principal
    st.title("🏫 Análisis Institucional")

    # Sección de filtros
    st.subheader("🔍 Filtros")

    # Crear 5 columnas para los filtros
    col1, col2, col3, col4, col5 = st.columns(5)

    # Filtro 1: País
    with col1:
        paises = ["Todos"] + sorted(df["PAIS"].dropna().unique().tolist())
        pais_seleccionado = st.selectbox("País", paises, key="pais")

    # Aplicar filtro de país
    if pais_seleccionado != "Todos":
        df_filtrado = df[df["PAIS"] == pais_seleccionado]
    else:
        df_filtrado = df.copy()

    # Filtro 2: Financiamiento (cascada) - Excluir SIN ESPECIFICAR
    with col2:
        financiamientos = ["Todos"] + sorted(
            [
                f
                for f in df_filtrado["FINANCIAMIENTO"].dropna().unique().tolist()
                if f != "SIN ESPECIFICAR"
            ]
        )
        financiamiento_seleccionado = st.selectbox(
            "Financiamiento", financiamientos, key="financiamiento"
        )

    # Aplicar filtro de financiamiento
    if financiamiento_seleccionado != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["FINANCIAMIENTO"] == financiamiento_seleccionado
        ]

    # Filtro 3: Tipo (cascada) - Excluir SIN CLASIFICAR
    with col3:
        tipos = ["Todos"] + sorted(
            [
                t
                for t in df_filtrado["TIPO"].dropna().unique().tolist()
                if t != "SIN CLASIFICAR"
            ]
        )
        tipo_seleccionado = st.selectbox("Tipo", tipos, key="tipo")

    # Aplicar filtro de tipo
    if tipo_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["TIPO"] == tipo_seleccionado]

    # Filtro 4: Nivel (cascada)
    with col4:
        niveles = ["Todos"] + sorted(df_filtrado["NIVEL"].dropna().unique().tolist())
        nivel_seleccionado = st.selectbox("Nivel", niveles, key="nivel")

    # Aplicar filtro de nivel
    if nivel_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["NIVEL"] == nivel_seleccionado]

    # Filtro 5: Facultad (cascada)
    with col5:
        facultades = ["Todos"] + sorted(
            df_filtrado["FACULTAD ASOCIADA"].dropna().unique().tolist()
        )
        facultad_seleccionada = st.selectbox("Facultad", facultades, key="facultad")

    # Aplicar filtro de facultad
    if facultad_seleccionada != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["FACULTAD ASOCIADA"] == facultad_seleccionada
        ]

    # Preparar datos para el gráfico bubble chart
    st.subheader("📊 Análisis de Carreras por Instituciones")

    # Agrupar por carrera y calcular métricas
    df_bubble = (
        df_filtrado.groupby("NOMBRE CARRERA")
        .agg(
            {
                "NOMBRE INSTITUCION": "nunique",  # Número de instituciones
                "MATRICULADOS": "sum",  # Total de matriculados
                "PAIS": "nunique",  # Número de países
                "NIVEL": lambda x: (
                    x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
                ),  # Nivel más frecuente
            }
        )
        .reset_index()
    )

    # Renombrar columnas
    df_bubble.columns = [
        "CARRERA",
        "NUM_INSTITUCIONES",
        "TOTAL_MATRICULADOS",
        "NUM_PAISES",
        "NIVEL",
    ]

    # Truncar nombres de carreras para mejor visualización
    df_bubble["CARRERA_TRUNCADA"] = df_bubble["CARRERA"].apply(
        lambda x: x[:40] + "..." if len(x) > 40 else x
    )

    # Definir colores por nivel
    color_map = {
        "PREGRADO": "#3b82f6",  # Azul
        "POSGRADO": "#ef4444",  # Rojo
    }

    df_bubble["COLOR"] = (
        df_bubble["NIVEL"].map(color_map).fillna("#9ca3af")
    )  # Gris por defecto

    if len(df_bubble) > 0:
        # Escalado dinamico de burbujas para una vista general consistente
        max_paises = max(1, int(df_bubble["NUM_PAISES"].max()))
        num_burbujas = len(df_bubble)
        if num_burbujas <= 25:
            size_max = 60
        elif num_burbujas <= 60:
            size_max = 48
        else:
            size_max = 38
        sizeref = 2.0 * max_paises / (size_max**2)

        # Crear bubble chart con Plotly
        fig = go.Figure()

        # Agregar burbujas por cada nivel
        for nivel in df_bubble["NIVEL"].unique():
            df_nivel = df_bubble[df_bubble["NIVEL"] == nivel]

            fig.add_trace(
                go.Scatter(
                    x=df_nivel["NUM_INSTITUCIONES"],
                    y=df_nivel["TOTAL_MATRICULADOS"],
                    mode="markers",
                    name=nivel,
                    marker=dict(
                        size=df_nivel["NUM_PAISES"],
                        color=(
                            df_nivel["COLOR"].iloc[0]
                            if len(df_nivel) > 0
                            else "#9ca3af"
                        ),
                        opacity=0.7,
                        line=dict(width=2, color="white"),
                        sizemode="area",
                        sizeref=sizeref,
                        sizemin=6,
                    ),
                    text=[
                        f"<b>{carrera}</b><br>"
                        + f"Instituciones: {inst}<br>"
                        + f"Matriculados: {mat:,}<br>"
                        + f"Países: {pais}<br>"
                        + f"Nivel: {nivel}"
                        for carrera, inst, mat, pais, nivel in zip(
                            df_nivel["CARRERA_TRUNCADA"],
                            df_nivel["NUM_INSTITUCIONES"],
                            df_nivel["TOTAL_MATRICULADOS"],
                            df_nivel["NUM_PAISES"],
                            df_nivel["NIVEL"],
                        )
                    ],
                    hovertemplate="%{text}<extra></extra>",
                )
            )

        # Calcular rangos con padding para mejor visualización
        x_min, x_max = (
            df_bubble["NUM_INSTITUCIONES"].min(),
            df_bubble["NUM_INSTITUCIONES"].max(),
        )
        y_min, y_max = (
            df_bubble["TOTAL_MATRICULADOS"].min(),
            df_bubble["TOTAL_MATRICULADOS"].max(),
        )

        # Agregar padding del 20% en cada lado
        x_padding = max(1, (x_max - x_min) * 0.2)
        y_padding_log = 0.3  # Padding en escala logarítmica

        fig.update_layout(
            title={
                "text": "Análisis de Carreras: Instituciones vs Matriculados vs Países",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "color": "#1f77b4"},
            },
            xaxis_title="Número de Instituciones",
            yaxis_title="Total de Matriculados (escala logarítmica)",
            height=700,
            hovermode="closest",
            plot_bgcolor="rgba(240, 240, 240, 0.5)",
            paper_bgcolor="white",
            font=dict(family="Arial, sans-serif", size=12),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray",
                zeroline=False,
                type="linear",
                range=[max(0, x_min - x_padding), x_max + x_padding],
                autorange=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray",
                zeroline=False,
                type="log",
                autorange=True,
            ),
            margin=dict(l=100, r=100, t=100, b=100),
            showlegend=False,
        )

        col1, col2, col3, col4 = st.columns(4)

        # Obtener el registro con más matriculados (estrella)
        estrella_idx = df_bubble["TOTAL_MATRICULADOS"].idxmax()
        estrella = df_bubble.loc[estrella_idx]

        # Obtener carrera con más instituciones
        mas_instituciones_idx = df_bubble["NUM_INSTITUCIONES"].idxmax()
        mas_instituciones = df_bubble.loc[mas_instituciones_idx]

        # Obtener carrera con más países
        mas_paises_idx = df_bubble["NUM_PAISES"].idxmax()
        mas_paises = df_bubble.loc[mas_paises_idx]

        with col1:
            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                color: white;
                min-height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 28px; margin-bottom: 8px;">⭐</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Carrera Estrella</div>
                <div style="font-size: 14px; font-weight: bold; line-height: 1.2; word-wrap: break-word;">{estrella['CARRERA_TRUNCADA']}</div>
                <div style="font-size: 11px; opacity: 0.9; margin-top: 5px;">{estrella['TOTAL_MATRICULADOS']:,} matriculados</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
                padding: 20px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                color: white;
                min-height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 28px; margin-bottom: 8px;">🏢</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Más Instituciones</div>
                <div style="font-size: 14px; font-weight: bold; line-height: 1.2; word-wrap: break-word;">{mas_instituciones['CARRERA_TRUNCADA']}</div>
                <div style="font-size: 11px; opacity: 0.9; margin-top: 5px;">{int(mas_instituciones['NUM_INSTITUCIONES'])} instituciones</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                padding: 20px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                color: white;
                min-height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 28px; margin-bottom: 8px;">🌍</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Mayor Alcance Global</div>
                <div style="font-size: 14px; font-weight: bold; line-height: 1.2; word-wrap: break-word;">{mas_paises['CARRERA_TRUNCADA']}</div>
                <div style="font-size: 11px; opacity: 0.9; margin-top: 5px;">{int(mas_paises['NUM_PAISES'])} países</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
                padding: 20px 25px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                color: white;
                min-height: 160px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 28px; margin-bottom: 8px;">📋</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Total Carreras</div>
                <div style="font-size: 28px; font-weight: bold;">{len(df_bubble)}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos que mostrar con los filtros seleccionados.")

else:
    st.error(
        "⚠️ No se pudo cargar el archivo base.xlsx. Verifica que el archivo existe en la carpeta 'db'."
    )
