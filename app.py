import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE INTERNO (Fase de Grupos) ---
# Esto se carga una sola vez y no depende del Excel
def cargar_fixture():
    data = [
        {"id": 1, "fecha": "2026-06-11", "hora": "17:00", "local": "México", "visitante": "EE.UU.", "sede": "Estadio Azteca"},
        {"id": 2, "fecha": "2026-06-12", "hora": "14:00", "local": "Uruguay", "visitante": "Corea del Sur", "sede": "Montevideo (Sede ficticia)"},
        {"id": 3, "fecha": "2026-06-12", "hora": "20:00", "local": "Argentina", "visitante": "Arabia Saudita", "sede": "Lusail"},
        # Puedes seguir agregando todos los partidos aquí...
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (CEREBRO / GRADIENTE) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98), rgba(255,255,255,0.85)), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover;
    }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 5px; border: 1px solid #eee; display: inline-block; margin-bottom: 20px; }
    h1 { color: #ED1C24 !important; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LÓGICA DE NEGOCIO ---
def verificar_registro(nombre, apellido, df_apuestas):
    if df_apuestas.empty: return False
    # Verificación por nombre completo para evitar duplicados
    existe = df_apuestas[(df_apuestas['nombre'].str.lower() == nombre.lower()) & 
                         (df_apuestas['apellido'].str.lower() == apellido.lower())]
    return not existe.empty

# --- 5. INTERFAZ ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h1>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 MI DESEMPEÑO", "🥇 RANKING"])

with tab1:
    df_partidos = cargar_fixture()
    
    # Intentar leer apuestas existentes para validar duplicados
    try:
        df_historico = conn.read(worksheet="apuestas", ttl=0)
    except:
        df_historico = pd.DataFrame()

    with st.form("registro_penca"):
        st.subheader("📝 Registro de Usuario")
        col_n, col_a = st.columns(2)
        nombre = col_n.text_input("Nombre:")
        apellido = col_a.text_input("Apellido:")
        
        col_e, col_s = st.columns(2)
        email = col_e.text_input("Email Würth (Preferente):")
        sector = col_s.selectbox("Sector:", ["Ventas", "Logística", "Administración", "IT", "Marketing", "Otros"])
        
        st.divider()
        st.subheader("⚽ Tus Pronósticos")
        st.caption("Recuerda: Una vez enviados, no podrán ser modificados.")
        
        pronosticos_actuales = []
        for _, row in df_partidos.iterrows():
            c_partido, c_goles = st.columns([3, 2])
            with c_partido:
                st.write(f"**{row['local']} vs {row['visitante']}**")
                st.caption(f"{row['sede']} | {row['hora']} hs")
            with c_goles:
                g1, g2 = st.columns(2)
                g_l = g1.number_input("L", 0, 20, 0, key=f"l_{row['id']}")
                g_v = g2.number_input("V", 0, 20, 0, key=f"v_{row['id']}")
            
            pronosticos_actuales.append({
                "nombre": nombre, "apellido": apellido, "email": email, "sector": sector,
                "partido_id": row['id'], "goles_local": g_l, "goles_visitante": g_v,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            st.markdown("---")

        enviar = st.form_submit_button("ENVIAR PENCA (BLOQUEAR)")

        if enviar:
            if not nombre or not apellido or "@" not in email:
                st.error("Por favor completa tus datos correctamente.")
            elif verificar_registro(nombre, apellido, df_historico):
                st.warning(f"Lo sentimos, {nombre} {apellido} ya tiene una apuesta registrada. No se permiten duplicados.")
            else:
                try:
                    df_nuevo = pd.DataFrame(pronosticos_actuales)
                    df_final = pd.concat([df_historico, df_nuevo], ignore_index=True)
                    conn.update(worksheet="apuestas", data=df_final)
                    st.success("¡Pronósticos bloqueados y guardados con éxito! ¡Mucha suerte!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar en Drive: {e}")

with tab2:
    st.info("Aquí podrás ver tus aciertos una vez que el administrador cargue los resultados reales.")

with tab3:
    st.info("Ranking general basado en puntos por acierto de resultado y marcador exacto.")
