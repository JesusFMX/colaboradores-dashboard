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

CSS = """
<style>
/* Fuente corporativa y fondo */
html, body, [data-testid="stAppViewContainer"] {
    font-family: "Leelawadee UI", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: radial-gradient(circle at top left, #1f4fa3 0, #0b172c 40%, #02040a 100%);
}

/* Contenedor principal (tarjeta blanca central) */
div.block-container {
    background-color: rgba(255, 255, 255, 0.98);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    margin-top: 2rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.35);
}

/* Sidebar con fondo oscuro corporativo */
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

/* Controles de selección (multiselect, selectbox) */
div[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1px solid #1f4fa3 !important;
    box-shadow: 0 0 0 1px rgba(31,79,163,0.1);
}

/* Chips de selección (los tags de los filtros) */
[data-baseweb="tag"] {
    background-color: #e3f2ff !important;   /* azul muy clarito */
    color: #11325f !important;              /* texto azul oscuro */
    border-radius: 999px !important;
    border: 1px solid #b3d4ff !important;
    font-weight: 500 !important;
}

/* Botones generales */
button {
    background-color: #1f4fa3 !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    border: none !important;
}

/* Barra superior corporativa */
.top-bar {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 0.8rem 0 1.6rem 0;
    border-bottom: 1px solid rgba(15, 35, 70, 0.12);
}
.top-bar-logo img {
    max-height: 52px;
}
.top-bar-title-main {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1f4fa3;
}
.top-bar-title-sub {
    font-si
