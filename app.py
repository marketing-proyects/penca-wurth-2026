import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTILOS Y LIMPIEZA DE INTERFAZ (Ocultar Menú/Share/Estrella) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    
    /* Configuración Visual Würth */
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .main-title {
        color: #ED1C24;
        font-size: 38px;
        font-family: 'Arial Black', sans-serif;
        margin-top: -15px;
        font-weight: bold;
    }
    
    .stButton>button { 
        background-color: #ED1C24; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold; height: 3em;
    }
    .stButton>button:hover { background-color: #000000; color: white; }
    
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f0f2f6; border-radius: 4px 4px 0 0; padding: 8px 20px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
with st.container():
    col1, col2 = st.columns([1, 4])
    with col1:
        # Logo oficial desde repositorio público
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
    with col2:
        st.markdown("<h1 class='main-title'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)
        st.markdown("<p style='margin-top:-20px; font-weight:bold; color: #555;'>Market Intelligence Unit • Uruguay</p>", unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ---
def obtener_datos(pestana):
    try:
        return conn.read(worksheet=pestana, ttl=0)
    except:
        return pd.DataFrame()

def calcular_puntos_futbol(row_apuesta, df_partidos):
    if df_partidos.empty: return 0
    p = df_partidos[df_partidos['id'] == row_apuesta['partido_id']]
    if p.empty or pd.isna(p.iloc[0]['resultado_local']): return 0
    rl, rv = p.iloc[0]['resultado_local'], p.iloc[0]['resultado_visitante']
    al, av = row_apuesta['goles_local'], row_apuesta['goles_visitante']
    if rl == al and rv == av: return 3
    if (rl > rv and al > av) or (rl < rv and al < av) or (rl == rv and al == av): return 1
    return 0

# --- ESTRUCTURA DE TABS ---
tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 DESAFÍO VENTAS", "🥇 RANKING"])

with tab1:
    st.header("FIXTURE MUNDIALISTA")
    df_partidos = obtener_datos("partidos")
    ahora = datetime.now()

    if not df_partidos.empty:
        with st.form("form_futbol"):
            usuario = st.text_input("Ingresa tu Nombre Completo:", placeholder="Ej: Diego_W")
            st.divider()
            
            apuestas_lista = []
            for _, row in df_partidos.iterrows():
                es_uruguay = row['local'] == 'Uruguay' or row['visitante'] == 'Uruguay'
                border = "8px solid #ED1C24" if es_uruguay else "1px solid #ddd"
                
                # Bloqueo horario (Hora Uruguay)
                f_dt = datetime.strptime(f"{row['fecha']} {row['hora_uy']}", "%Y-%m-%d %H:%M")
                bloqueado = ahora >= f_dt

                st.markdown(f"<div style='border-left: {border}; padding: 15px; margin-bottom:10px; border-radius:5px; background-color:#f9f9f9;'>", unsafe_allow_html=True)
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
                    st.success("✅ ¡Pronósticos guardados exitosamente!")
                else: st.error("⚠️ Falta el nombre de usuario.")
    else:
        st.warning("Carga los partidos en la planilla 'partidos'.")

with tab2:
    st.header("🎯 DESAFÍO ESPECIAL DE VENTAS")
    with st.form("form_ventas"):
        u_v = st.text_input("Nombre:", key="v_u")
        val_v = st.number_input("Cumplimiento esperado (%)", 0.00, 300.00, 100.00, step=0.01, format="%.2f")
        if st.form_submit_button("REGISTRAR APUESTA VENTAS"):
            if u_v:
                df_v_new = pd.DataFrame([[u_v, val_v, ahora.strftime("%Y-%m-%d %H:%M")]], columns=['usuario','apuesta_porcentaje','timestamp'])
                df_v_old = obtener_datos("ventas")
                conn.update(worksheet="ventas", data=pd.concat([df_v_old, df_v_new], ignore_index=True))
                st.success(f"🎯 Registrado: {val_v}% para {u_v}")
            else: st.error("⚠️ Ingresa tu nombre.")

with tab3:
    st.header("🥇 RANKING GENERAL")
    df_p = obtener_datos("partidos")
    df_a = obtener_datos("apuestas")
    df_v = obtener_datos("ventas")
    
    if not df_a.empty and 'usuario' in df_a.columns:
        df_a['puntos'] = df_a.apply(lambda x: calcular_puntos_futbol(x, df_p), axis=1)
        rank = df_a.groupby('usuario')['puntos'].sum().reset_index()
        
        # Resultado Real (Se actualiza cuando termine el evento)
        KPI_REAL = 101.60 
        
        if not df_v.empty and 'usuario' in df_v.columns:
            df_v['err'] = abs(df_v['apuesta_porcentaje'] - KPI_REAL).round(2)
            min_err = df_v['err'].min()
            df_v['pts_v'] = df_v['err'].apply(lambda x: 10 if x == min_err else 0)
            rank_v = df_v.groupby('usuario')['pts_v'].sum().reset_index()
            rank = pd.merge(rank, rank_v, on='usuario', how='outer').fillna(0)
            rank['Total'] = rank['puntos'] + rank['pts_v']
        else:
            rank['Total'] = rank['puntos']
            
        rank = rank.sort_values(by='Total', ascending=False)
        st.table(rank[['usuario', 'Total']].rename(columns={'usuario': 'Participante', 'Total': 'Puntos'}))
    else:
        st.info("Ranking disponible tras las primeras apuestas.")
