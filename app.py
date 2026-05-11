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

# --- 2. CSS: FONDO FUNDIDO E INTERFAZ LIMPIA ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* CAPA DE FONDO: Imagen con opacidad blanca fundida (Estilo Puntos) */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* CONTENEDOR DE CONTENIDO (Sin cuadros, centrado) */
    [data-testid="stVerticalBlock"] {
        max-width: 1000px;
        margin: 0 auto;
        background-color: transparent !important;
    }

    /* MARCO DEL LOGO JPG (Con aire de 1px) */
    .logo-frame {
        background-color: white;
        padding: 5px;
        border-radius: 4px;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        margin-bottom: 20px;
        letter-spacing: -1px;
    }
    
    /* Pestañas estilizadas (Estilo Puntos Würth) */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        background-color: transparent;
        border-bottom: 2px solid #ED1C24;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255, 255, 255, 0.6); 
        border-radius: 8px 8px 0 0; 
        padding: 10px 25px; 
        font-weight: bold;
        color: #444;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ED1C24 !important; 
        color: white !important; 
    }

    /* Quitar bordes de contenedores de Streamlit */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO DE ELEMENTOS ---

# Logo con su marco blanco para el JPG
st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=200)
else:
    st.write("### WÜRTH")
st.markdown('</div>', unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# Estructura de Pestañas
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    df_p = obtener_datos("partidos")
    if not df_p.empty:
        # Aquí cargarías el fixture con un diseño de tarjetas ligeras
        st.info("Fixture listo para pronosticar.")
    else:
        st.warning("Sin partidos cargados en la base de datos.")

# El contenido fluirá naturalmente sobre el fondo fundido
