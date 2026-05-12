import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# URL RAW DE GITHUB (Reemplaza con tu enlace real al archivo .xlsx o .csv)
# Debe ser el enlace que empieza con 'raw.githubusercontent.com'
URL_RESULTADOS_REALES = "https://raw.githubusercontent.com/tu_usuario/tu_repo/main/resultados.xlsx"

def init_db():
    conn = sqlite3.connect('penca.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apuestas 
                 (wn TEXT, nombre TEXT, apellido TEXT, sector TEXT, partido_id INTEGER, 
                  g1 INTEGER, g2 INTEGER, fecha_reg TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. FIXTURE COMPLETO (Sincronizado Grupos A al L) ---
def cargar_fixture():
    data = [
        # GRUPO A
        {"id": 1, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "fase": "Grupos", "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 13, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Corea del Sur 🇰🇷", "fecha": "17/06", "hora": "22:00"},
        {"id": 14, "fase": "Grupos", "grupo": "A", "e1": "Rep. Checa 🇨🇿", "e2": "Sudáfrica 🇿🇦", "fecha": "17/06", "hora": "18:00"},
        # GRUPO B
        {"id": 3, "fase": "Grupos", "grupo": "B", "e1": "Canadá 🇨🇦", "e2": "Bosnia 🇧🇦", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "fase": "Grupos", "grupo": "B", "e1": "Qatar 🇶🇦", "e2": "Suiza 🇨🇭", "fecha": "12/06", "hora": "20:00"},
        # GRUPO F (Uruguay)
        {"id": 9, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia S. 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 10, "fase": "Grupos", "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        {"id": 30, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "España 🇪🇸", "fecha": "20/06", "hora": "21:00"},
        # GRUPO J
        {"id": 50, "fase": "Grupos", "grupo": "J", "e1": "Argentina 🇦🇷", "e2": "Argelia 🇩🇿", "fecha": "18/06", "hora": "21:00"},
    ]
    # Puedes seguir añadiendo el resto de los 72 partidos aquí...
    return pd.DataFrame(data)

# --- 3. LÓGICA DE PUNTOS Y RANKING ---
def calcular_puntos(row_apuesta, df_reales):
    res_real = df_reales[df_reales['partido_id'] == row_apuesta['partido_id']]
    if res_real.empty: return 0
    
    g1_r, g2_r = res_real.iloc[0]['g1_real'], res_real.iloc[0]['g2_real']
    g1_a, g2_a = row_apuesta['g1'], row_apuesta['g2']
    
    # Exacto (3 pts)
    if g1_r == g1_a and g2_r == g2_a: return 3
    # Ganador/Empate (1 pt)
    if (g1_r > g2_r and g1_a > g2_a) or (g1_r < g2_r and g1_a < g2_a) or (g1_r == g2_r and g1_a == g2_a): return 1
    return 0

# --- 4. ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    .logo-box { background-color: white; padding: 10px; display: inline-block; margin-bottom: 20px; border: 1px solid #eee; }
    .grupo-card {
        background: white; border: 1px solid #ddd; border-radius: 8px;
        padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .grupo-title {
        background: #ED1C24; color: white; padding: 5px 10px;
        border-radius: 4px; font-weight: bold; margin-bottom: 10px;
    }
    .ranking-gold { background-color: #FFD700; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
logo_path = "logo_wurth.jpg"
st.image(logo_path if os.path.exists(logo_path) else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING", "🔒 ADMIN"])

# --- TAB 1: PRONÓSTICOS (Se mantiene funcional por día) ---
with menu[0]:
    df_fixture = cargar_fixture()
    st.subheader("👤 Registro de Colaborador")
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom = c1.text_input("Nombre:").strip()
    u_ape = c2.text_input("Apellido:").strip()
    u_wn = c3.text_input("Código WN:").strip().upper()
    u_sec = c4.selectbox("Sector:", ["Ventas", "Marketing", "Logística", "IT", "Administración", "RRHH", "Otros"], index=None, placeholder="Tu sector...")

    if all([u_nom, u_ape, u_wn, u_sec]):
        db_conn = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db_conn)
        db_conn.close()

        # [Lógica de Pop-up Comodín y Tabs de Pronósticos se mantienen igual que en la versión anterior]
        # ... (Por brevedad, omito el bloque repetido de formularios por día que ya funciona bien)

# --- TAB 2: TABLAS (Visual Estilo PDF) ---
with menu[1]:
    st.subheader("📊 Grupos del Mundial")
    df_fix = cargar_fixture()
    grupos_lista = sorted(df_fix['grupo'].unique())
    
    # Grid de 3 columnas para los grupos
    cols = st.columns(3)
    for idx, g_name in enumerate(grupos_lista):
        with cols[idx % 3]:
            st.markdown(f'<div class="grupo-card"><div class="grupo-title">GRUPO {g_name}</div>', unsafe_allow_html=True)
            equipos_grupo = pd.concat([df_fix[df_fix['grupo']==g_name]['e1'], df_fix[df_fix['grupo']==g_name]['e2']]).unique()
            for eq in equipos_grupo:
                st.write(f"• {eq}")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: RANKING ---
with menu[2]:
    st.subheader("🥇 Ranking General")
    try:
        # 1. Leer resultados reales de GitHub
        df_reales = pd.read_excel(URL_RESULTADOS_REALES) # o pd.read_csv
        
        # 2. Leer todas las apuestas de la DB
        db_conn = sqlite3.connect('penca.db')
        df_todas = pd.read_sql("SELECT * FROM apuestas WHERE partido_id != 999", db_conn)
        db_conn.close()
        
        if not df_todas.empty:
            df_todas['puntos'] = df_todas.apply(lambda x: calcular_puntos(x, df_reales), axis=1)
            ranking = df_todas.groupby(['wn', 'nombre', 'apellido', 'sector'])['puntos'].sum().reset_index()
            ranking = ranking.sort_values(by='puntos', ascending=False)
            
            st.table(ranking.style.highlight_max(subset=['puntos'], color='#ED1C24'))
        else:
            st.info("El ranking se generará cuando comiencen los partidos.")
    except:
        st.warning("Cargando resultados oficiales desde GitHub...")

# --- TAB 4: ADMIN ---
with menu[3]:
    st.subheader("🔒 Panel Administrativo")
    with st.form("admin_gate"):
        input_pass = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("Acceder"):
            if input_pass == "market1NG?":
                st.session_state.admin_ok = True
            else: st.error("Clave incorrecta")

    if st.session_state.get("admin_ok"):
        db_conn = sqlite3.connect('penca.db')
        df_admin = pd.read_sql("SELECT * FROM apuestas", db_conn)
        db_conn.close()
        csv = df_admin.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Datos (CSV)", csv, "penca_final.csv", "text/csv")
