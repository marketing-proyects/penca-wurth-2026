import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# Conexión a Google Sheets (Asegúrate de tener el Secret configurado)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILOS CORPORATIVOS WÜRTH ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .stButton>button { 
        background-color: #ED1C24; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold; height: 3.5em;
    }
    .stButton>button:hover { background-color: #000000; color: white; }
    [data-testid="stMetricValue"] { color: #ED1C24; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f0f2f6; border-radius: 4px 4px 0 0; padding: 10px 20px; 
    }
    /* Estilo para los contenedores de partidos */
    .partido-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 8px solid #eee;
    }
    .partido-uruguay { border-left: 8px solid #ED1C24; background-color: #fff5f5; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA DE DATOS ---

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
    
    if real_l == ap_l and real_v == ap_v: return 3 # Exacto
    if (real_l > real_v and ap_l > ap_v) or \
       (real_l < real_v and ap_l < ap_v) or \
       (real_l == real_v and ap_l == ap_v): return 1 # Ganador/Empate
    return 0

# --- CABECERA ---
with st.container():
    col_l, col_r = st.columns([1, 5])
    with col_l:
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=120)
    with col_r:
        st.title("PENCA DIGITAL WÜRTH 2026")
        st.markdown("**Market Intelligence Unit • Uruguay**")

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS ---
with tab1:
    st.header("Fixture Mundialista")
    df_partidos = obtener_datos("partidos")
    ahora = datetime.now()

    if not df_partidos.empty:
        with st.form("form_penca"):
            usuario = st.text_input("Ingresa tu Nombre Completo:", placeholder="Ej: Diego_W")
            st.divider()
            
            apuestas_lista = []
            for _, row in df_partidos.iterrows():
                # Destaque de Uruguay
                es_uruguay = row['local'] == 'Uruguay' or row['visitante'] == 'Uruguay'
                clase_card = "partido-uruguay" if es_uruguay else ""
                
                # Bloqueo por tiempo
                f_dt = datetime.strptime(f"{row['fecha']} {row['hora_uy']}", "%Y-%m-%d %H:%M")
                bloqueado = ahora >= f_dt

                st.markdown(f"<div class='partido-card {clase_card}'>", unsafe_allow_html=True)
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
                    st.success("⚽ ¡Pronósticos guardados!")
                else: st.error("Ingresa tu nombre")
    else: st.warning("Carga los partidos en la planilla 'partidos'.")

# --- TAB 2: VENTAS ---
with tab2:
    st.header("🎯 Bono Especial: Día de Ventas")
    st.write("Apostá al cumplimiento final del objetivo (2 decimales).")
    with st.form("form_v"):
        u_v = st.text_input("Nombre:", key="v_name")
        val_v = st.number_input("Cumplimiento (%)", 0.00, 300.00, 100.00, step=0.01, format="%.2f")
        if st.form_submit_button("REGISTRAR APUESTA VENTAS"):
            if u_v:
                df_v_new = pd.DataFrame([[u_v, val_v, ahora.strftime("%Y-%m-%d %H:%M")]], columns=['usuario','apuesta_porcentaje','timestamp'])
                df_v_old = obtener_datos("ventas")
                conn.update(worksheet="ventas", data=pd.concat([df_v_old, df_v_new], ignore_index=True))
                st.success(f"🎯 Registrado: {val_v}%")
            else: st.error("Ingresa tu nombre")

# --- TAB 3: RANKING ---
with tab3:
    st.header("🥇 Posiciones Generales")
    df_p = obtener_datos("partidos")
    df_a = obtener_datos("apuestas")
    df_v = obtener_datos("ventas")
    
    if not df_a.empty and 'usuario' in df_a.columns:
        df_a['puntos'] = df_a.apply(lambda x: calcular_puntos_futbol(x, df_p), axis=1)
        rank = df_a.groupby('usuario')['puntos'].sum().reset_index()
        
        # Valor real del KPI (Se edita aquí cuando se sepa)
        VALOR_REAL_KPI = 101.60 
        
        if not df_v.empty and 'usuario' in df_v.columns:
            df_v['err'] = abs(df_v['apuesta_porcentaje'] - VALOR_REAL_KPI).round(2)
            min_err = df_v['err'].min()
            df_v['puntos_v'] = df_v['err'].apply(lambda x: 10 if x == min_err else 0)
            rank_v = df_v.groupby('usuario')['puntos_v'].sum().reset_index()
            rank = pd.merge(rank, rank_v, on='usuario', how='outer').fillna(0)
            rank['Total'] = rank['puntos'] + rank['puntos_v']
        else:
            rank['Total'] = rank['puntos']
            
        rank = rank.sort_values(by='Total', ascending=False)
        st.table(rank[['usuario', 'Total']].rename(columns={'usuario': 'Participante', 'Total': 'Puntos'}))
    else:
        st.info("Aún no hay apuestas registradas.")
