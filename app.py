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

# --- 2. CSS DE ALTA PRIORIDAD (TÉCNICA CEREBRO) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* FONDO: Opacidad 95% (Casi blanco, estética limpia) */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* ELIMINAR REDONDEO DE STREAMLIT (Target directo a la imagen) */
    [data-testid="stImage"] img {
        border-radius: 0px !important;
    }

    /* CONTENEDOR DEL LOGO: Sin redondeos y con aire blanco */
    .logo-box-cerebro {
        background-color: white !important;
        padding: 5px !important;
        border-radius: 0px !important;
        display: inline-block;
        line-height: 0;
        margin-bottom: 20px;
        border: 1px solid #eee; /* Un pequeño borde para definir el bloque */
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        margin-top: 0px;
        margin-bottom: 30px;
        letter-spacing: -1px;
    }
    
    /* Pestañas estilo Puntos/Cerebro */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 12px; 
        border-bottom: 2px solid #ED1C24;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255, 255, 255, 0.8); 
        border-radius: 4px 4px 0 0; 
        padding: 12px 25px; 
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ED1C24 !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO ---

# Logo con blindaje de esquinas
st.markdown('<div class="logo-box-cerebro">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=220)
else:
    st.write("### WÜRTH")
st.markdown('</div>', unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# Pestañas
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    df_p = obtener_datos("partidos")
    if not df_p.empty:
        st.info("Fixture listo para completar.")
    else:
        st.warning("No se encontraron partidos en la base de datos.")
