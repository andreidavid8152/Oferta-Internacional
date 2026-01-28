import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuración de la página
st.set_page_config(page_title="Ranking de Carreras", page_icon="📊", layout="wide")


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
    st.title("📊 Ranking de Carreras - Matriculados Internacionales")

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

    # Preparar datos para el gráfico
    st.subheader("📈 Ranking de Carreras")

    # Agrupar por carrera y sumar matriculados
    df_grafico = df_filtrado[["NOMBRE CARRERA", "MATRICULADOS"]].copy()
    df_grafico = df_grafico.rename(columns={"NOMBRE CARRERA": "CARRERA"})
    df_grafico = df_grafico.groupby("CARRERA", as_index=False)["MATRICULADOS"].sum()

    # Truncar nombres de carreras a 50 caracteres con puntos suspensivos
    df_grafico["CARRERA"] = df_grafico["CARRERA"].apply(
        lambda x: x[:50] + "..." if len(x) > 50 else x
    )

    # Ordenar por matriculados de mayor a menor (para el gráfico)
    df_grafico = df_grafico.sort_values("MATRICULADOS", ascending=True)

    if len(df_grafico) > 0:
        # Crear gráfico de barras horizontales con Plotly
        fig = go.Figure(
            data=[
                go.Bar(
                    y=df_grafico["CARRERA"],
                    x=df_grafico["MATRICULADOS"],
                    orientation="h",
                    marker=dict(
                        color=df_grafico["MATRICULADOS"],
                        colorscale="Viridis",
                        showscale=True,
                        colorbar=dict(
                            title="Total<br>Matriculados", thickness=15, len=0.7
                        ),
                    ),
                    text=df_grafico["MATRICULADOS"].apply(lambda x: f"{x:,}"),
                    textposition="auto",
                    hovertemplate="<b>%{y}</b><br>Total Matriculados: %{x:,}<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title={
                "text": "Ranking de Carreras por Total de Matriculados Internacionales",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "color": "#1f77b4"},
            },
            xaxis_title="Total de Matriculados",
            yaxis_title="Carrera",
            height=max(400, len(df_grafico) * 30 + 100),
            hovermode="closest",
            margin=dict(l=300, r=50, t=100, b=50),
            plot_bgcolor="rgba(240, 240, 240, 0.5)",
            paper_bgcolor="white",
            font=dict(family="Arial, sans-serif", size=12),
            xaxis=dict(
                showgrid=True, gridwidth=1, gridcolor="lightgray", zeroline=False
            ),
            yaxis=dict(showgrid=False),
        )

        col1, col2, col3, col4 = st.columns(4)

        # Obtener nombres de carreras y calcular tamaño de fuente dinámico
        carrera_mayor = df_grafico.iloc[-1]["CARRERA"]
        carrera_menor = df_grafico.iloc[0]["CARRERA"]

        # Calcular tamaño de fuente dinámico (entre 12 y 20px)
        font_size_mayor = max(12, min(20, 300 // len(carrera_mayor)))
        font_size_menor = max(12, min(20, 300 // len(carrera_menor)))

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
                <div style="font-size: 28px; margin-bottom: 8px;">📋</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Total Carreras</div>
                <div style="font-size: 28px; font-weight: bold;">{len(df_grafico)}</div>
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
                <div style="font-size: 28px; margin-bottom: 8px;">🎯</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Mayor Demanda</div>
                <div style="font-size: {font_size_mayor}px; font-weight: bold; line-height: 1.2; word-wrap: break-word;">{carrera_mayor}</div>
                <div style="font-size: 11px; opacity: 0.9; margin-top: 5px;">{df_grafico.iloc[-1]['MATRICULADOS']:,}</div>
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
                <div style="font-size: 28px; margin-bottom: 8px;">📉</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Menor Demanda</div>
                <div style="font-size: {font_size_menor}px; font-weight: bold; line-height: 1.2; word-wrap: break-word;">{carrera_menor}</div>
                <div style="font-size: 11px; opacity: 0.9; margin-top: 5px;">{df_grafico.iloc[0]['MATRICULADOS']:,}</div>
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
                <div style="font-size: 28px; margin-bottom: 8px;">📊</div>
                <div style="font-size: 12px; opacity: 0.95; margin-bottom: 6px; font-weight: 500;">Promedio</div>
                <div style="font-size: 28px; font-weight: bold;">{df_grafico['MATRICULADOS'].mean():,.0f}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.plotly_chart(fig, use_container_width=True)
    st.error(
        "⚠️ No se pudo cargar el archivo base.xlsx. Verifica que el archivo existe en la carpeta 'db'."
    )
