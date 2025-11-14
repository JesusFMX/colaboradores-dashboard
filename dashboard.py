import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ------------------------------
st.set_page_config(
    page_title="Dashboard de Servicios de Colaboradores",
    page_icon="📊",
    layout="wide"
)

st.title("🏆 Panel de Rendimiento de Colaboradores")
st.markdown("""
Analiza quién es mejor en **velocidad** y **precio** por **colaborador**, 
así como por **provincia** y **gremio**.  
Carga el Excel exportado y empieza a explorar.
""")

# ------------------------------
# FUNCIÓN PARA CARGAR DATOS
# ------------------------------
@st.cache_data
def load_data(file):
    # Leemos todo el Excel
    df = pd.read_excel(file)

    # Normalizamos nombres de columnas (quitamos espacios y pasamos a minúsculas)
    df.columns = [c.strip().lower() for c in df.columns]

    # Mapeo de nombres esperados -> nombres reales
    rename_map = {}

    # Intentamos localizar las columnas según lo que me comentaste
    for c in df.columns:
        if "proveedor" in c:
            rename_map[c] = "colaborador"          # U
        elif "tiempo" in c and "prov" in c:
            rename_map[c] = "velocidad"            # X
        elif "precio_proveedor" in c or ("precio" in c and "prov" in c):
            rename_map[c] = "precio"               # K
        elif "provincia" in c:
            rename_map[c] = "provincia"            # V
        elif "gremio" in c:
            rename_map[c] = "gremio"               # B

    df = df.rename(columns=rename_map)

    # Nos quedamos solo con las columnas que necesitamos
    cols_needed = ["colaborador", "velocidad", "precio", "provincia", "gremio"]
    missing = [c for c in cols_needed if c not in df.columns]

    if missing:
        st.error(
            "Faltan columnas en el Excel después del mapeo automático: "
            + ", ".join(missing)
            + ".\n\n"
            "Revisa que existan columnas como **Proveedor**, **Tiempo total prov**, "
            "**Precio_proveedor**, **Provincia** y **Gremio**."
        )
        return None

    # Convertimos numéricas y limpiamos
    df["velocidad"] = pd.to_numeric(df["velocidad"], errors="coerce")
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

    # Excluimos velocidades 0 y nulos
    df = df.replace({0: np.nan})
    df = df.dropna(subset=["velocidad", "precio", "colaborador"])

    # Limpieza básica de texto
    for col in ["colaborador", "provincia", "gremio"]:
        df[col] = df[col].astype(str).str.strip().str.title()

    return df


# ------------------------------
# CARGA DEL ARCHIVO
# ------------------------------
uploaded_file = st.file_uploader("📥 Cargar archivo Excel", type=["xlsx", "xls"])

if not uploaded_file:
    st.info("👆 Carga un archivo Excel para comenzar el análisis.")
    st.stop()

df = load_data(uploaded_file)
if df is None:
    st.stop()

# ------------------------------
# FILTROS LATERALES
# ------------------------------
st.sidebar.header("🎛️ Filtros")

provincias = sorted(df["provincia"].dropna().unique())
gremios = sorted(df["gremio"].dropna().unique())
colaboradores = sorted(df["colaborador"].dropna().unique())

selected_provincias = st.sidebar.multiselect(
    "Provincia(s)", options=provincias, default=provincias
)
selected_gremios = st.sidebar.multiselect(
    "Gremio(s)", options=gremios, default=gremios
)
selected_colabs = st.sidebar.multiselect(
    "Colaborador(es)", options=colaboradores, default=colaboradores
)

min_precio, max_precio = float(df["precio"].min()), float(df["precio"].max())
rango_precio = st.sidebar.slider(
    "Rango de Precio (€)",
    min_precio, max_precio,
    (min_precio, max_precio)
)

min_vel, max_vel = float(df["velocidad"].min()), float(df["velocidad"].max())
rango_vel = st.sidebar.slider(
    "Rango de Velocidad (seg)",
    min_vel, max_vel,
    (min_vel, max_vel)
)

