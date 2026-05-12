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

# --- 2. CSS: ESTILO CEREBRO / GRADIENTE DIRECCIONAL ---
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
    
    .stTabs [data-baseweb="tab-list"] { gap: 12px; border-bottom: 2px solid #ED1C24; }
    .stTabs [data-baseweb="tab"] { background-color: rgba(255, 255, 255, 0.5); border-radius: 4px 4px 0 0; padding: 12px 25px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS (CON LIMPIEZA) ---
def obtener_datos(pestana):
    try:
        # ttl=0 para forzar lectura fresca
        df = conn.read(worksheet=pestana, ttl=0)
        # Limpieza: eliminar columnas o filas vacías que ensucian la lectura
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        return df
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

    # Verificamos si el DataFrame tiene datos y las columnas necesarias
    columnas_req = ['id', 'local', 'visitante']
    if not df_partidos.empty and all(col in df_partidos.columns for col in columnas_req):
        with st.form("form_penca"):
            usuario = st.text_input("Participante:", placeholder="Ingresa tu nombre")
            st.divider()
            
            respuestas = []
            for _, row in df_partidos.iterrows():
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**{row['local']} vs {row['visitante']}**")
                    # Manejo de columnas opcionales para evitar errores
                    fecha = row.get('fecha', 'TBD')
                    hora = row.get('hora_uy', '--:--')
                    st.caption(f"{fecha} | {hora} hs")
                
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
                        # Intentar leer apuestas previas para no sobreescribir todo el archivo
                        try:
                            df_viejas = obtener_datos("apuestas")
                            df_final = pd.concat([df_viejas, df_nuevas], ignore_index=True)
                        except:
                            df_final = df_nuevas
                            
                        conn.update(worksheet="apuestas", data=df_final)
                        st.success(f"✅ ¡Pronósticos guardados, {usuario}!")
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                else:
                    st.error("⚠️ El nombre es obligatorio.")
    else:
        # Si el DataFrame llega vacío o con columnas mal nombradas
        st.warning("⚠️ No se detectan datos válidos.")
        st.write("Columnas detectadas en el Excel:", list(df_partidos.columns))
        st.info("Asegúrate de que la primera fila del Excel tenga exactamente: id, fecha, hora_uy, local, visitante.")

with tab2:
    st.header("🎯 Desafío Ventas")
    st.info("Módulo en desarrollo.")

with tab3:
    st.header("🥇 Ranking")
    st.info("Se habilitará al comenzar el torneo.")
