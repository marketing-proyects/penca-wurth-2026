import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# Conexión centralizada a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILOS CORPORATIVOS WÜRTH ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .stButton>button { 
        background-color: #ED1C24; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold; height: 3em;
    }
    .stButton>button:hover { background-color: #000000; color: white; }
    [data-testid="stMetricValue"] { color: #ED1C24; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f0f2f6; border-radius: 4px 4px 0 0; padding: 10px 20px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---

def obtener_datos(pestana):
    return conn.read(worksheet=pestana, ttl=0) # ttl=0 para datos frescos

def calcular_puntos_futbol(row_apuesta, df_partidos):
    partido = df_partidos[df_partidos['id'] == row_apuesta['partido_id']]
    if partido.empty or pd.isna(partido.iloc[0]['resultado_local']):
        return 0
    
    real_l = partido.iloc[0]['resultado_local']
    real_v = partido.iloc[0]['resultado_visitante']
    apuesta_l = row_apuesta['goles_local']
    apuesta_v = row_apuesta['goles_visitante']
    
    # Acierto Exacto: 3 pts
    if real_l == apuesta_l and real_v == apuesta_v:
        return 3
    # Acierto Ganador/Empate: 1 pt
    if (real_l > real_v and apuesta_l > apuesta_v) or \
       (real_l < real_v and apuesta_l < apuesta_v) or \
       (real_l == real_v and apuesta_l == apuesta_v):
        return 1
    return 0

# --- ESTRUCTURA DE LA APP ---
st.title("🏆 PENCA DIGITAL WÜRTH 2026")
st.subheader("Market Intelligence Unit • Uruguay")

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING GENERAL"])

# --- TAB 1: PRONÓSTICOS FÚTBOL ---
with tab1:
    st.header("Fixture y Carga de Goles")
    df_partidos = obtener_datos("partidos")
    ahora = datetime.now()

    with st.form("form_futbol"):
        usuario = st.text_input("Ingresa tu Nombre Completo:", placeholder="Ej: Diego_W")
        st.divider()
        
        nuevas_apuestas = []
        for _, row in df_partidos.iterrows():
            # Bloqueo: Hora Uruguay
            f_partido = datetime.strptime(f"{row['fecha']} {row['hora_uy']}", "%Y-%m-%d %H:%M")
            bloqueado = ahora >= f_partido
            
            col1, col_vs, col2 = st.columns([2, 1, 2])
            with col1:
                st.write(f"**{row['local']}**")
                g_l = st.number_input("Goles", 0, 20, 0, key=f"l_{row['id']}", disabled=bloqueado)
            with col_vs:
                st.markdown(f"<p style='text-align:center; padding-top:25px;'>{row['hora_uy']}hs</p>", unsafe_allow_html=True)
            with col2:
                st.write(f"**{row['visitante']}**")
                g_v = st.number_input("Goles", 0, 20, 0, key=f"v_{row['id']}", disabled=bloqueado)
            
            nuevas_apuestas.append([usuario, row['id'], g_l, g_v, ahora.strftime("%Y-%m-%d %H:%M")])
            st.divider()

        if st.form_submit_button("GUARDAR MIS PRONÓSTICOS"):
            if usuario:
                df_apuestas_nuevas = pd.DataFrame(nuevas_apuestas, columns=['usuario', 'partido_id', 'goles_local', 'goles_visitante', 'timestamp'])
                df_actual = obtener_datos("apuestas")
                df_final = pd.concat([df_actual, df_apuestas_nuevas], ignore_index=True)
                conn.update(worksheet="apuestas", data=df_final)
                st.success("✅ ¡Pronósticos guardados exitosamente!")
            else:
                st.error("⚠️ Debes ingresar tu nombre.")

# --- TAB 2: KPI VENTAS (DÍA ESPECIAL) ---
with tab2:
    st.header("🎯 Bono de Precisión: Día de Ventas")
    st.write("Apostá al cumplimiento final del día especial de ventas (Junio 2026).")
    
    with st.form("form_ventas"):
        u_v = st.text_input("Tu Nombre:", key="u_v")
        val_v = st.number_input("¿Qué % de cumplimiento haremos? (2 decimales)", 0.00, 300.00, 100.00, step=0.01, format="%.2f")
        
        if st.form_submit_button("REGISTRAR APUESTA DE VENTAS"):
            if u_v:
                df_v_nuevas = pd.DataFrame([[u_v, val_v, ahora.strftime("%Y-%m-%d %H:%M")]], columns=['usuario', 'apuesta_porcentaje', 'timestamp'])
                df_v_actual = obtener_datos("ventas")
                df_v_final = pd.concat([df_v_actual, df_v_nuevas], ignore_index=True)
                conn.update(worksheet="ventas", data=df_v_final)
                st.success(f"🎯 Registrado: {val_v}% para {u_v}")
            else:
                st.error("⚠️ Falta tu nombre.")

# --- TAB 3: RANKING GENERAL ---
with tab3:
    st.header("🥇 Tabla de Posiciones")
    
    # Cargar todos los datos para el cálculo
    df_p = obtener_datos("partidos")
    df_a = obtener_datos("apuestas")
    df_v = obtener_datos("ventas")
    
    if not df_a.empty:
        # 1. Calcular puntos de fútbol
        df_a['puntos'] = df_a.apply(lambda x: calcular_puntos_futbol(x, df_p), axis=1)
        ranking_f = df_a.groupby('usuario')['puntos'].sum().reset_index()
        
        # 2. Lógica Especial Ventas (10 pts por aproximación)
        # Supongamos que el resultado real se carga en una variable o celda especial. 
        # Aquí lo definimos (tú lo cambiarás cuando sepa el real):
        RESULTADO_REAL_VENTAS = 101.60 
        
        if not df_v.empty:
            df_v['error'] = abs(df_v['apuesta_porcentaje'] - RESULTADO_REAL_VENTAS).round(2)
            error_minimo = df_v['error'].min()
            df_v['puntos_v'] = df_v['error'].apply(lambda x: 10 if x == error_minimo else 0)
            ranking_v = df_v.groupby('usuario')['puntos_v'].sum().reset_index()
            
            # Unificar rankings
            ranking_final = pd.merge(ranking_f, ranking_v, on='usuario', how='outer').fillna(0)
            ranking_final['Total'] = ranking_final['puntos'] + ranking_final['puntos_v']
        else:
            ranking_final = ranking_f
            ranking_final['Total'] = ranking_final['puntos']

        ranking_final = ranking_final.sort_values(by='Total', ascending=False)
        
        # Visualización
        st.table(ranking_final[['usuario', 'Total']].rename(columns={'usuario': 'Participante', 'Total': 'Puntos Totales'}))
    else:
        st.info("Esperando las primeras apuestas para generar el ranking...")
