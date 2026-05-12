import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# URL del archivo proporcionada
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/10ggCVluq5S4w2lvQdtYVedb6y7SzJ9SGaNMCBQC0co4/edit?usp=sharing"

# --- 2. FIXTURE COMPLETO ---
def cargar_fixture():
    data = [
        # GRUPO A
        {"id": 1, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "fase": "Grupos", "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        # GRUPO F (Uruguay)
        {"id": 9, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia S. 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 10, "fase": "Grupos", "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        {"id": 30, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "España 🇪🇸", "fecha": "20/06", "hora": "21:00"},
        # ELIMINATORIAS (Estructura para habilitar tabs)
        {"id": 101, "fase": "Octavos", "grupo": "Octavos", "e1": "1° Grupo A", "e2": "2° Grupo B", "fecha": "28/06", "hora": "15:00"},
        {"id": 201, "fase": "Cuartos", "grupo": "Cuartos", "e1": "Ganador 101", "e2": "Ganador 102", "fecha": "04/07", "hora": "17:00"},
        {"id": 301, "fase": "Semis", "grupo": "Semis", "e1": "Ganador 201", "e2": "Ganador 202", "fecha": "14/07", "hora": "21:00"},
        {"id": 401, "fase": "Final", "grupo": "Final", "e1": "Finalista 1", "e2": "Finalista 2", "fecha": "19/07", "hora": "19:00"},
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (Würth Style) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 10px; display: inline-block; margin-bottom: 20px; border: 1px solid #eee; }
    h1, h2 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; }
    .grupo-header-card {
        background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%);
        color: white; padding: 12px; border-radius: 8px 8px 0px 0px;
        font-weight: bold; font-size: 18px; margin-top: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LÓGICA PRINCIPAL ---
df_fixture = cargar_fixture()

st.subheader("👤 Registro")
c1, c2, c3, c4 = st.columns([1,1,1,2])
u_nom = c1.text_input("Nombre:").strip()
u_ape = c2.text_input("Apellido:").strip()
u_wn = c3.text_input("Código WN:").strip().upper()
u_sec = c4.selectbox("Sector:", ["Ventas", "Logística", "IT", "Marketing", "Administración", "Otros"])

if u_nom and u_ape and u_wn:
    try:
        # Intento de lectura con URL directa para forzar conexión
        df_apuestas_total = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="apuestas", ttl=0)
        df_apuestas_total['wn'] = df_apuestas_total['wn'].astype(str).str.strip().str.upper()
        df_u = df_apuestas_total[df_apuestas_total['wn'] == u_wn]
    except:
        df_apuestas_total, df_u = pd.DataFrame(), pd.DataFrame()

    # TABS DE FASES (Como pediste, separadas)
    fases = ["Grupos", "Octavos", "Cuartos", "Semis", "Final"]
    tab_fases = st.tabs([f"⚽ {f}" for f in fases])

    with st.form("penca_form_v2"):
        for idx, fase in enumerate(fases):
            with tab_fases[idx]:
                df_fase = df_fixture[df_fixture['fase'] == fase]
                
                if fase == "Grupos":
                    dias = sorted(df_fase['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
                    tab_dias = st.tabs([f"📅 {d}" for d in dias])
                    for d_idx, dia in enumerate(dias):
                        with tab_dias[d_idx]:
                            partidos = df_fase[df_fase['fecha'] == dia]
                            for _, row in partidos.iterrows():
                                # Valores previos
                                v1, v2 = 0, 0
                                if not df_u.empty:
                                    prev = df_u[df_u['partido_id'] == row['id']]
                                    if not prev.empty:
                                        v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])
                                
                                st.markdown(f'<div class="grupo-header-card">GRUPO {row["grupo"]} - {row["hora"]}hs</div>', unsafe_allow_html=True)
                                col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                                col_p.markdown(f"<div style='padding-top:20px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                                st.session_state[f"e1_{row['id']}"] = col_g1.number_input("L", 0, 20, v1, key=f"in_e1_{row['id']}")
                                st.session_state[f"e2_{row['id']}"] = col_g2.number_input("V", 0, 20, v2, key=f"in_e2_{row['id']}")
                else:
                    st.info(f"Los cruces de {fase} se habilitarán al finalizar la fase anterior.")

        if st.form_submit_button("💾 GUARDAR PRONÓSTICOS"):
            # Recolección de datos
            nuevas = []
            for _, row in df_fixture.iterrows():
                val1 = st.session_state.get(f"e1_{row['id']}", 0)
                val2 = st.session_state.get(f"e2_{row['id']}", 0)
                nuevas.append({
                    "nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": u_sec,
                    "partido_id": row['id'], "goles_equipo_1": val1, "goles_equipo_2": val2,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            
            # Consolidar (otros usuarios + este usuario actualizado)
            df_otros = df_apuestas_total[df_apuestas_total['wn'] != u_wn] if not df_apuestas_total.empty else pd.DataFrame()
            df_final = pd.concat([df_otros, pd.DataFrame(nuevas)], ignore_index=True)
            
            # ELIMINAR CUALQUIER FORMATO Y ESCRIBIR
            try:
                # Usamos la URL directa para asegurar que apunte al archivo correcto
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="apuestas", data=df_final)
                st.success("¡Datos guardados con éxito en Drive!")
                st.rerun()
            except Exception as e:
                st.error(f"Error de conexión: {e}")
                st.info("Asegúrate de que la hoja 'apuestas' no tenga filtros activos en el Drive.")
