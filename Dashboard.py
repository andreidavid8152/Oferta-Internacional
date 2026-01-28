import streamlit as st
import pandas as pd
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Oferta Internacional", page_icon="🌍", layout="wide"
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
    st.title("🌍 Dashboard Oferta Internacional")

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

    # Filtro 2: Financiamiento (cascada)
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

    # Filtro 3: Tipo (cascada)
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

    # Calcular métricas
    total_matriculados = int(df_filtrado["MATRICULADOS"].sum())
    total_universidades = df_filtrado["NOMBRE INSTITUCION"].nunique()

    # Tarjetas minimalistas con HTML/CSS personalizado
    st.subheader("📊 Resumen")

    # Crear contenedor con tarjetas centradas
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

    # Tabla dinámica
    st.subheader("📋 Detalle de Carreras")

    # Preparar datos para la tabla
    df_tabla = df_filtrado[["NOMBRE CARRERA", "MATRICULADOS"]].copy()
    df_tabla = df_tabla.rename(columns={"NOMBRE CARRERA": "CARRERA"})

    # Agrupar por carrera y sumar matriculados
    df_tabla = df_tabla.groupby("CARRERA", as_index=False)["MATRICULADOS"].sum()

    # Ordenar alfabéticamente por carrera
    df_tabla = df_tabla.sort_values("CARRERA", ascending=True)

    # Resetear índice para que comience en 1
    df_tabla.reset_index(drop=True, inplace=True)
    df_tabla.index = df_tabla.index + 1

    # Calcular altura dinámica de la tabla (aproximadamente 35px por fila + header)
    num_filas = len(df_tabla)
    altura_fila = 35
    altura_header = 40
    altura_minima = 100
    altura_maxima = 500

    altura_dinamica = max(
        altura_minima, min(num_filas * altura_fila + altura_header, altura_maxima)
    )

    # Mostrar tabla con formato
    st.dataframe(
        df_tabla,
        use_container_width=True,
        height=int(altura_dinamica),
        column_config={
            "CARRERA": st.column_config.TextColumn("CARRERA", width="large"),
            "MATRICULADOS": st.column_config.NumberColumn("MATRICULADOS", format="%d"),
        },
    )

    # Información adicional
    st.info(f"📊 Total de registros mostrados: **{len(df_tabla)}**")

else:
    st.error(
        "⚠️ No se pudo cargar el archivo base.xlsx. Verifica que el archivo existe en la carpeta 'db'."
    )
