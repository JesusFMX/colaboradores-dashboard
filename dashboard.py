# =============================
# DASHBOARD FAMAEX - CÓDIGO CORREGIDO
# =============================
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
    """
<style>

html, body, [data-testid="stAppViewContainer"] {
    font-family: "Leelawadee UI", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: radial-gradient(circle at top left, #1f4fa3 0, #0b172c 40%, #02040a 100%);
}

/* Contenedor principal */
div.block-container {
    background-color: rgba(255, 255, 255, 0.98);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-top: 2rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.35);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: rgba(3, 17, 40, 0.97);
    color: #f5f7fb;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #f5f7fb !important;
}

/* Títulos */
h1, h2, h3, h4 {
    color: #1f4fa3;
}

/* Multiselect y selectbox */
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1px solid #1f4fa3 !important;
}

/* CHIPS AZULES */
[data-baseweb="tag"] {
    background-color: #e3f2ff !important;
    color: #11325f !important;
    border-radius: 999px !important;
    border: 1px solid #b3d4ff !important;
    font-weight: 500 !important;
}

/* KPI CARDS */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.2rem;
    margin-top: 1.5rem;
}
.kpi-card {
    background: linear-gradient(135deg, #1f4fa3, #0090ff);
    border-radius: 18px;
    padding: 1rem 1.3rem;
    color: white;
}
.kpi-icon { font-size: 1.4rem; }
.kpi-label { font-size: 0.9rem; }
.kpi-value { font-size: 1.6rem; font-weight: 700; }

.famaex-footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0,0,0,0.15);
    text-align: center;
    font-size: 0.8rem;
    color: #6b7484;
}

</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# DATA + INTERFAZ
# -----------------------------
st.title("Dashboard de colaboradores · FAMAEX")

uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
else:
    df = pd.read_excel("proveedores_principales_provincias.xlsx")

# Simulación de columnas estándar
cols_ok = ["Colaborador","Provincia","Gremio","Precio","Velocidad","Calidad","Documentación","Nota final"]
df.columns = cols_ok

# -----------------------------
# FILTROS
# -----------------------------
st.sidebar.header("Filtros")
prov = st.sidebar.multiselect("Provincia(s)", df["Provincia"].unique(), default=df["Provincia"].unique())
gre = st.sidebar.multiselect("Gremio(s)", df["Gremio"].unique(), default=df["Gremio"].unique())

df_f = df[df["Provincia"].isin(prov) & df["Gremio"].isin(gre)]

# -----------------------------
# KPIs
# -----------------------------
st.markdown(f"""
<div class="kpi-row">
<div class="kpi-card"><div class="kpi-icon">👥</div><div class="kpi-label">Colaboradores</div><div class="kpi-value">{df_f['Colaborador'].nunique()}</div></div>
<div class="kpi-card"><div class="kpi-icon">📍</div><div class="kpi-label">Provincias</div><div class="kpi-value">{df_f['Provincia'].nunique()}</div></div>
<div class="kpi-card"><div class="kpi-icon">🛠️</div><div class="kpi-label">Gremios</div><div class="kpi-value">{df_f['Gremio'].nunique()}</div></div>
<div class="kpi-card"><div class="kpi-icon">⭐</div><div class="kpi-label">Nota media</div><div class="kpi-value">{df_f['Nota final'].mean():.2f}</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.bar_chart(df_f.groupby("Provincia")["Nota final"].mean())

st.markdown('<div class="famaex-footer">FAMAEX © 2025 · Dashboard interno</div>', unsafe_allow_html=True)
