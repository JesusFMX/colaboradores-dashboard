import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Funciones auxiliares
# -----------------------------
def detectar_fila_encabezado(df: pd.DataFrame, palabra_clave="Proveedor"):
    """
    Busca la fila que contiene 'Proveedor' y la usa como fila de encabezados.
    Devuelve el dataframe limpio.
    """
    header_row_idx = None
    for i in range(len(df)):
        fila = df.iloc[i].astype(str)
        if fila.str.contains(palabra_clave, case=False, na=False).any():
            header_row_idx = i
            break

    if header_row_idx is None:
        # Si no encuentra nada, asumimos que la primera fila ya es encabezado
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)
    else:
        df.columns = df.iloc[header_row_idx]
        df = df.iloc[header_row_idx + 1 :].reset_index(drop=True)
    return df


def normalizar_nombre(col):
    """Pasa a minúsculas, quita acentos y espacios para facilitar el mapeo."""
    import unicodedata
    s = str(col).strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )
    s = s.replace(".", "").replace("  ", " ")
    return s


def preparar_dataframe(df_raw: pd.DataFrame):
    # 1. Detectar encabezado real
    df = detectar_fila_encabezado(df_raw)

    # 2. Crear un diccionario de columnas normalizadas
    colmap_norm = {normalizar_nombre(c): c for c in df.columns}

    def get_col(*posibles):
        for p in posibles:
            if p in colmap_norm:
                return colmap_norm[p]
        return None

    # 3. Buscar las columnas que necesitamos
    col_proveedor = get_col("proveedor")
    col_provincia = get_col("provincia")
    col_gremio = get_col("gremio")
    col_precio = get_col("puntuacion coste", "puntuacion costo")
    col_velocidad = get_col("puntuacion sla", "sla", "velocidad")
    col_calidad = get_col("puntuacion calidad", "calidad")
    col_doc = get_col("puntuacion doc", "puntuacion documentacion")
    col_nota_final = get_col("puntuacion final", "nota final")

    columnas_requeridas = {
        "Colaborador": col_proveedor,
        "Provincia": col_provincia,
        "Gremio": col_gremio,
        "Precio": col_precio,
        "Velocidad": col_velocidad,
        "Calidad": col_calidad,
        "Documentación": col_doc,
        "Nota final": col_nota_final,
    }

    faltantes = [k for k, v in columnas_requeridas.items() if v is None]
    if faltantes:
        raise ValueError(
            f"No se han podido identificar estas columnas en el Excel: {', '.join(faltantes)}. "
            "Revisa los nombres de columnas."
        )

    # 4. Construir un df limpio con nombres estándar
    df_clean = pd.DataFrame()
    for nuevo, original in columnas_requeridas.items():
        df_clean[nuevo] = df[original]

    # Aseguramos que las métricas sean numéricas
    metricas = ["Precio", "Velocidad", "Calidad", "Documentación", "Nota final"]
    for m in metricas:
        df_clean[m] = pd.to_numeric(df_clean[m], errors="coerce")

    # Quitamos filas sin colaborador o sin nota final
    df_clean = df_clean.dropna(subset=["Colaborador"]).reset_index(drop=True)

    return df_clean


# -----------------------------
# Interfaz Streamlit
# -----------------------------
st.set_page_config(
    page_title="Dashboard Colaboradores",
    layout="wide",
)

st.title("📊 Dashboard de colaboradores")
st.markdown(
    """
Sube un Excel con los servicios de tus colaboradores y analizaremos:

- Quién es mejor según **Precio, Velocidad, Calidad, Documentación y Nota final**  
- Comparativas por **Provincia** y **Gremio**  
"""
)

# -----------------------------
# Subida de archivo
# -----------------------------
uploaded_file = st.file_uploader(
    "Sube tu archivo Excel (.xlsx)", type=["xlsx", "xls"]
)

@st.cache_data
def cargar_datos(uploaded_file):
    """Carga el Excel subido o, si no hay, uno de ejemplo por defecto."""
    if uploaded_file is not None:
        df_raw = pd.read_excel(uploaded_file)
        origen = "Excel subido por el usuario"
    else:
        # Excel de ejemplo que has subido al repositorio
        df_raw = pd.read_excel("proveedores_principales_provincias.xlsx")
        origen = "Excel de ejemplo por defecto"

    df = preparar_dataframe(df_raw)
    return df, origen

try:
    df, origen_datos = cargar_datos(uploaded_file)
    st.caption(f"🗂 Origen de datos: {origen_datos}")
