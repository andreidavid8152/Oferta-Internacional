import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# Configuracion de la pagina
st.set_page_config(page_title="Ranking de Universidades", page_icon="🎓", layout="wide")


# Funcion para cargar datos
@st.cache_data
def load_data():
    file_path = os.path.join("db", "base.xlsx")
    try:
        df = pd.read_excel(file_path)
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # Normalizar espacios en columnas usadas por filtros
        filter_cols = ["PAIS", "FINANCIAMIENTO", "TIPO", "NIVEL", "FACULTAD ASOCIADA"]
        for col in filter_cols:
            if col in df.columns:
                df[col] = df[col].astype("string").str.strip()
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None


def sort_filter_values(values):
    return sorted(values, key=lambda v: str(v).lower())


# Cargar datos
df = load_data()

if df is not None:
    # Titulo principal
    st.title("🎓 Ranking de Universidades")

    # Seccion de filtros
    st.subheader("🔍 Filtros")

    # Crear 5 columnas para los filtros
    col1, col2, col3, col4, col5 = st.columns(5)

    # Filtro 1: Pais
    with col1:
        paises = ["Todos"] + sort_filter_values(df["PAIS"].dropna().unique().tolist())
        pais_seleccionado = st.selectbox("Pais", paises, key="pais")

    # Aplicar filtro de pais
    if pais_seleccionado != "Todos":
        df_filtrado = df[df["PAIS"] == pais_seleccionado]
    else:
        df_filtrado = df.copy()

    # Filtro 2: Financiamiento (cascada) - Excluir SIN ESPECIFICAR
    with col2:
        financiamientos = ["Todos"] + sort_filter_values(
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
        tipos = ["Todos"] + sort_filter_values(
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
        niveles = ["Todos"] + sort_filter_values(
            df_filtrado["NIVEL"].dropna().unique().tolist()
        )
        nivel_seleccionado = st.selectbox("Nivel", niveles, key="nivel")

    # Aplicar filtro de nivel
    if nivel_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["NIVEL"] == nivel_seleccionado]

    # Filtro 5: Facultad (cascada)
    with col5:
        facultades = ["Todos"] + sort_filter_values(
            df_filtrado["FACULTAD ASOCIADA"].dropna().unique().tolist()
        )
        facultad_seleccionada = st.selectbox("Facultad", facultades, key="facultad")

    # Aplicar filtro de facultad
    if facultad_seleccionada != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["FACULTAD ASOCIADA"] == facultad_seleccionada
        ]

    # Preparar datos para el grafico

    # Agrupar por universidad y sumar matriculados
    df_grafico = df_filtrado[["NOMBRE INSTITUCION", "MATRICULADOS"]].copy()
    df_grafico = df_grafico.rename(columns={"NOMBRE INSTITUCION": "INSTITUCION"})
    df_grafico = df_grafico.groupby("INSTITUCION", as_index=False)["MATRICULADOS"].sum()

    # Truncar nombres de universidades a 50 caracteres con puntos suspensivos
    df_grafico["INSTITUCION"] = df_grafico["INSTITUCION"].apply(
        lambda x: x[:50] + "..." if len(x) > 50 else x
    )

    # Mantener solo el top 10 y ordenar para el grafico
    df_grafico = df_grafico.sort_values("MATRICULADOS", ascending=False).head(10)
    df_grafico = df_grafico.sort_values("MATRICULADOS", ascending=True)

    if len(df_grafico) > 0:
        # Crear grafico de barras horizontales con Plotly
        fig = go.Figure(
            data=[
                go.Bar(
                    y=df_grafico["INSTITUCION"],
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
                "text": "Ranking de Universidades por Total de Matriculados Internacionales",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "color": "#1f77b4"},
            },
            xaxis_title="Total de Matriculados",
            yaxis_title="Universidad",
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

        # Insights generales (no basados en el top 10)
        total_matriculados = int(df_filtrado["MATRICULADOS"].sum())
        total_universidades = df_filtrado["NOMBRE INSTITUCION"].nunique()

        # Tarjetas minimalistas con HTML/CSS personalizado (igual que Dashboard)
        st.subheader("📊 Resumen")
        col1, card1, col2, card2, col3 = st.columns([0.8, 1.2, 0.6, 1.2, 0.8])

        # Tarjeta 1: Total Matriculados
        with card1:
            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                padding: 24px 28px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                color: white;
            ">
                <div style="font-size: 36px; margin-bottom: 10px;">👥</div>
                <div style="font-size: 13px; opacity: 0.95; margin-bottom: 8px; font-weight: 500; letter-spacing: 0.3px;">Total Matriculados</div>
                <div style="font-size: 32px; font-weight: bold; line-height: 1.2;">{total_matriculados:,}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Tarjeta 2: Universidades
        with card2:
            st.markdown(
                f"""
            <div style="
                background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
                padding: 24px 28px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                text-align: center;
                color: white;
            ">
                <div style="font-size: 36px; margin-bottom: 10px;">🏫</div>
                <div style="font-size: 13px; opacity: 0.95; margin-bottom: 8px; font-weight: 500; letter-spacing: 0.3px;">Universidades</div>
                <div style="font-size: 32px; font-weight: bold; line-height: 1.2;">{total_universidades}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No hay datos que mostrar con los filtros seleccionados.")

else:
    st.error(
        "❌ No se pudo cargar el archivo base.xlsx. Verifica que el archivo existe en la carpeta 'db'."
    )
