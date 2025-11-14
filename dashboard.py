import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Servicios de Colaboradores",
    page_icon="📊",
    layout="wide"
)

# Título y descripción
st.title("🏆 Panel de Rendimiento de Colaboradores")
st.markdown("""
Analiza y compara el rendimiento de tus colaboradores en velocidad de servicio y precio.  
**Carga tu archivo Excel exportado** para comenzar el análisis.
""")


# ----------------------------
# FUNCIÓN PARA CARGAR LOS DATOS
# ----------------------------
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is None:
        return None

    df = pd.read_excel(uploaded_file)

    # Normalizamos nombres para buscarlos aunque el Excel tenga mayúsculas
    colmap = {c.strip().lower(): c for c in df.columns}

    # Columnas reales del Excel que necesitamos:
    req = {
        "proveedor": "colaborador",
        "tiempo total prov": "velocidad",
        "precio_proveedor": "precio",
        "provincia": "provincia",
        "gremio": "gremio"
    }

    # Comprobamos que existan TODAS
    missing = [src for src in req if src not in colmap]
    if missing:
        st.error(
            "Faltan columnas obligatorias en el Excel:\n\n" +
            ", ".join(missing) +
            "\n\nColumnas encontradas:\n" +
            ", ".join(df.columns.astype(str))
        )
        return None

    # Creamos dataframe estándar
    df_std = pd.DataFrame()

    df_std["colaborador"] = df[colmap["proveedor"]].astype(str).str.strip()
    df_std["velocidad"] = pd.to_numeric(df[colmap["tiempo total prov"]], errors="coerce")
    df_std["precio"] = pd.to_numeric(df[colmap["precio_proveedor"]], errors="coerce")
    df_std["provincia"] = df[colmap["provincia"]].astype(str).str.strip()
    df_std["gremio"] = df[colmap["gremio"]].astype(str).str.strip()

    # EXCLUSIÓN de velocidad == 0
    df_std = df_std[df_std["velocidad"] > 0]

    # Eliminamos filas vacías
    df_std = df_std.dropna(subset=["velocidad", "precio"])

    return df_std


# ----------------------------
# CARGA DEL ARCHIVO
# ----------------------------
uploaded_file = st.file_uploader("Cargar archivo Excel", type=["xlsx", "xls"])

if uploaded_file:
    df = load_data(uploaded_file)

    if df is None:
        st.stop()

    # ----------------------------
    # FILTROS LATERALES
    # ----------------------------
    st.sidebar.header("Filtros")

    provincias = sorted(df["provincia"].unique().tolist())
    provincia_sel = st.sidebar.selectbox("Provincia", ["Todas"] + provincias)

    gremios = sorted(df["gremio"].unique().tolist())
    gremio_sel = st.sidebar.selectbox("Gremio", ["Todos"] + gremios)

    colaboradores = df["colaborador"].unique().tolist()
    colaboradores_sel = st.sidebar.multiselect("Colaboradores", colaboradores, colaboradores)

    # Rangos
    min_price, max_price = st.sidebar.slider(
        "Rango de Precio (€)",
        float(df["precio"].min()),
        float(df["precio"].max()),
        (float(df["precio"].min()), float(df["precio"].max()))
    )

    min_speed, max_speed = st.sidebar.slider(
        "Rango de Velocidad (seg)",
        float(df["velocidad"].min()),
        float(df["velocidad"].max()),
        (float(df["velocidad"].min()), float(df["velocidad"].max()))
    )

    # Aplicar filtros
    df_filtered = df.copy()
    if provincia_sel != "Todas":
        df_filtered = df_filtered[df_filtered["provincia"] == provincia_sel]
    if gremio_sel != "Todos":
        df_filtered = df_filtered[df_filtered["gremio"] == gremio_sel]

    df_filtered = df_filtered[
        (df_filtered["colaborador"].isin(colaboradores_sel)) &
        (df_filtered["precio"].between(min_price, max_price)) &
        (df_filtered["velocidad"].between(min_speed, max_speed))
    ]

    if df_filtered.empty:
        st.warning("No hay datos con los filtros seleccionados.")
        st.stop()

    # ----------------------------
    # MÉTRICAS PRINCIPALES
    # ----------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Colaboradores filtrados", df_filtered["colaborador"].nunique())

    with col2:
        velo_min = df_filtered["velocidad"].min()
        colaborador_speed = df_filtered.loc[df_filtered["velocidad"].idxmin(), "colaborador"]
        st.metric("Mejor velocidad", f"{colaborador_speed} ({velo_min:.2f} seg)")

    with col3:
        price_min = df_filtered["precio"].min()
        colaborador_price = df_filtered.loc[df_filtered["precio"].idxmin(), "colaborador"]
        st.metric("Mejor precio", f"{colaborador_price} (€{price_min:.2f})")

    # ----------------------------
    # MEJORES POR PROVINCIA Y GREMIO
    # ----------------------------
    st.subheader("🏅 Mejores por provincia y gremio")

    # Mejor velocidad
    best_speed = df_filtered.loc[
        df_filtered.groupby(["provincia", "gremio"])["velocidad"].idxmin(),
        ["provincia", "gremio", "colaborador", "velocidad"]
    ].rename(columns={
        "colaborador": "mejor_en_velocidad",
        "velocidad": "velocidad_min"
    })

    # Mejor precio
    best_price = df_filtered.loc[
        df_filtered.groupby(["provincia", "gremio"])["precio"].idxmin(),
        ["provincia", "gremio", "colaborador", "precio"]
    ].rename(columns={
        "colaborador": "mejor_en_precio",
        "precio": "precio_min"
    })

    resumen = best_speed.merge(best_price, on=["provincia", "gremio"], how="outer")

    st.dataframe(resumen, use_container_width=True)

    # ----------------------------
    # GRÁFICOS
    # ----------------------------
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("Precio vs Velocidad")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df_filtered, x="precio", y="velocidad", hue="colaborador", ax=ax)
        ax.set_xlabel("Precio (€)")
        ax.set_ylabel("Velocidad (seg)")
        ax.grid(alpha=0.3)
        st.pyplot(fig)

    with colg2:
        st.subheader("Top rendimiento")
        tmp = df_filtered.copy()
        tmp["puntuacion"] = tmp["velocidad"] * 0.7 + tmp["precio"] * 0.3
        tmp = tmp.sort_values("puntuacion").head(10)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(tmp["colaborador"], tmp["puntuacion"])
        ax.invert_yaxis()
        ax.set_xlabel("Puntuación (menor = mejor)")
        st.pyplot(fig)

    # ----------------------------
    # DESCARGA DE RESULTADOS
    # ----------------------------
    st.subheader("💾 Descargar datos filtrados")

    buffer = BytesIO()
    df_filtered.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "Descargar Excel filtrado",
        buffer,
        "resultados.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("👆 Cargue un archivo Excel para comenzar.")