except Exception as e:
    st.error(f"Error al leer/procesar el archivo: {e}")
    st.stop()

# -----------------------------
# Filtros en la barra lateral
# -----------------------------
st.sidebar.header("Filtros")

provincias = sorted(df["Provincia"].dropna().unique())
gremios = sorted(df["Gremio"].dropna().unique())

prov_seleccionadas = st.sidebar.multiselect(
    "Provincia(s)", options=provincias, default=provincias
)
gremios_seleccionados = st.sidebar.multiselect(
    "Gremio(s)", options=gremios, default=gremios
)

df_filtrado = df[
    df["Provincia"].isin(prov_seleccionadas)
    & df["Gremio"].isin(gremios_seleccionados)
]

if df_filtrado.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada.")
    st.stop()

# -----------------------------
# KPIs generales
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Colaboradores únicos", df_filtrado["Colaborador"].nunique())
with col2:
    st.metric("Provincias", df_filtrado["Provincia"].nunique())
with col3:
    st.metric("Gremios", df_filtrado["Gremio"].nunique())
with col4:
    st.metric("Nota final media", f"{df_filtrado['Nota final'].mean():.2f}")

st.markdown("---")

# -----------------------------
# Ranking por criterio
# -----------------------------
st.subheader("🏆 Ranking de colaboradores")

criterio = st.selectbox(
    "Selecciona criterio para ordenar el ranking:",
    ["Nota final", "Precio", "Velocidad", "Calidad", "Documentación"],
    index=0,
)

top_n = st.slider("Ver top N colaboradores", min_value=5, max_value=50, value=10, step=5)

df_ranking = (
    df_filtrado.groupby("Colaborador", as_index=False)[
        ["Precio", "Velocidad", "Calidad", "Documentación", "Nota final"]
    ]
    .mean()
    .sort_values(by=criterio, ascending=False)
)

st.write(f"Top {top_n} por **{criterio}**")

st.dataframe(df_ranking.head(top_n), use_container_width=True)

fig_bar = px.bar(
    df_ranking.head(top_n),
    x="Colaborador",
    y=criterio,
    title=f"Top {top_n} colaboradores por {criterio}",
)
fig_bar.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# -----------------------------
# Comparación detallada de un colaborador
# -----------------------------
st.subheader("📌 Análisis detallado por colaborador")

colaborador_sel = st.selectbox(
    "Selecciona un colaborador para ver su detalle:",
    options=df_ranking["Colaborador"].tolist(),
)

df_colab = df_filtrado[df_filtrado["Colaborador"] == colaborador_sel]

col_a, col_b = st.columns([1, 2])

with col_a:
    st.markdown(f"### {colaborador_sel}")
    st.write("Provincias donde trabaja:", ", ".join(sorted(df_colab["Provincia"].unique())))
    st.write("Gremios:", ", ".join(sorted(df_colab["Gremio"].unique())))
    st.write("Medias:")
    st.write(
        df_colab[
            ["Precio", "Velocidad", "Calidad", "Documentación", "Nota final"]
        ].mean().round(2)
    )

with col_b:
    # Radar chart / gráfico polar
    medias = (
        df_colab[["Precio", "Velocidad", "Calidad", "Documentación", "Nota final"]]
        .mean()
        .reset_index()
    )
    medias.columns = ["Métrica", "Valor"]
    fig_radar = px.line_polar(
        medias,
        r="Valor",
        theta="Métrica",
        line_close=True,
        title=f"Perfil de {colaborador_sel}",
    )
    fig_radar.update_traces(fill="toself")
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# -----------------------------
# Comparación de provincias o gremios
# -----------------------------
st.subheader("🌍 Comparativas por Provincia / Gremio")

modo_comp = st.radio("Comparar por:", ["Provincia", "Gremio"], horizontal=True)

if modo_comp == "Provincia":
    grupo = "Provincia"
else:
    grupo = "Gremio"

df_comp = (
    df_filtrado.groupby(grupo, as_index=False)[
        ["Precio", "Velocidad", "Calidad", "Documentación", "Nota final"]
    ]
    .mean()
    .sort_values(by="Nota final", ascending=False)
)

st.dataframe(df_comp, use_container_width=True)

fig_comp = px.bar(
    df_comp,
    x=grupo,
    y="Nota final",
    title=f"Nota final media por {grupo}",
)
fig_comp.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_comp, use_container_width=True)

st.caption("Consejo: puedes cambiar filtros en la barra lateral para focalizar en una zona o gremio concreto.")
