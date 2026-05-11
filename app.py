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

# --- 2. ESTILOS CSS (Capas y Márgenes) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* CAPA DE FONDO (Secundaria) */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* CUADRO INTERACTIVO DE LA APP (Capa Principal) */
    .penca-canvas {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        margin: 20px auto;
        max-width: 1200px;
    }

    /* CONTENEDOR DEL LOGO (Con el aire de 1px solicitado) */
    .logo-container {
        padding: 2px; /* Margen interno para que no toque bordes */
        display: inline-block;
        background-color: white;
        margin-bottom: 20px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 45px;
        font-family: 'Arial Black', sans-serif;
        margin-top: 5px;
    }

    /* Ajuste de Tabs dentro del cuadro blanco */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f8f9fa; border-radius: 4px 4px 0 0; padding: 10px 25px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO DE LA APLICACIÓN (Capa Flotante) ---

# Abrimos el lienzo blanco principal
st.markdown('<div class="penca-canvas">', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Logo en JPG con su margen protector
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        if os.path.exists("logo_wurth.jpg"):
            st.image("logo_wurth.jpg", width=220)
        else:
            st.write("### WÜRTH")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# Pestañas dentro del cuadro blanco
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    if not df_partidos.empty:
        # Aquí va tu bucle de partidos
        st.write("Partidos cargados correctamente.")
    else:
        st.info("Carga los partidos en el Excel para comenzar.")

# Cerramos el lienzo blanco
st.markdown('</div>', unsafe_allow_html=True)
