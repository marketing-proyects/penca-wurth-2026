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

# --- 2. CSS: ESTILO CEREBRO CON FONDO GRADUAL ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
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

    /* Blindaje Logo Técnica CEREBRO */
    [data-testid="stImage"] img { border-radius: 0px !important; }
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
    .main-title { color: #ED1C24; font-size: 42px; font-family: 'Arial Black', sans-serif; margin: 0 0 30px 0; letter-spacing: -1px; }
    
    /* Tabs Corporativos */
    .stTabs [data-baseweb="tab-list"] { gap: 12px; border-bottom: 2px solid #ED1C24; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255, 255, 255, 0.5); border-radius: 4px 4px 0 0; padding: 12px 25px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #ED1C24 !important; color: white !important; }
    
    /* Estilo de filas de partidos */
    .partido-row {
        background-color: rgba(255, 255, 255, 0.7);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #ED1C24;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS ---
def obtener_datos(pestana):
    try:
        # ttl=0 asegura que traiga los datos reales del Excel al recargar
        return conn.read(worksheet=pestana, ttl=0)
    except Exception:
        return pd.DataFrame()

# --- 4. RENDERIZADO CABECERA ---
st.markdown('<div class="logo-box-cerebro">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=220)
else:
    st.write("### WÜRTH")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# --- 5. TABS ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    df_partidos = obtener_datos("partidos")

    if not df_partidos.empty:
        with st.form("form_penca"):
            usuario = st.text_input("Participante:", placeholder="Tu nombre")
            st.divider()
            
            respuestas = []
            for _, row in df_partidos.iterrows():
                # Renderizado de fila de partido
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**{row['local']} vs {row['visitante']}**")
                    st.caption(f"{row['fecha']} | {row['hora_uy']} hs")
                with col2:
                    c1, c2 = st.columns(2)
                    g_l = c1.number_input("L", 0, 20, 0, key=f"l_{row['id']}")
                    g_v = c2.number_input("V", 0, 20, 0, key=f"v_{row['id']}")
                
                respuestas.append({
                    "usuario": usuario,
                    "partido_id": row['id'],
                    "g_local": g_l,
                    "g_visitante": g_v,
                    "fecha_envio": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.markdown("---")
            
            if st.form_submit_button("GUARDAR PRONÓSTICOS"):
                if usuario:
                    try:
                        df_nuevas = pd.DataFrame(respuestas)
                        df_existentes = obtener_datos("apuestas")
                        df_final = pd.concat([df_existentes, df_nuevas], ignore_index=True)
                        conn.update(worksheet="apuestas", data=df_final)
                        st.success(f"✅ ¡Pronósticos guardados correctamente, {usuario}!")
                    except:
                        st.error("Error al guardar. Asegúrate de tener una pestaña llamada 'apuestas'.")
                else:
                    st.error("⚠️ Por favor ingresa tu nombre.")
    else:
        st.warning("⚠️ No se encontraron partidos. Verifica que la pestaña 'partidos' tenga datos y que las columnas sean: id, fecha, hora_uy, local, visitante.")

with tab2:
    st.header("🎯 Desafío Ventas")
    st.info("Próximamente disponible.")

with tab3:
    st.header("🥇 Ranking")
    st.info("El ranking se actualizará al finalizar los partidos.")
