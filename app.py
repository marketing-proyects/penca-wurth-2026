import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Penca Würth 2026", 
    page_icon="favicon.png", 
    layout="wide"
)

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LÓGICA DE FONDO (Imagen Única) ---
fondos = [
    "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&q=80&w=2070",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&q=80&w=2070",
    "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&q=80&w=2093"
]
fondo_seleccionado = random.choice(fondos)

# --- ESTILOS CSS AVANZADOS ---
st.markdown(f"""
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    
    /* Fondo de pantalla completa */
    .stApp {{
        background: url("{fondo_seleccionado}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* CUADRO PRINCIPAL (Efecto para resaltar la App) */
    .penca-container {{
        background-color: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 20px auto;
        max-width: 1200px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* CONTENEDOR DEL LOGO (Ajuste de aire/espaciado) */
    .logo-frame {{
        background-color: white;
        padding: 12px; /* Espacio interno */
        margin: 1px;  /* El 'aire' de 1px solicitado */
        border-radius: 10px;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}

    h1, h2, h3 {{ color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }}
    
    .main-title {{
        color: #ED1C24;
        font-size: 45px;
        font-family: 'Arial Black', sans-serif;
        font-weight: bold;
        margin-bottom: 0px;
    }}
    
    /* Estilo de los botones */
    .stButton>button {{ 
        background-color: #ED1C24; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold; height: 3.5em;
    }}
    .stButton>button:hover {{ background-color: #000000; color: white; }}
    </style>
    """, unsafe_allow_html=True)

# --- INICIO DEL CUADRO DE LA APLICACIÓN ---
st.markdown('<div class="penca-container">', unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown('<div class="logo-frame">', unsafe_allow_html=True)
        # Cargamos el archivo .jpg que subiste
        if os.path.exists("logo_wurth.jpg"):
            st.image("logo_wurth.jpg", width=220)
        else:
            st.write("### WÜRTH")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)
        st.write("---")

# --- FUNCIONES DE DATOS ---
def obtener_datos(pestana):
    try:
        return conn.read(worksheet=pestana, ttl=0)
    except:
        return pd.DataFrame()

# --- CONTENIDO DE TABS ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    if not df_partidos.empty:
        with st.form("penca_form"):
            usuario = st.text_input("Tu Nombre:")
            # Aquí va el bucle de partidos... (manteniendo la lógica previa)
            st.form_submit_button("Guardar")
    else:
        st.info("Carga partidos en el Excel para comenzar.")

with tab2:
    st.header("DESAFÍO VENTAS")
    # Lógica de ventas...

with tab3:
    st.header("POSICIONES")
    # Lógica de ranking...

st.markdown('</div>', unsafe_allow_html=True) # CIERRE DEL CUADRO PRINCIPAL
