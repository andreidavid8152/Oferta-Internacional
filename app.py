import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Oferta Internacional", page_icon="🎓", layout="wide")

# Título de la aplicación
st.title("📊 Oferta Internacional - Análisis de Matrículas")


# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel("db/data.xlsx")
    return df


# Cargar el dataset
try:
    df = load_data()

    st.subheader("🔍 Filtros")

    # Crear columnas para los filtros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Filtro 1: PAIS
        paises_disponibles = ["Todos"] + sorted(df["PAIS"].dropna().unique().tolist())
        pais_seleccionado = st.selectbox("1. Seleccione PAÍS", paises_disponibles)

    # Filtrar datos según PAIS
    if pais_seleccionado != "Todos":
        df_filtrado = df[df["PAIS"] == pais_seleccionado].copy()
    else:
        df_filtrado = df.copy()

    with col2:
        # Filtro 2: NIVEL
        niveles_disponibles = ["Todos"] + sorted(
            df_filtrado["NIVEL"].dropna().unique().tolist()
        )
        nivel_seleccionado = st.selectbox("2. Seleccione NIVEL", niveles_disponibles)

    # Filtrar datos según NIVEL
    if nivel_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["NIVEL"] == nivel_seleccionado].copy()

    with col3:
        # Filtro 3: DESC CINE CAMPO AMPLIO (en cascada)
        campos_amplios_disponibles = ["Todos"] + sorted(
            df_filtrado["DESC CINE CAMPO AMPLIO"].dropna().unique().tolist()
        )
        campo_amplio_seleccionado = st.selectbox(
            "3. Seleccione CINE CAMPO AMPLIO", campos_amplios_disponibles
        )

    # Filtrar datos según CAMPO AMPLIO
    if campo_amplio_seleccionado != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["DESC CINE CAMPO AMPLIO"] == campo_amplio_seleccionado
        ].copy()

    with col4:
        # Filtro 4: DESC CINE CAMPO ESPECIFICO (en cascada)
        campos_especificos_disponibles = ["Todos"] + sorted(
            df_filtrado["DESC CINE CAMPO ESPECIFICO"].dropna().unique().tolist()
        )
        campo_especifico_seleccionado = st.selectbox(
            "4. Seleccione CINE CAMPO ESPECÍFICO", campos_especificos_disponibles
        )

    # Filtrar datos según CAMPO ESPECÍFICO
    if campo_especifico_seleccionado != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["DESC CINE CAMPO ESPECIFICO"] == campo_especifico_seleccionado
        ].copy()

    # Seleccionar columnas a mostrar (sin PAIS)
    df_tabla = df_filtrado[["NOMBRE CARRERA", "MATRICULADOS"]].copy()

    st.markdown("---")

    st.subheader("Tabla")

    # Mostrar métricas
    col_izq, col1, col2, col3, col_der = st.columns([1, 1, 1, 1, 1])
    with col1:
        st.metric("Total de Registros", len(df_tabla))
    with col2:
        st.metric("Total de Matriculados", f"{df_tabla['MATRICULADOS'].sum():,.0f}")
    with col3:
        st.metric("Universidades", df_filtrado["NOMBRE INSTITUCION"].nunique())

    # Configurar la tabla con formato
    st.dataframe(
        df_tabla,
        width="stretch",
        hide_index=True,
        height=600,
        column_config={
            "NOMBRE CARRERA": st.column_config.TextColumn(
                "Nombre Carrera", width="large"
            ),
            "MATRICULADOS": st.column_config.NumberColumn("Matriculados", format="%d"),
        },
    )

except FileNotFoundError:
    st.error(
        "❌ Error: No se encontró el archivo 'db/data.xlsx'. Por favor, asegúrese de que el archivo existe."
    )
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {str(e)}")
