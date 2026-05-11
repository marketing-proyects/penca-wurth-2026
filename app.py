import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# --- ESTILOS CORPORATIVOS WÜRTH ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button { 
        background-color: #ED1C24; color: white; border-radius: 4px; 
        width: 100%; border: none; font-weight: bold;
    }
    .stButton>button:hover { background-color: #000000; color: white; }
    .stMetric { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #ED1C24; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA DE DATOS ---
def guardar_datos(df_nuevo, archivo):
    path = f'data/{archivo}'
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if os.path.exists(path):
        df_hist = pd.read_csv(path)
        df_final = pd.concat([df_hist, df_nuevo], ignore_index=True)
    else:
        df_final = df_nuevo
    
    df_final.to_csv(path, index=False)

def cargar_partidos():
    return pd.read_csv('data/partidos.csv')

# --- INTERFAZ PRINCIPAL ---
st.title("🏆 PENCA DIGITAL WÜRTH 2026")
st.subheader("Market Intelligence Unit - Uruguay")

tab1, tab2, tab3 = st.tabs(["⚽ PRONÓSTICOS", "📊 KPI VENTAS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS DE FÚTBOL ---
with tab1:
    st.header("Carga de Partidos")
    df_partidos = cargar_partidos()
    ahora = datetime.now()

    with st.form("penca_futbol"):
        usuario = st.text_input("Nombre / Legajo:", placeholder="Ej: Diego_W")
        st.divider()
        
        apuestas_temporales = []
        
        for idx, row in df_partidos.iterrows():
            col1, col_vs, col2 = st.columns([2, 1, 2])
            
            # Lógica de bloqueo (Ejemplo: 1 hora antes)
            fecha_str = f"{row['fecha']} {row['hora_uy']}"
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
            bloqueado = ahora >= fecha_dt 

            with col1:
                st.write(f"**{row['local']}**")
                g_l = st.number_input("Goles", 0, 20, 0, key=f"l_{row['id']}", disabled=bloqueado)
            
            with col_vs:
                st.markdown(f"<p style='text-align:center; font-size:20px;'>VS</p>", unsafe_allow_html=True)
                st.caption(f"{row['hora_uy']} hs")
            
            with col2:
                st.write(f"**{row['visitante']}**")
                g_v = st.number_input("Goles", 0, 20, 0, key=f"v_{row['id']}", disabled=bloqueado)
            
            apuestas_temporales.append({
                "usuario": usuario, "partido_id": row['id'], 
                "goles_local": g_l, "goles_visitante": g_v, 
                "timestamp": ahora.strftime("%Y-%m-%d %H:%M")
            })
            st.divider()

        btn_futbol = st.form_submit_button("GUARDAR PRONÓSTICOS")
        
        if btn_futbol:
            if usuario:
                df_apuestas = pd.DataFrame(apuestas_temporales)
                guardar_datos(df_apuestas, 'apuestas.csv')
                st.success(f"✅ Pronósticos de {usuario} guardados localmente.")
            else:
                st.error("⚠️ Por favor ingresa tu nombre.")

# --- TAB 2: KPI VENTAS (EL DÍA ESPECIAL) ---
with tab2:
    st.header("🎯 Desafío Especial de Ventas")
    st.write("KPI: Crecimiento de Pedidos por Vendedor (Junio 2026 vs 2025)")
    
    with st.form("penca_ventas"):
        user_v = st.text_input("Tu Nombre:", key="user_v")
        st.write("### ¿Cuál será el % de cumplimiento del día especial?")
        apuesta_val = st.number_input("Ingresa el porcentaje (ej: 101.60)", 
                                      min_value=0.00, max_value=300.00, 
                                      value=100.00, step=0.01, format="%.2f")
        
        btn_ventas = st.form_submit_button("REGISTRAR APUESTA DE VENTAS")
        
        if btn_ventas:
            if user_v:
                df_v = pd.DataFrame([{
                    "usuario": user_v, 
                    "apuesta_porcentaje": apuesta_val, 
                    "timestamp": ahora.strftime("%Y-%m-%d %H:%M")
                }])
                guardar_datos(df_v, 'ventas_kpi.csv')
                st.success(f"🎯 Apuesta de {apuesta_val}% registrada para {user_v}")
            else:
                st.error("⚠️ Ingresa tu nombre.")

# --- TAB 3: RANKING (VISUALIZACIÓN LOCAL) ---
with tab3:
    st.header("🥇 Posiciones en Tiempo Real")
    
    col_rank1, col_rank2 = st.columns(2)
    
    with col_rank1:
        st.subheader("Últimas Apuestas Fútbol")
        if os.path.exists('data/apuestas.csv'):
            st.dataframe(pd.read_csv('data/apuestas.csv').tail(10))
        else:
            st.info("No hay datos de fútbol aún.")

    with col_rank2:
        st.subheader("Apuestas de Ventas")
        if os.path.exists('data/ventas_kpi.csv'):
            st.dataframe(pd.read_csv('data/ventas_kpi.csv').tail(10))
        else:
            st.info("No hay datos de ventas aún.")
