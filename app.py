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

# --- 2. CSS: DEGRADADO DIRECCIONAL Y BLINDAJE LOGO CEREBRO ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* FONDO: Degradado de Izquierda (98% blanco) a Derecha (80% blanco) */
    .stApp {
        background: linear-gradient(
            to right, 
            rgba(255, 255, 255, 0.98) 0%, 
            rgba(255, 255, 255, 0.92) 50%, 
            rgba(255, 255, 255, 0.80) 100%
        ), 
        url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* TÉCNICA CEREBRO: Eliminar redondeo de imagen de raíz (Target directo al tag img) */
    [data-testid="stImage"] img {
        border-radius: 0px !important;
    }

    /* CONTENEDOR DEL LOGO: Sin redondeos y con aire limpio */
    .logo-box-cerebro {
        background-color: white !important;
        padding: 5px !important;
        border-radius: 0px !important;
        display: inline-block;
        line-height: 0;
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
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
        background-color: rgba(255, 255, 255, 0.5); 
        border-radius: 4px 4px 0 0; 
        padding: 12px 25px; 
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ED1C24 !important; 
        color: white !important; 
    }
    
    /* Estilo para las filas de partidos */
    .partido-row {
        background-color: rgba(255, 255, 255, 0.6);
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
        border-left: 5px solid #ED1C24;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS ---
def obtener_datos(pestana):
    try:
        return conn.read(worksheet=pestana, ttl=0)
    except Exception as e:
        st.error(f"Error al conectar con la pestaña {pestana}")
        return pd.DataFrame()

# --- 4. RENDERIZADO DE CABECERA ---

# Logo con blindaje de esquinas (Técnica CEREBRO)
st.markdown('<div class="logo-box-cerebro">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=220)
else:
    st.write("### WÜRTH")
st.markdown('</div>', unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# --- 5. ESTRUCTURA DE NAVEGACIÓN ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CARGA AUTOMÁTICA DESDE GOOGLE SHEETS
    df_partidos = obtener_datos("partidos")

    if not df_partidos.empty:
        with st.form("form_penca"):
            usuario = st.text_input("Tu Nombre Completo:", placeholder="Ej: Juan Pérez")
            st.divider()
            
            respuestas_usuario = []
            
            # Bucle para generar el fixture automáticamente
            for index, row in df_partidos.iterrows():
                with st.container():
                    col_info, col_goles = st.columns([3, 2])
                    
                    with col_info:
                        st.markdown(f"**{row['local']} vs {row['visitante']}**")
                        st.caption(f"📅 {row['fecha']} | ⏰ {row['hora_uy']} hs")
                    
                    with col_goles:
                        c1, c2 = st.columns(2)
                        g_l = c1.number_input("L", 0, 20, 0, key=f"l_{row['id']}")
                        g_v = c2.number_input("V", 0, 20, 0, key=f"v_{row['id']}")
                    
                    st.markdown("---")
                    
                    respuestas_usuario.append({
                        "usuario": usuario,
                        "partido_id": row['id'],
                        "goles_local": g_l,
                        "goles_visitante": g_v,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # Botón de Guardado
            if st.form_submit_button("GUARDAR MIS PRONÓSTICOS"):
                if usuario:
                    # Lógica para persistir datos en la pestaña "apuestas"
                    df_nuevas_apuestas = pd.DataFrame(respuestas_usuario)
                    try:
                        df_existente = obtener_datos("apuestas")
                        df_final = pd.concat([df_existente, df_nuevas_apuestas], ignore_index=True)
                        conn.update(worksheet="apuestas", data=df_final)
                        st.success(f"¡Excelente {usuario}! Tus resultados han sido guardados.")
                    except:
                        st.error("Error al guardar. Verifica la pestaña 'apuestas'.")
                else:
                    st.warning("Por favor, ingresa tu nombre para registrar la apuesta.")
    else:
        st.warning("⚠️ No se encontraron partidos cargados en la pestaña 'partidos'.")

with tab2:
    st.header("🎯 Bono Especial: Día de Ventas")
    st.info("Próximamente disponible.")

with tab3:
    st.header("🥇 Ranking de Posiciones")
    st.info("El ranking se actualizará automáticamente con los resultados reales.")
