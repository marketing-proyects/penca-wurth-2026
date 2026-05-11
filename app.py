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

# --- 2. CSS: FONDO CASI BLANCO Y LOGO RESPIRANDO ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* CAPA DE FONDO: 95% de opacidad blanca para que el estadio apenas se intuya */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.95)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* CONTENEDOR DE CONTENIDO CENTRADO */
    [data-testid="stVerticalBlock"] {
        max-width: 1000px;
        margin: 0 auto;
    }

    /* EL AIRE DEL LOGO: Padding de 4px para evitar redondeo del JPG */
    .logo-frame {
        background-color: white;
        padding: 4px;
        display: outline-block;
        margin-bottom: 10px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        margin-top: 5px;
        margin-bottom: 25px;
        letter-spacing: -1px;
    }
    
    /* Pestañas estilo Puntos Würth */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 10px; 
        background-color: transparent;
        border-bottom: 2px solid #ED1C24;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255, 255, 255, 0.8); 
        border-radius: 8px 8px 0 0; 
        padding: 10px 25px; 
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ED1C24 !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO ---

# Logo JPG con su marco de aire de 1px/2px
st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
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
        st.info("Fixture listo para pronosticar.")
    else:
        st.warning("Carga los partidos en la planilla 'partidos'.")
