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
html, body, [data-testid=\"stAppViewContainer\"] {{
font-family: "Leelawadee UI", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
background: radial-gradient(circle at top left, #1f4fa3 0, #0b172c 40%, #02040a 100%);
}}

/* Contenedor principal */
div.block-container {{
background-color: rgba(255, 255, 255, 0.98);
border-radius: 24px;
padding: 2.5rem 3rem;
margin-top: 2rem;
box-shadow: 0 20px 50px rgba(0,0,0,0.35);
}}

/* Sidebar */
section[data-testid=\"stSidebar\"] {{
background-color: rgba(3, 17, 40, 0.97);
color: #f5f7fb;
}}
section[data-testid=\"stSidebar\"] h2,
section[data-testid=\"stSidebar\"] label,
section[data-testid=\"stSidebar\"] span {{
color: #f5f7fb !important;
}}

h1, h2, h3, h4 {{
color: {FAMAEX_BLUE};
}}

/* Controles */
div[data-baseweb=\"select\"] > div {{
border-radius: 10px !important;
border: 1px solid {FAMAEX_BLUE} !important;
}}

/* ✅ CHIPS AZULES CORREGIDOS */
[data-baseweb="tag"] {{
background-color: #e3f2ff !important;
color: #11325f !important;
border-radius: 999px !important;
border: 1px solid #b3d4ff !important;
font-weight: 500 !important;
}}

button {{
background-color: {FAMAEX_BLUE} !important;
color: white !important;
border-radius: 999px !important;
}}

.kpi-row {{
display: grid;
grid-template-columns: repeat(4, minmax(0, 1fr));
gap: 1.2rem;
margin-top: 1.5rem;
}}
.kpi-card {{
background: linear-gradient(135deg, #1f4fa3, #0090ff);
border-radius: 18px;
padding: 1rem 1.3rem;
color: #ffffff;
}}
