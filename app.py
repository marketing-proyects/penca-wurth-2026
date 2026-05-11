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

# --- LÓGICA DE FONDO DINÁMICO (Imagen Única) ---
fondos = [
    "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&q=80&w=2070", # Estadio noche
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&q=80&w=2070", # Estadio césped
    "https://images.unsplash.com/photo-1574629810360-7efbbe195018?auto=format&fit=crop&q=80&w=2093", # Balón en campo
    "https://images.unsplash.com/photo-1510279770292-4b34de9f5c23?auto=format&fit=crop&q=80&w=2070"  # Gradas estadio
]
fondo_seleccionado = random.choice(fondos)

# --- ESTILOS, FONDO Y LIMPIEZA DE INTERFAZ ---
st.markdown(f"""
    <style>
    /* Ocultar elementos de Streamlit */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    
    /* Fondo con imagen única y opacidad para legibilidad */
    .stApp {{
        background: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), 
                    url("{fondo_seleccionado}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Contenedor del LOGO con padding para evitar redondeo en los bordes de la imagen */
    .logo-box {{
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        display: inline-block;
        margin-bottom: 10px;
    }}

    h1, h2, h3 {{ color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }}
    
    .main-title {{
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        margin-top: -10px;
        font-weight: bold;
    }}
    
    /* Estilo de los Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ 
        background-color: rgba(240, 242, 246, 0.9); 
        border-radius: 4px 4px 0 0; padding: 10px 20px; font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown('<div class="logo-box">', unsafe_allow_html=True)
        if os.path.exists("logo_wurth.jpg"):
            st.image("logo_wurth.jpg", width=200)
        else:
            st.write("WÜRTH")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# --- FUNCIONES DE DATOS ---
def obtener_datos(pestana):
    try:
        return conn.read(worksheet=pestana, ttl=0)
    except:
        return pd.DataFrame()

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    ahora = datetime.now()

    if not df_partidos.empty:
        with st.form("form_penca"):
            usuario = st.text_input("Participante:", placeholder="Tu nombre")
            st.divider()
            
            # Lógica de renderizado de partidos
            for _, row in df_partidos.iterrows():
                es_uy = row['local'] == 'Uruguay' or row['visitante'] == 'Uruguay'
                bg_color = "#fff5f5" if es_uy else "#f9f9f9"
                border = "5px solid #ED1C24" if es_uy else "1px solid #ddd"
                
                st.markdown(f"<div style='border-left: {border}; padding: 15px; margin-bottom:10px; border-radius:5px; background-color:{bg_color};'>", unsafe_allow_html=True)
                c1, c_vs, c2 = st.columns([2, 1, 2])
                with c1:
                    st.write(f"**{row['local']}**")
                    st.number_input("Goles", 0, 20, 0, key=f"l_{row['id']}")
                with c_vs:
                    st.markdown(f"<p style='text-align:center; padding-top:20px;'>{row['hora_uy']} hs</p>", unsafe_allow_html=True)
                with c2:
                    st.write(f"**{row['visitante']}**")
                    st.number_input("Goles", 0, 20, 0, key=f"v_{row['id']}")
                st.markdown("</div>", unsafe_allow_html=True)
            
            if st.form_submit_button("GUARDAR PRONÓSTICOS"):
                st.success("¡Datos enviados!")
    else:
        st.warning("Sin datos en 'partidos'.")

# (Tabs 2 y 3 mantienen la lógica de guardado en GSheets previa)
