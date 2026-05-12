import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE INTERNO (Nombres Directos) ---
def cargar_fixture():
    return pd.DataFrame([
        {"id": 1, "e1": "México", "e2": "EE.UU.", "fecha": "11/06", "hora": "17:00"},
        {"id": 2, "e1": "Uruguay", "e2": "Corea del Sur", "fecha": "12/06", "hora": "14:00"},
        {"id": 3, "e1": "Argentina", "e2": "Arabia Saudita", "fecha": "12/06", "hora": "20:00"},
    ])

# --- 3. ESTILO VISUAL CEREBRO ---
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

st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS ---
with tab1:
    df_partidos = cargar_fixture()
    try:
        df_historico = conn.read(worksheet="apuestas", ttl=0)
    except:
        df_historico = pd.DataFrame()

    with st.form("registro_penca"):
        st.subheader("📝 Registro de Participante")
        c1, c2, c3 = st.columns(3)
        nombre = c1.text_input("Nombre:")
        apellido = c2.text_input("Apellido:")
        email = c3.text_input("Email @wurth.com.uy:")
        sector = st.selectbox("Sector:", ["Ventas", "Logística", "Administración", "IT", "Marketing", "Depósito"])
        
        st.divider()
        st.subheader("⚽ Fase de Grupos")
        
        apuestas_actuales = []
        for _, row in df_partidos.iterrows():
            col_txt, col_input = st.columns([3, 2])
            with col_txt:
                st.write(f"**{row['e1']} vs {row['e2']}**")
                st.caption(f"{row['fecha']} - {row['hora']} hs")
            with col_input:
                g1, g2 = st.columns(2)
                res1 = g1.number_input(f"Goles {row['e1']}", 0, 20, 0, key=f"e1_{row['id']}")
                res2 = g2.number_input(f"Goles {row['e2']}", 0, 20, 0, key=f"e2_{row['id']}")
            
            apuestas_actuales.append({
                "nombre": nombre, "apellido": apellido, "email": email, "sector": sector,
                "partido_id": row['id'], "goles_equipo_1": res1, "goles_equipo_2": res2,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        if st.form_submit_button("BLOQUEAR Y GUARDAR APUESTA"):
            # Validación de usuario único
            if not df_historico.empty and ((df_historico['nombre'] == nombre) & (df_historico['apellido'] == apellido)).any():
                st.error("Ya existe una apuesta registrada para este usuario. No se admiten cambios.")
            elif not nombre or not apellido or "@" not in email:
                st.warning("Completa todos los campos correctamente.")
            else:
                df_envio = pd.DataFrame(apuestas_actuales)
                df_final = pd.concat([df_historico, df_envio], ignore_index=True)
                conn.update(worksheet="apuestas", data=df_final)
                st.success("¡Apuesta registrada! Mucha suerte.")

# --- TAB 2: VENTAS ---
with tab2:
    st.header("📊 Desafío de Ventas")
    st.write("Premio al cumplimiento: Quien más se acerque al 100% del plan mensual suma puntos extra.")
    try:
        df_ventas = conn.read(worksheet="ventas", ttl=0)
        st.dataframe(df_ventas, use_container_width=True)
    except:
        st.info("Cargando datos de plan vs real...")

# --- TAB 3: RANKING ---
with tab3:
    st.header("🥇 Ranking de la Penca")
    st.write("Los puntos se calculan automáticamente comparando tus apuestas con los resultados reales en Drive.")
