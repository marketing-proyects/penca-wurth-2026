import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", layout="wide")

# Conexión a la base de datos (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILOS WÜRTH ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { background-color: #ED1C24; color: white; border: none; font-weight: bold; width: 100%; }
    .stButton>button:hover { background-color: #000000; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE DATOS ---
def get_partidos():
    return conn.read(worksheet="partidos")

# --- INTERFAZ ---
st.title("🏆 PENCA DIGITAL WÜRTH 2026")

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 KPI VENTAS", "🥇 RANKING"])

with tab1:
    st.header("Carga de Partidos")
    df_partidos = get_partidos()
    ahora = datetime.now()
    
    with st.form("penca_futbol"):
        usuario = st.text_input("Tu Nombre/Legajo:")
        
        apuestas_form = []
        for _, row in df_partidos.iterrows():
            # Validación de bloqueo (hora Uruguay)
            fecha_dt = datetime.strptime(f"{row['fecha']} {row['hora_uy']}", "%Y-%m-%d %H:%M")
            bloqueado = ahora >= fecha_dt
            
            col1, col2, col3 = st.columns([2,1,2])
            with col1: st.write(f"**{row['local']}**"); g_l = st.number_input("Goles", 0, 20, 0, key=f"l_{row['id']}", disabled=bloqueado)
            with col2: st.markdown("<p style='text-align:center;'>VS</p>", unsafe_allow_html=True)
            with col3: st.write(f"**{row['visitante']}**"); g_v = st.number_input("Goles", 0, 20, 0, key=f"v_{row['id']}", disabled=bloqueado)
            
            apuestas_form.append([usuario, row['id'], g_l, g_v, ahora.strftime("%Y-%m-%d %H:%M")])
            st.divider()

        if st.form_submit_button("GUARDAR PRONÓSTICOS"):
            if usuario:
                # Escribir en la hoja 'apuestas'
                df_apuestas = pd.DataFrame(apuestas_form, columns=['usuario', 'partido_id', 'goles_local', 'goles_visitante', 'timestamp'])
                # Leer existentes y concatenar
                df_prev = conn.read(worksheet="apuestas")
                df_final = pd.concat([df_prev, df_apuestas], ignore_index=True)
                conn.update(worksheet="apuestas", data=df_final)
                st.success("✅ ¡Pronósticos guardados en la nube!")
            else:
                st.error("Ingresa tu nombre")

with tab2:
    st.header("🎯 Desafío Especial de Ventas")
    with st.form("penca_ventas"):
        u_v = st.text_input("Nombre:")
        val = st.number_input("Cumplimiento esperado (%)", 0.00, 300.00, 100.00, step=0.01, format="%.2f")
        
        if st.form_submit_button("REGISTRAR APUESTA"):
            df_v = pd.DataFrame([[u_v, val, ahora.strftime("%Y-%m-%d %H:%M")]], columns=['usuario', 'apuesta_porcentaje', 'timestamp'])
            df_v_prev = conn.read(worksheet="ventas")
            df_v_final = pd.concat([df_v_prev, df_v], ignore_index=True)
            conn.update(worksheet="ventas", data=df_v_final)
            st.success(f"Registrado: {val}%")

with tab3:
    st.header("🥇 Posiciones")
    # Mostrar tablas de la nube
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Fútbol")
        st.dataframe(conn.read(worksheet="apuestas").tail(10))
    with col_b:
        st.subheader("Ventas")
        st.dataframe(conn.read(worksheet="ventas").tail(10))
