import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILOS Y OCULTAR INTERFAZ DE STREAMLIT ---
st.markdown("""
    <style>
    /* Ocultar Menú, Marca de Agua y Botones superiores */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* Configuración de Fuentes y Colores */
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* Estilo del Título Principal */
    .main-title {
        color: #ED1C24;
        font-size: 42px;
        font-family: 'Arial Black', sans-serif;
        margin-top: -10px;
        font-weight: bold;
    }
    
    /* Estilo de los Botones */
    .stButton>button { 
        background-color: #ED1C24; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold; height: 3.5em;
    }
    .stButton>button:hover { background-color: #000000; color: white; }
    
    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f0f2f6; border-radius: 4px 4px 0 0; padding: 5px 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA (Ajustada a la imagen) ---
with st.container():
    col1, col2 = st.columns([1, 4])
    with col1:
        # Usamos una URL directa del logo que funciona bien en resoluciones estándar
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=220)
    with col2:
        st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)
        st.markdown("<p style='margin-top:-20px; font-weight:bold;'>Market Intelligence Unit • Uruguay</p>", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---
def obtener_datos(pestana):
    try:
        return conn.read(worksheet=pestana, ttl=0)
    except:
        return pd.DataFrame()

def calcular_puntos_futbol(row_apuesta, df_partidos):
    if df_partidos.empty: return 0
    partido = df_partidos[df_partidos['id'] == row_apuesta['partido_id']]
    if partido.empty or pd.isna(partido.iloc[0]['resultado_local']):
        return 0
    real_l, real_v = partido.iloc[0]['resultado_local'], partido.iloc[0]['resultado_visitante']
    ap_l, ap_v = row_apuesta['goles_local'], row_apuesta['goles_visitante']
    if real_l == ap_l and real_v == ap_v: return 3
    if (real_l > real_v and ap_l > ap_v) or (real_l < real_v and ap_l < ap_v) or (real_l == real_v and ap_l == ap_v): return 1
    return 0

# --- ESTRUCTURA DE PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    ahora = datetime.now()

    if not df_partidos.empty:
        with st.form("form_penca"):
            usuario = st.text_input("Ingresa tu Nombre Completo:", placeholder="Ej: Diego_W")
            st.divider()
            
            apuestas_lista = []
            for _, row in df_partidos.iterrows():
                es_uruguay = row['local'] == 'Uruguay' or row['visitante'] == 'Uruguay'
                border = "8px solid #ED1C24" if es_uruguay else "1px solid #ddd"
                
                # Bloqueo horario
                f_dt = datetime.strptime(f"{row['fecha']} {row['hora_uy']}", "%Y-%m-%d %H:%M")
                bloqueado = ahora >= f_dt

                with st.container():
                    st.markdown(f"<div style='border-left: {border}; padding: 15px; margin-bottom:10px; border-radius:5px; background-color:#f9f9f9;'>", unsafe_allow_html=True)
                    c1, c_vs, c2 = st.columns([2, 1, 2])
                    with c1:
                        st.write(f"**{row['local']}**")
                        g_l = st.number_input("Goles", 0, 20, 0, key=f"l_{row['id']}", disabled=bloqueado)
                    with c_vs:
                        st.markdown(f"<p style='text-align:center; padding-top:20px;'>{row['hora_uy']} hs</p>", unsafe_allow_html=True)
                    with c2:
                        st.write(f"**{row['visitante']}**")
                        g_v = st.number_input("Goles", 0, 20, 0, key=f"v_{row['id']}", disabled=bloqueado)
                    st.markdown("</div>", unsafe_allow_html=True)
                    apuestas_lista.append([usuario, row['id'], g_l, g_v, ahora.strftime("%Y-%m-%d %H:%M")])
            
            if st.form_submit_button("GUARDAR MIS PRONÓSTICOS"):
                if usuario:
                    df_new = pd.DataFrame(apuestas_lista, columns=['usuario','partido_id','goles_local','goles_visitante','timestamp'])
                    df_old = obtener_datos("apuestas")
                    conn.update(worksheet="apuestas", data=pd.concat([df_old, df_new], ignore_index=True))
                    st.success("✅ ¡Pronósticos guardados!")
                else: st.error("⚠️ Ingresa tu nombre.")
    else: 
        st.warning("Carga los partidos en la planilla 'partidos'.")

# (Se mantienen Tab 2 y Tab 3 con la lógica previa)
