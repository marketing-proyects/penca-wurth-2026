import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE (Resumen para la prueba) ---
def cargar_fixture():
    data = [
        {"id": 1, "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 9, "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia Saudita 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 30, "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "España 🇪🇸", "fecha": "20/06", "hora": "21:00"},
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (Corrección de Logo y Estética) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    
    /* CORRECCIÓN LOGO: Forzar cuadrado */
    [data-testid="stImage"] img {
        border-radius: 0px !important;
        box-shadow: none !important;
    }
    
    .logo-box { background-color: white; padding: 10px; display: inline-block; margin-bottom: 20px; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    .grupo-header-card {
        background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%);
        color: white; padding: 15px; border-radius: 8px 8px 0px 0px;
        font-weight: bold; font-size: 20px; margin-top: 30px;
        display: flex; align-items: center; justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RENDER CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
# Se aplica el logo asegurando que no tenga bordes redondeados
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING"])

with menu[0]:
    fases = st.tabs(["Fase de Grupos", "🔒 Octavos", "🔒 Cuartos", "🔒 Final"])
    
    with fases[0]:
        df_fixture = cargar_fixture()
        
        st.subheader("👤 Registro de Colaborador")
        col_reg1, col_reg2, col_reg3 = st.columns([1,1,1])
        u_nom = col_reg1.text_input("Nombre:").strip()
        u_ape = col_reg2.text_input("Apellido:").strip()
        u_wn = col_reg3.text_input("Código WN (Alfanumérico):").strip().upper() # Nuevo campo WN
        
        c_sec = st.selectbox("Sector:", ["RRHH", "Finanzas", "Créditos", "Compras", "IT", "Marketing", "Dirección", "CEO", "Logística", "Tiendas", "Telentas", "e-Commerce", "Ventas", "Otra"])

        if u_nom and u_ape and u_wn:
            try:
                df_apuestas = conn.read(worksheet="apuestas", ttl=0)
                df_u = df_apuestas[(df_apuestas['wn'] == u_wn)] # Buscamos ahora por el código único WN
            except:
                df_apuestas, df_u = pd.DataFrame(), pd.DataFrame()

            st.markdown("### Selecciona el día:")
            dias = sorted(df_fixture['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            tabs_dias = st.tabs([f"📅 {d}" for d in dias])

            with st.form("penca_form_wn"):
                for i, dia in enumerate(dias):
                    with tabs_dias[i]:
                        partidos_dia = df_fixture[df_fixture['fecha'] == dia]
                        for _, row in partidos_dia.iterrows():
                            st.markdown(f'<div class="grupo-header-card"><span>GRUPO {row["grupo"]}</span><span style="font-size: 14px; opacity: 0.8;">{row["fecha"]} - {row["hora"]} hs</span></div>', unsafe_allow_html=True)
                            
                            v1, v2 = 0, 0
                            if not df_u.empty:
                                prev = df_u[df_u['partido_id'] == row['id']]
                                if not prev.empty:
                                    v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])

                            col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                            with col_p:
                                st.markdown(f"<div style='padding-top:20px; font-size:18px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                            with col_g1:
                                st.number_input(f"Goles {row['e1']}", 0, 20, v1, key=f"e1_{row['id']}")
                            with col_g2:
                                st.number_input(f"Goles {row['e2']}", 0, 20, v2, key=f"e2_{row['id']}")
                
                st.divider()
                st.markdown("### 🃏 COMODÍN DE VENTAS JUNIO")
                u_com = st.number_input("Cumplimiento estimado (%)", 0.0, 200.0, 100.0, step=0.1, key="comodin_val")

                if st.form_submit_button("💾 GUARDAR PRONÓSTICOS"):
                    nuevas = []
                    for _, row in df_fixture.iterrows():
                        nuevas.append({
                            "nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": c_sec, 
                            "partido_id": row['id'], 
                            "goles_equipo_1": st.session_state[f"e1_{row['id']}"], 
                            "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                    # Guardado del comodín
                    nuevas.append({"nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": c_sec, "partido_id": 999, "goles_equipo_1": u_com, "goles_equipo_2": 0, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    
                    # Limpiamos registros previos del mismo WN para no duplicar
                    df_limpio = df_apuestas[df_apuestas['wn'] != u_wn] if not df_apuestas.empty else pd.DataFrame()
                    df_final = pd.concat([df_limpio, pd.DataFrame(nuevas)], ignore_index=True)
                    conn.update(worksheet="apuestas", data=df_final)
                    st.success(f"¡Pronósticos guardados para el colaborador {u_wn}!")
