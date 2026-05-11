import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Penca Würth 2026", 
    page_icon="favicon.png", 
    layout="wide"
)

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. CSS DE ALTA PRIORIDAD (FORZADO DE CAPAS) ---
st.markdown("""
    <style>
    /* 1. OCULTAR TODO LO QUE NO SEA NUESTRO LIENZO */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* 2. FONDO TOTAL (CAPA INFERIOR) */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 3. FORZAR TRANSPARENCIA EN CONTENEDORES INTERMEDIOS DE STREAMLIT */
    [data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
    }

    /* 4. EL LIENZO MAESTRO BLANCO (CAPA SUPERIOR) */
    .master-canvas {
        background-color: white !important;
        padding: 50px;
        border-radius: 10px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        margin: 20px auto;
        max-width: 1100px;
        min-height: 85vh;
        z-index: 99;
    }

    /* EL AIRE DEL LOGO JPG */
    .logo-frame {
        padding: 2px;
        background-color: white;
        display: inline-block;
        margin-bottom: 20px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        line-height: 1.1;
        margin: 0;
    }
    
    /* Tabs dentro del lienzo blanco */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 2px solid #f0f2f6; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f8f9fa; border-radius: 4px 4px 0 0; padding: 12px 25px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO DEL LIENZO MAESTRO ---

# Este div DEBE envolver absolutamente todo lo que sigue
st.markdown('<div class="master-canvas">', unsafe_allow_html=True)

# Cabecera
col_log, col_tit = st.columns([1, 3])

with col_log:
    st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
    if os.path.exists("logo_wurth.jpg"):
        st.image("logo_wurth.jpg", width=220)
    else:
        st.write("### WÜRTH")
    st.markdown('</div>', unsafe_allow_html=True)

with col_tit:
    st.markdown("<h1 class='main-title'>PENCA DIGITAL<br>WÜRTH 2026</h1>", unsafe_allow_html=True)

st.write("---")

# Contenido Interactivo
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_p = obtener_datos("partidos")
    if not df_p.empty:
        st.info("Fixture cargado desde GSheets.")
    else:
        st.warning("No hay partidos en la planilla 'partidos'.")

# IMPORTANTE: Cerramos el lienzo maestro al FINAL de todo el código
st.markdown('</div>', unsafe_allow_html=True)
