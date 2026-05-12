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

# --- 2. CSS: ESTILO CEREBRO / GRADIENTE / BLINDAJE ---
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
            rgba(255, 255, 255, 0.82) 100%
        ), 
        url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box-cerebro {
        background-color: white !important;
        padding: 4px !important;
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

# --- 3. FUNCIÓN DE DATOS CON MANEJO DE ERRORES CRÍTICOS ---
def obtener_datos(pestana):
    try:
        # ttl=0 forzado para evitar el error de caché de la imagen
        df = conn.read(worksheet=pestana, ttl=0)
        if df is not None and not df.empty:
            # Limpiar nombres de columnas
            df.columns = [str(c).strip().lower() for c in df.columns]
            # Eliminar filas/columnas fantasma
            df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
            return df
        return pd.DataFrame()
    except Exception as e:
        # Si falla por "EmptyData", devolvemos DF vacío sin romper la app
        return pd.DataFrame()

# --- 4. CABECERA ---
st.markdown('<div class="logo-box-cerebro">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=220)
else:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=220)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

# --- 5. TABS ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    df_partidos = obtener_datos("partidos")

    # Columnas mínimas para operar
    cols_necesarias = ['id', 'local', 'visitante']
    
    if not df_partidos.empty and all(c in df_partidos.columns for c in cols_necesarias):
        with st.form("form_penca"):
            usuario = st.text_input("Participante:", placeholder="Tu nombre")
            st.divider()
            
            respuestas = []
            for _, row in df_partidos.iterrows():
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"**{row['local']} vs {row['visitante']}**")
                    st.caption(f"{row.get('fecha', '-')} | {row.get('hora_uy', '-')} hs")
                
                with col2:
                    c1, c2 = st.columns(2)
                    g_l = c1.number_input("L", 0, 20, 0, key=f"l_{row['id']}")
                    g_v = c2.number_input("V", 0, 20, 0, key=f"v_{row['id']}")
                
                respuestas.append({
                    "usuario": usuario,
                    "partido_id": row['id'],
                    "goles_local": g_l,
                    "goles_visitante": g_v,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.markdown("---")
            
            if st.form_submit_button("GUARDAR PRONÓSTICOS"):
                if usuario:
                    try:
                        df_nuevas = pd.DataFrame(respuestas)
                        df_actual = obtener_datos("apuestas")
                        df_final = pd.concat([df_actual, df_nuevas], ignore_index=True)
                        conn.update(worksheet="apuestas", data=df_final)
                        st.success(f"✅ ¡Guardado con éxito, {usuario}!")
                    except:
                        st.error("Error al guardar. Verifica que exista la pestaña 'apuestas'.")
                else:
                    st.error("⚠️ El nombre es obligatorio.")
    else:
        st.warning("⚠️ No se detectan datos en 'partidos'.")
        if not df_partidos.empty:
            st.write("Columnas detectadas:", list(df_partidos.columns))
        st.info("Asegúrate de que los encabezados estén en la FILA 1 de la hoja 'partidos'.")

with tab2:
    st.header("📊 Desafío Ventas")
    st.write("Seguimiento de objetivos comerciales.")

with tab3:
    st.header("🥇 Ranking")
    st.write("Tabla de posiciones de la Penca.")
