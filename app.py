import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE INTERNO (Fase de Grupos) ---
def cargar_fixture():
    data = [
        {"id": 1, "grupo": "GRUPO A", "e1": "México", "e2": "EE.UU.", "fecha": "11/06", "hora": "17:00"},
        {"id": 2, "grupo": "GRUPO A", "e1": "Uruguay", "e2": "Corea del Sur", "fecha": "12/06", "hora": "14:00"},
        {"id": 3, "grupo": "GRUPO B", "e1": "Argentina", "e2": "Arabia Saudita", "fecha": "12/06", "hora": "20:00"},
        {"id": 4, "grupo": "GRUPO B", "e1": "Francia", "e2": "Australia", "fecha": "13/06", "hora": "15:00"},
        # Puedes seguir completando la lista aquí...
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (CEREBRO + GRADIENTE) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.82) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 5px; border: 1px solid #f0f0f0; display: inline-block; margin-bottom: 20px; }
    h1, h2 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .grupo-header { 
        background-color: #ED1C24; color: white; padding: 12px; border-radius: 4px; 
        margin-top: 25px; font-weight: bold; font-size: 18px;
    }
    .main-title { color: #ED1C24; font-size: 42px; font-family: 'Arial Black'; margin-bottom: 30px; letter-spacing: -1px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RENDER CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS ---
with tab1:
    df_fixture = cargar_fixture()
    
    # Inicializar estado de navegación si no existe
    if 'paso_registro' not in st.session_state:
        st.session_state.paso_registro = False

    # PASO 1: Identificación
    st.subheader("👤 Registro del Colaborador")
    col1, col2 = st.columns(2)
    u_nombre = col1.text_input("Nombre:").strip()
    u_apellido = col2.text_input("Apellido:").strip()
    
    col3, col4 = st.columns(2)
    u_email = col3.text_input("Email:")
    u_sector = col4.selectbox("Sector:", ["Ventas", "Logística", "Administración", "IT", "Marketing", "Depósito", "Directorio"])

    if st.button("INGRESAR AL FIXTURE"):
        if u_nombre and u_apellido and "@" in u_email:
            st.session_state.paso_registro = True
            st.rerun()
        else:
            st.error("Por favor, completa Nombre, Apellido e Email válido para continuar.")

    # PASO 2: Mostrar Fixture si ya se identificó
    if st.session_state.paso_registro:
        st.divider()
        st.success(f"Bienvenido {u_nombre}. Puedes completar tus pronósticos a continuación.")
        
        # Cargar apuestas previas para permitir "Guardado Parcial"
        try:
            df_todas = conn.read(worksheet="apuestas", ttl=0)
            df_usu = df_todas[(df_todas['nombre'].str.lower() == u_nombre.lower()) & 
                             (df_todas['apellido'].str.lower() == u_apellido.lower())]
        except:
            df_todas = pd.DataFrame()
            df_usu = pd.DataFrame()

        with st.form("penca_grupos"):
            grupos = df_fixture['grupo'].unique()
            
            for g in grupos:
                st.markdown(f'<div class="grupo-header">{g}</div>', unsafe_allow_html=True)
                partidos_grupo = df_fixture[df_fixture['grupo'] == g]
                
                for _, row in partidos_grupo.iterrows():
                    # Valores por defecto (si ya existen en el drive)
                    v1, v2 = 0, 0
                    if not df_usu.empty:
                        prev = df_usu[df_usu['partido_id'] == row['id']]
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
            
            if st.form_submit_button("💾 GUARDAR AVANCES"):
                nuevas = []
                for _, row in df_fixture.iterrows():
                    nuevas.append({
                        "nombre": u_nombre, "apellido": u_apellido, "email": u_email, "sector": u_sector,
                        "partido_id": row['id'], 
                        "goles_equipo_1": st.session_state[f"e1_{row['id']}"],
                        "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                
                df_envio = pd.DataFrame(nuevas)
                # Limpiar registros anteriores del mismo usuario en el DataFrame antes de subir
                if not df_todas.empty:
                    df_limpio = df_todas[~((df_todas['nombre'].str.lower() == u_nombre.lower()) & 
                                          (df_todas['apellido'].str.lower() == u_apellido.lower()))]
                    df_final = pd.concat([df_limpio, df_envio], ignore_index=True)
                else:
                    df_final = df_envio
                
                conn.update(worksheet="apuestas", data=df_final)
                st.success("Tus pronósticos han sido guardados. Puedes volver más tarde si deseas cambiarlos.")
                st.balloons()

# --- TAB 2: VENTAS ---
with tab2:
    st.header("📊 Desafío de Ventas")
    st.write("Suma puntos extra por cumplimiento de objetivos de empresa.")
    try:
        df_v = conn.read(worksheet="ventas", ttl=0)
        st.dataframe(df_v, use_container_width=True)
    except:
        st.info("Planilla de ventas en proceso de actualización.")

# --- TAB 3: RANKING ---
with tab3:
    st.header("🥇 Tabla de Posiciones")
    st.write("Cargando puntajes oficiales...")