peso_vel = st.sidebar.slider(
    "Peso de la velocidad en la puntuación", 0.0, 1.0, 0.7, step=0.05
)
peso_prec = 1.0 - peso_vel
st.sidebar.caption(
    f"La puntuación se calcula como: **velocidad×{peso_vel:.2f} + precio×{peso_prec:.2f}**"
)

# ------------------------------
# APLICAMOS FILTROS
# ------------------------------
filtered = df[
    df["provincia"].isin(selected_provincias)
    & df["gremio"].isin(selected_gremios)
    & df["colaborador"].isin(selected_colabs)
    & df["precio"].between(*rango_precio)
    & df["velocidad"].between(*rango_vel)
].copy()

if filtered.empty:
    st.warning("No hay datos que cumplan los filtros seleccionados.")
    st.stop()

# Puntuación combinada
filtered["puntuacion"] = (
    filtered["velocidad"] * peso_vel + filtered["precio"] * peso_prec
)

# ------------------------------
# MÉTRICAS GENERALES
# ------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Colaboradores únicos", filtered["colaborador"].nunique())
with col2:
    st.metric("Provincias", filtered["provincia"].nunique())
with col3:
    st.metric("Gremios", filtered["gremio"].nunique())
with col4:
    st.metric("Registros filtrados", len(filtered))

# Mejor colaborador global (puntuación baja = mejor)
best_global = (
    filtered.groupby("colaborador")["puntuacion"]
    .mean()
    .sort_values()
    .reset_index()
)
best_colab = best_global.iloc[0]

st.success(
    f"🏅 **Mejor colaborador global** (según la puntuación): "
    f"**{best_colab['colaborador']}** "
    f"con puntuación media **{best_colab['puntuacion']:.2f}**"
)

# ------------------------------
# MEJORES POR PROVINCIA Y GREMIO
# ------------------------------
st.markdown("## 🏆 Mejores por provincia y gremio")

# Por provincia
best_by_prov = (
    filtered.groupby(["provincia", "colaborador"])["puntuacion"]
    .mean()
    .reset_index()
)
best_by_prov = (
    best_by_prov.sort_values(["provincia", "puntuacion"])
    .groupby("provincia")
    .head(1)
    .reset_index(drop=True)
)
st.markdown("### 🗺️ Mejor colaborador por provincia")
st.dataframe(best_by_prov)

# Por gremio
best_by_gremio = (
    filtered.groupby(["gremio", "colaborador"])["puntuacion"]
    .mean()
    .reset_index()
)
best_by_gremio = (
    best_by_gremio.sort_values(["gremio", "puntuacion"])
    .groupby("gremio")
    .head(1)
    .reset_index(drop=True)
)
st.markdown("### 🧰 Mejor colaborador por gremio")
st.dataframe(best_by_gremio)

# ------------------------------
# GRÁFICOS
# ------------------------------
st.markdown("## 📈 Análisis gráfico")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Velocidad vs Precio")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=filtered,
        x="precio",
        y="velocidad",
        hue="colaborador",
        alpha=0.8,
        s=80,
        ax=ax,
    )
    ax.set_xlabel("Precio (€)")
    ax.set_ylabel("Velocidad (segundos)")
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with c2:
    st.subheader("Top 10 colaboradores por puntuación")
    ranking = (
        filtered.groupby("colaborador")["puntuacion"]
        .mean()
        .sort_values()
        .head(10)
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(ranking["colaborador"], ranking["puntuacion"])
    ax.invert_yaxis()
    ax.set_xlabel("Puntuación (menos es mejor)")
    st.pyplot(fig)

# ------------------------------
# TABLA DETALLADA Y EXPORTACIÓN
# ------------------------------
st.markdown("## 📋 Datos detallados")
st.dataframe(
    filtered.sort_values(["puntuacion", "velocidad", "precio"])
)

st.download_button(
    "💾 Descargar datos filtrados (Excel)",
    data=filtered.to_excel(index=False),
    file_name="datos_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
