import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# -----------------------------
# Configuración de página
# -----------------------------
st.set_page_config(
    page_title="Dashboard Colaboradores | FAMAEX",
    layout="wide",
)

# =============================
# ESTILO CORPORATIVO FAMAEX
# =============================
FAMAEX_BLUE = "#1f4fa3"

st.markdown(
    f"""
<style>
/* Fuente corporativa (Leelawadee UI si está instalada, si no, similares) */
html, body, [data-testid="stAppViewContainer"] {{
    font-family: "Leelawadee UI", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: radial-gradient(circle at top left, #1f4fa3 0, #0b172c 40%, #02040a 100%);
}}

/* Contenedor principal (tarjeta blanca central) */
div.block-container {{
    background-color: rgba(255, 255, 255, 0.98);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-top: 2rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.35);
}}

/* Sidebar con fondo oscuro corporativo */
section[data-testid="stSidebar"] {{
    background-color: rgba(3, 17, 40, 0.97);
    color: #f5f7fb;
}}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {{
    color: #f5f7fb !important;
}}

/* Títulos */
h1, h2, h3, h4 {{
    color: {FAMAEX_BLUE};
}}

/* Controles de selección (multiselect, selectbox) */
div[data-baseweb="select"] > div {{
    border-radius: 10px !important;
    border: 1px solid {FAMAEX_BLUE} !important;
    box-shadow: 0 0 0 1px rgba(31,79,163,0.1);
}}

/* Chips de selección (lo que ahora ves rojo) */
div[data-baseweb="tag"] {{
    background-color: #e3f2ff !important;
    color: #11325f !important;
    border-radius: 999px !important;
    border: 1px solid #b3d4ff !important;
    font-weight: 500 !important;
}}

/* Botones generales */
button {{
    background-color: {FAMAEX_BLUE} !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    border: none !important;
}}

/* Barra superior corporativa */
.top-bar {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 0.8rem 0 1.6rem 0;
    border-bottom: 1px solid rgba(15, 35, 70, 0.12);
}}
.top-bar-logo img {{
    max-height: 52px;
}}
.top-bar-title-main {{
    font-size: 1.8rem;
    font-weight: 700;
    color: {FAMAEX_BLUE};
}}
.top-bar-title-sub {{
    font-size: 0.95rem;
    color: #55627a;
}}

/* Footer corporativo */
.famaex-footer {{
    margin-top: 2.2rem;
    padding-top: 0.8rem;
    border-top: 1px solid rgba(15, 35, 70, 0.12);
    text-align: center;
    font-size: 0.8rem;
    color: #6b7484;
}}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Barra superior con logo
# -----------------------------
logo_path = Path("logo_famaex.png")

col_logo, col_text = st.columns([1, 4])

with col_logo:
    if logo_path.exists():
        st.markdown("<div class='top-bar-logo'>", unsafe_allow_html=True)
        st.image(str(logo_path))
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("### FAMAEX")

with col_text:
    st.markdown(
        """
        <div class="top-bar">
            <div>
                <div class="top-bar-title-main">Dashboard de colaboradores</div>
                <div class="top-bar-title-sub">
                    Análisis de rendimiento por colaborador, provincia y gremio
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
Sube un Excel con los servicios de tus colaboradores y analizaremos:

- Quién es mejor según **Precio, Velocidad, Calidad, Documentación y Nota final**  
- Comparativas por **Provincia** y **Gremio**  
"""
)

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

    # Quitamos filas sin colaborador
    df_clean = df_clean.dropna(subset=["Colaborador"]).reset_index(drop=True)

    return df_clean


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
# KPIs generales (con iconos, estilo normal)
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Colaboradores únicos", df_filtrado["Colaborador"].nunique())
with col2:
    st.metric("📍 Provincias", df_filtrado["Provincia"].nunique())
with col3:
    st.metric("🛠️ Gremios", df_filtrado["Gremio"].nunique())
with col4:
    st.metric("⭐ Nota final media", f"{df_filtrado['Nota final'].mean():.2f}")

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

top_n = st.slider(
    "Ver top N colaboradores", min_value=5, max_value=50, value=10, step=5
)

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
    st.write(
        "Provincias donde trabaja:",
        ", ".join(sorted(df_colab["Provincia"].unique())),
    )
    st.write("Gremios:", ", ".join(sorted(df_colab["Gremio"].unique())))
    st.write("Medias:")
    st.write(
        df_colab[
            ["Precio", "Velocidad", "Calidad", "Documentación", "Nota final"]
        ]
        .mean()
        .round(2)
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

st.caption(
    "Consejo: puedes cambiar filtros en la barra lateral para focalizar en una zona o gremio concreto."
)

# -----------------------------
# Footer corporativo
# -----------------------------
st.markdown(
    """
    <div class="famaex-footer">
        FAMAEX © 2025 · Dashboard interno de colaboradores
    </div>
    """,
    unsafe_allow_html=True,
)
