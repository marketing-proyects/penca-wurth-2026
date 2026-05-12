import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE INTERNO (Hardcoded para estabilidad) ---
def cargar_fixture():
    return pd.DataFrame([
        {"id": 1, "fecha": "2026-06-11", "hora": "17:00", "local": "México", "visitante": "EE.UU.", "sede": "Azteca"},
        {"id": 2, "fecha": "2026-06-12", "hora": "14:00", "local": "Uruguay", "visitante": "Corea del Sur", "sede": "Montevideo"},
        {"id": 3, "fecha": "2026-06-12", "hora": "20:00", "local": "Argentina", "visitante": "Arabia Saudita", "sede": "Lusail"},
    ])

# --- 3. ESTILO CEREBRO / GRADIENTE ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 5px; border: 1px solid #f0f0f0; display: inline-block; margin-bottom: 20px; }
    h1 { color: #ED1C24 !important; font-family: 'Arial Black'; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. INTERFAZ ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS (Registro único y bloqueo) ---
with tab1:
    df_partidos = cargar_fixture()
    try:
        df_historico = conn.read(worksheet="apuestas", ttl=0)
    except:
        df_historico = pd.DataFrame()

    with st.form("registro_penca"):
        st.subheader("📝 Datos del Participante")
        c1, c2, c3 = st.columns(3)
        nombre = c1.text_input("Nombre:")
        apellido = c2.text_input("Apellido:")
        email = c3.text_input("Email @wurth.com.uy:")
        sector = st.selectbox("Sector:", ["Ventas", "Logística", "Administración", "IT", "Marketing"])
        
        st.divider()
        st.subheader("⚽ Fase de Grupos")
        
        nuevos_pronosticos = []
        for _, row in df_partidos.iterrows():
            col_p, col_g = st.columns([3, 2])
            with col_p:
                st.write(f"**{row['local']} vs {row['visitante']}**")
                st.caption(f"{row['sede']} | {row['hora']} hs")
            with col_g:
                g1, g2 = st.columns(2)
                l = g1.number_input("L", 0, 20, 0, key=f"l_{row['id']}")
                v = g2.number_input("V", 0, 20, 0, key=f"v_{row['id']}")
            
            nuevos_pronosticos.append({
                "nombre": nombre, "apellido": apellido, "email": email, "sector": sector,
                "partido_id": row['id'], "goles_local": l, "goles_visitante": v,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        if st.form_submit_button("BLOQUEAR Y ENVIAR APUESTA"):
            # Validación de duplicados
            if not df_historico.empty and ((df_historico['nombre'] == nombre) & (df_historico['apellido'] == apellido)).any():
                st.error(f"Error: {nombre} {apellido} ya tiene una apuesta registrada y no puede modificarse.")
            elif not nombre or not apellido or "@" not in email:
                st.warning("Completa todos los campos obligatorios.")
            else:
                df_envio = pd.DataFrame(nuevos_pronosticos)
                df_final = pd.concat([df_historico, df_envio], ignore_index=True)
                conn.update(worksheet="apuestas", data=df_final)
                st.success("¡Apuesta enviada con éxito! Ya no puedes realizar cambios.")

# --- TAB 2: VENTAS (Embocarle al %) ---
with tab2:
    st.header("📊 Desafío de Ventas")
    st.write("Premio especial: Puntos extra por cercanía al 100% del plan mensual.")
    
    try:
        df_ventas = conn.read(worksheet="ventas", ttl=0)
        if not df_ventas.empty:
            # Aquí podrías mostrar el progreso actual del mes
            st.dataframe(df_ventas, use_container_width=True)
            st.info("Al final del mes, el sistema otorgará puntos a quienes tengan el % de cumplimiento más alto.")
    except:
        st.warning("Aún no se han cargado datos en la pestaña 'ventas' del Drive.")

# --- TAB 3: RANKING ---
with tab3:
    st.header("🥇 Ranking General")
    st.write("Calculando puntos (Acierto = 1pt, Resultado exacto = 3pts, Bono Ventas = 5pts)...")
