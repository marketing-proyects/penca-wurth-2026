import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Penca Würth 2026", 
    page_icon="favicon.png", 
    layout="wide"
)

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILOS CSS REFINADOS ---
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* Fondo con imagen única y opacidad controlada */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.8), rgba(255, 255, 255, 0.8)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Cuadro de contenido profesional */
    .penca-box {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 10px;
    }

    /* Marco del Logo con "Aire" de 1px */
    .logo-frame {
        background-color: white;
        padding: 2px; /* Espacio para que no toque bordes */
        border: 1px solid transparent; /* El aire de 1px */
        display: inline-block;
        line-height: 0;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 40px;
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        margin: 0;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: white; border-radius: 4px 4px 0 0; padding: 10px 20px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        if os.path.exists("logo_wurth.jpg"):
            st.image("logo_wurth.jpg", width=200)
        else:
            st.write("WÜRTH")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# --- CUADRO PRINCIPAL DE LA APP ---
st.markdown('<div class="penca-box">', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    if not df_partidos.empty:
        # Aquí iría el resto de tu lógica de partidos...
        pass
    else:
        st.info("Carga los partidos en el Excel para comenzar.")

st.markdown('</div>', unsafe_allow_html=True)
