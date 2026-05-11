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

# --- 2. CSS: CAPAS INDEPENDIENTES ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* CAPA 0: FONDO (Detrás de todo) */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* CAPA 1: EL CUADRO BLANCO (Lienzo interactivo) */
    .penca-canvas {
        background-color: white;
        padding: 45px;
        border-radius: 12px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        margin: 50px auto; /* Centrado y con aire arriba/abajo */
        max-width: 1100px;
        min-height: 80vh;
    }

    /* EL AIRE DEL LOGO (Margen de 1px/2px sobre fondo blanco) */
    .logo-wrapper {
        padding: 2px;
        display: inline-block;
        background-color: white;
        margin-bottom: 25px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        margin: 0;
        line-height: 1.2;
    }

    /* Estilo de los Tabs dentro del lienzo blanco */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 2px solid #f0f2f6; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f8f9fa; border-radius: 4px 4px 0 0; padding: 12px 30px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO DEL LIENZO PRINCIPAL ---

# Todo lo que escribamos dentro de este DIV aparecerá sobre el cuadro blanco
st.markdown('<div class="penca-canvas">', unsafe_allow_html=True)

# Layout de Cabecera
col_log, col_tit = st.columns([1, 3])

with col_log:
    st.markdown('<div class="logo-wrapper">', unsafe_allow_html=True)
    if os.path.exists("logo_wurth.jpg"):
        st.image("logo_wurth.jpg", width=220)
    else:
        st.write("### WÜRTH")
    st.markdown('</div>', unsafe_allow_html=True)

with col_tit:
    st.markdown("<h1 class='main-title'>PENCA DIGITAL<br>WÜRTH 2026</h1>", unsafe_allow_html=True)

st.write("---")

# Estructura de Pestañas
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    if not df_partidos.empty:
        st.write("Partidos listos para pronosticar.")
    else:
        st.info("Carga partidos en tu Google Sheet para ver el fixture.")

# Cerramos el lienzo blanco (Capas separadas correctamente)
st.markdown('</div>', unsafe_allow_html=True)
