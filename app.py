import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE EXTENDIDO (Basado en PDF y Ajuste UY) ---
def cargar_fixture():
    data = [
        # GRUPO A
        {"id": 1, "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 10, "grupo": "A", "e1": "México 🇲🇽", "e2": "Corea del Sur 🇰🇷", "fecha": "17/06", "hora": "22:00"},
        {"id": 11, "grupo": "A", "e1": "Sudáfrica 🇿🇦", "e2": "Rep. Checa 🇨🇿", "fecha": "17/06", "hora": "18:00"},
        # GRUPO B
        {"id": 3, "grupo": "B", "e1": "Canadá 🇨🇦", "e2": "Bosnia 🇧🇦", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "grupo": "B", "e1": "Qatar QA", "e2": "Suiza 🇨🇭", "fecha": "12/06", "hora": "20:00"},
        # GRUPO F (Uruguay)
        {"id": 9, "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia Saudita 走", "fecha": "15/06", "hora": "15:00"},
        {"id": 20, "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        {"id": 30, "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "España 🇪🇸", "fecha": "20/06", "hora": "21:00"},
    ]
    # Nota: Aquí se deben seguir agregando los 72 partidos de fase de grupos del PDF
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL "PASSION FOR SOCCER" ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    .logo-box { background-color: white; padding: 5px; border: 1px solid #f0f0f0; display: inline-block; margin-bottom: 20px; }
    h1, h2, h3 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    
    /* CABECERA DE GRUPO ESTILO TARJETA */
    .grupo-header-card {
        background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%);
        color: white;
        padding: 15px;
        border-radius: 8px 8px 0px 0px;
        font-weight: bold;
        font-size: 22px;
        margin-top: 30px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* FILA DE PARTIDO */
    .partido-row {
        background-color: white;
        padding: 15px;
        border-bottom: 1px solid #eee;
        transition: 0.3s;
    }
    .partido-row:hover { background-color: #fff9f9; }

    /* PESTAÑAS BLOQUEADAS */
    .locked-tab { color: #999 !important; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RENDER CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu_principal = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING"])

with menu_principal[0]:
    # PESTAÑAS DE FASES
    fases = st.tabs(["Fase de Grupos", "🔒 Octavos", "🔒 Cuartos", "🔒 Final"])
    
    with fases[0]:
        df_fixture = cargar_fixture()
        
        st.subheader("👤 Tu Identificación")
        c1, c2, c3 = st.columns([1,1,2])
        u_nom = c1.text_input("Nombre:").strip()
        u_ape = c2.text_input("Apellido:").strip()
        u_sec = c3.selectbox("Sector:", ["Ventas", "Logística", "Administración", "IT", "RRHH", "Dirección", "Otros"])

        if u_nom and u_ape:
            # Lógica de carga de apuestas (mismo que antes)
            try:
                df_apuestas = conn.read(worksheet="apuestas", ttl=0)
                df_u = df_apuestas[(df_apuestas['nombre'].str.lower() == u_nom.lower()) & (df_apuestas['apellido'].str.lower() == u_ape.lower())]
            except:
                df_apuestas, df_u = pd.DataFrame(), pd.DataFrame()

            # PESTAÑAS POR DÍA PARA ORDENAR EL FIXTURE
            st.markdown("### Selecciona el día para apostar:")
            dias = sorted(df_fixture['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            tabs_dias = st.tabs([f"📅 {d}" for d in dias])

            with st.form("penca_form_v2"):
                for i, dia in enumerate(dias):
                    with tabs_dias[i]:
                        partidos_dia = df_fixture[df_fixture['fecha'] == dia]
                        
                        for _, row in partidos_dia.iterrows():
                            # Header de Grupo llamativo
                            st.markdown(f'''
                                <div class="grupo-header-card">
                                    <span>GRUPO {row['grupo']}</span>
                                    <span style="font-size: 14px; opacity: 0.8;">{row['fecha']} - {row['hora']} hs</span>
                                </div>
                            ''', unsafe_allow_html=True)
                            
                            # Cargar valores previos
                            v1, v2 = 0, 0
                            if not df_u.empty:
                                prev = df_u[df_u['partido_id'] == row['id']]
                                if not prev.empty:
                                    v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])

                            # Fila de apuesta
                            col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                            with col_p:
                                st.markdown(f"<div style='padding-top:20px; font-size:18px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                            with col_g1:
                                st.number_input(f"Goles {row['e1']}", 0, 20, v1, key=f"e1_{row['id']}")
                            with col_g2:
                                st.number_input(f"Goles {row['e2']}", 0, 20, v2, key=f"e2_{row['id']}")
                
                st.divider()
                st.markdown("### 🃏 COMODÍN DE VENTAS JUNIO")
                # Lógica del comodín (ID 999) igual que antes...
                u_com = st.number_input("Cumplimiento estimado (%)", 0.0, 200.0, 100.0, step=0.1, key="comodin_val")

                if st.form_submit_button("💾 GUARDAR PRONÓSTICOS DEL DÍA"):
                    # Lógica de guardado...
                    st.success("¡Datos guardados con éxito!")

    with fases[1]:
        st.markdown("<h3 class='locked-tab'>🔒 Octavos de Final</h3>", unsafe_allow_html=True)
        st.info("Esta sección se habilitará cuando se definan los clasificados de la Fase de Grupos.")

# --- TAB 2: TABLAS (Auto-calculadas) ---
with menu_principal[1]:
    st.subheader("📊 Posiciones Reales")
    # Motor de tablas automáticas (basado en lo que llenas en Drive)
