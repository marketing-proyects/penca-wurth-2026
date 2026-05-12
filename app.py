import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE INTERNO POR GRUPOS (Información estática) ---
def cargar_fixture():
    data = [
        {"id": 1, "grupo": "GRUPO A", "e1": "México", "e2": "EE.UU.", "fecha": "11/06", "hora": "17:00"},
        {"id": 2, "grupo": "GRUPO A", "e1": "Uruguay", "e2": "Corea del Sur", "fecha": "12/06", "hora": "14:00"},
        {"id": 3, "grupo": "GRUPO B", "e1": "Argentina", "e2": "Arabia Saudita", "fecha": "12/06", "hora": "20:00"},
        {"id": 4, "grupo": "GRUPO B", "e1": "Francia", "e2": "Australia", "fecha": "13/06", "hora": "15:00"},
        # Puedes completar aquí todos los partidos del mundial
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (Técnica CEREBRO + Gradiente) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.82) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box-cerebro { background-color: white; padding: 5px; border-radius: 0px !important; display: inline-block; margin-bottom: 20px; border: 1px solid #f0f0f0; }
    h1, h2 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .grupo-header { 
        background-color: #ED1C24; color: white; padding: 12px; border-radius: 4px; 
        margin-top: 25px; font-weight: bold; font-size: 18px; letter-spacing: 1px;
    }
    .main-title { color: #ED1C24; font-size: 42px; font-family: 'Arial Black'; margin-bottom: 30px; letter-spacing: -1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RENDER CABECERA ---
st.markdown('<div class="logo-box-cerebro">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS ---
with tab1:
    df_fixture = cargar_fixture()
    
    st.subheader("👤 Identificación de Usuario")
    c1, c2, c3, c4 = st.columns(4)
    u_nombre = c1.text_input("Nombre:").strip()
    u_apellido = c2.text_input("Apellido:").strip()
    u_email = c3.text_input("Email @wurth.com.uy:")
    u_sector = c4.selectbox("Sector:", ["Ventas", "Logística", "Administración", "IT", "Marketing", "Depósito"])

    if u_nombre and u_apellido:
        # Intentar leer base de datos de apuestas
        try:
            df_apuestas_todas = conn.read(worksheet="apuestas", ttl=0)
            df_usuario = df_apuestas_todas[(df_apuestas_todas['nombre'].str.lower() == u_nombre.lower()) & 
                                         (df_apuestas_todas['apellido'].str.lower() == u_apellido.lower())]
        except:
            df_apuestas_todas = pd.DataFrame()
            df_usuario = pd.DataFrame()

        st.divider()
        st.info(f"Hola {u_nombre}, puedes completar o modificar tus pronósticos. No olvides darle a 'Guardar' al finalizar.")
        
        grupos = df_fixture['grupo'].unique()
        
        with st.form("penca_fase_grupos"):
            for g in grupos:
                st.markdown(f'<div class="grupo-header">{g}</div>', unsafe_allow_html=True)
                partidos_grupo = df_fixture[df_fixture['grupo'] == g]
                
                for _, row in partidos_grupo.iterrows():
                    # Cargar valores previos si existen
                    v1, v2 = 0, 0
                    if not df_usuario.empty:
                        prev = df_usuario[df_usuario['partido_id'] == row['id']]
                        if not prev.empty:
                            v1 = int(prev.iloc[0]['goles_equipo_1'])
                            v2 = int(prev.iloc[0]['goles_equipo_2'])

                    col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                    with col_p:
                        st.markdown(f"<div style='padding-top:15px;'><b>{row['e1']} vs {row['e2']}</b><br><small>{row['fecha']} - {row['hora']} hs</small></div>", unsafe_allow_html=True)
                    with col_g1:
                        res1 = st.number_input(f"Goles {row['e1']}", 0, 20, v1, key=f"e1_{row['id']}")
                    with col_g2:
                        res2 = st.number_input(f"Goles {row['e2']}", 0, 20, v2, key=f"e2_{row['id']}")
            
            if st.form_submit_button("💾 GUARDAR PRONÓSTICOS"):
                if "@" not in u_email:
                    st.error("Ingresa un email válido.")
                else:
                    # Preparar nuevos registros
                    nuevas = []
                    for _, row in df_fixture.iterrows():
                        nuevas.append({
                            "nombre": u_nombre, "apellido": u_apellido, "email": u_email, "sector": u_sector,
                            "partido_id": row['id'], 
                            "goles_equipo_1": st.session_state[f"e1_{row['id']}"],
                            "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                    
                    df_nuevas = pd.DataFrame(nuevas)
                    # Eliminar registros anteriores del usuario y agregar los actuales
                    if not df_apuestas_todas.empty:
                        df_limpio = df_apuestas_todas[~((df_apuestas_todas['nombre'].str.lower() == u_nombre.lower()) & 
                                                       (df_apuestas_todas['apellido'].str.lower() == u_apellido.lower()))]
                        df_final = pd.concat([df_limpio, df_nuevas], ignore_index=True)
                    else:
                        df_final = df_nuevas
                    
                    conn.update(worksheet="apuestas", data=df_final)
                    st.success("¡Pronósticos actualizados en el sistema!")
                    st.balloons()
    else:
        st.warning("Escribe tu nombre y apellido para habilitar el fixture.")

# --- TAB 2: VENTAS ---
with tab2:
    st.header("📊 Desafío de Ventas")
    st.write("Premio al cumplimiento del plan.")
    try:
        df_v = conn.read(worksheet="ventas", ttl=0)
        st.dataframe(df_v, use_container_width=True)
    except:
        st.info("Esperando carga de datos de ventas...")

# --- TAB 3: RANKING ---
with tab3:
    st.header("🥇 Ranking")
    st.write("El ranking se calculará cruzando tus apuestas con la pestaña 'partidos' del Drive.")
