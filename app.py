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

# --- 2. CSS: ARQUITECTURA DE CAPAS (Lienzo Único) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* CAPA 0: FONDO TOTAL */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* CAPA 1: EL LIENZO BLANCO (Contenedor Maestro) */
    /* Este contenedor obliga a que todo lo de adentro tenga fondo blanco sólido */
    .master-canvas {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        margin: 40px auto;
        max-width: 1100px;
        min-height: 85vh;
    }

    /* EL AIRE DEL LOGO */
    .logo-box {
        padding: 2px;
        display: inline-block;
        background-color: white;
        margin-bottom: 20px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        line-height: 1.1;
        margin-top: 10px;
    }

    /* Tabs dentro del lienzo */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 2px solid #f0f2f6; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f8f9fa; border-radius: 4px 4px 0 0; padding: 12px 25px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO DEL LIENZO MAESTRO ---

# Abrimos el contenedor que atrapará TODO el contenido
st.markdown('<div class="master-canvas">', unsafe_allow_html=True)

# Cabecera integrada
col_logo, col_titulo = st.columns([1, 3])

with col_logo:
    st.markdown('<div class="logo-box">', unsafe_allow_html=True)
    if os.path.exists("logo_wurth.jpg"):
        st.image("logo_wurth.jpg", width=220)
    else:
        st.write("### WÜRTH")
    st.markdown('</div>', unsafe_allow_html=True)

with col_titulo:
    st.markdown("<h1 class='main-title'>PENCA DIGITAL<br>WÜRTH 2026</h1>", unsafe_allow_html=True)

st.write("---")

# Pestañas
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    if not df_partidos.empty:
        # Aquí puedes insertar el formulario de pronósticos que teníamos
        st.info("Fixture listo para pronosticar.")
    else:
        st.warning("Carga los partidos en la planilla 'partidos' del Excel.")

# Cerramos el contenedor maestro
st.markdown('</div>', unsafe_allow_html=True)
