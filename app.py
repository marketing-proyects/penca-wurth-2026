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

# --- 2. CSS: ESTILO INTEGRADO (Inspirado en Puntos Würth) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* CAPA DE FONDO: Imagen con opacidad fundida */
    .stApp {
        background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* CONTENEDOR MAESTRO (Sin bordes pesados, integrado al fondo) */
    .master-container {
        max-width: 1000px;
        margin: 0 auto;
        padding-top: 50px;
        text-align: center;
    }

    /* MARCO DEL LOGO (Resaltado sobre el fondo fundido) */
    .logo-frame {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 48px;
        font-family: 'Arial Black', sans-serif;
        margin-bottom: 40px;
        letter-spacing: -1px;
    }
    
    /* Estilo de los Tabs (Limpio y minimalista) */
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center; 
        background-color: transparent;
        border-bottom: 2px solid #ED1C24;
    }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255,255,255,0.5); 
        border-radius: 8px 8px 0 0; 
        padding: 10px 30px; 
        font-weight: bold;
        color: #333;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ED1C24 !important; 
        color: white !important; 
    }

    /* Inputs y Formularios integrados */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: rgba(255,255,255,0.9) !important;
        border: 1px solid #ddd !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RENDERIZADO ---

# Abrimos el contenedor principal
st.markdown('<div class="master-container">', unsafe_allow_html=True)

# Logo Centrado (como en Puntos Würth)
st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=250)
else:
    st.write("### WÜRTH")
st.markdown('</div>', unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# Pestañas de Navegación
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

def obtener_datos(pestana):
    try: return conn.read(worksheet=pestana, ttl=0)
    except: return pd.DataFrame()

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    df_p = obtener_datos("partidos")
    if not df_p.empty:
        # Aquí insertamos la carga de partidos en un contenedor con opacidad
        with st.container():
            st.info("El fixture se encuentra disponible para completar.")
    else:
        st.warning("Sin partidos cargados en la base de datos.")

# Cerramos el contenedor maestro
st.markdown('</div>', unsafe_allow_html=True)
