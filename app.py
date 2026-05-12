import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

def init_db():
    conn = sqlite3.connect('penca.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apuestas 
                 (wn TEXT, nombre TEXT, apellido TEXT, sector TEXT, partido_id INTEGER, 
                  g1 INTEGER, g2 INTEGER, fecha_reg TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. FIXTURE (Estructura Total) ---
def cargar_fixture():
    data = [
        # GRUPOS (Ejemplo de carga según PDF)
        {"id": 1, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "fase": "Grupos", "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 9, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia S. 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 10, "fase": "Grupos", "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        {"id": 30, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "España 🇪🇸", "fecha": "20/06", "hora": "21:00"},
    ]
    # Fases Finales
    eliminatorias = [
        {"id": 101, "fase": "Octavos", "grupo": "Elim.", "e1": "1º Grupo A", "e2": "2º Grupo B", "fecha": "28/06", "hora": "15:00"},
        {"id": 201, "fase": "Cuartos", "grupo": "Elim.", "e1": "Ganador 101", "e2": "Ganador 102", "fecha": "04/07", "hora": "17:00"},
        {"id": 301, "fase": "Final", "grupo": "Final", "e1": "Finalista 1", "e2": "Finalista 2", "fecha": "19/07", "hora": "19:00"},
    ]
    return pd.DataFrame(data + eliminatorias)

# --- 3. DIÁLOGO EMERGENTE (COMODÍN) ---
@st.dialog("🃏 COMODÍN DE VENTAS JUNIO")
def modal_comodin(v_actual):
    st.markdown("##### ¿Qué porcentaje de cumplimiento alcanzará Würth Uruguay este mes?")
    val = st.number_input("Tu apuesta (%):", 0.0, 200.0, v_actual, step=0.1)
    st.caption("Recuerda: 50 pts al exacto | 10 pts al Top 10 más cercano.")
    if st.button("Confirmar Apuesta"):
        st.session_state.comodin_temp = val
        st.rerun()

# --- 4. ESTILO VISUAL ---
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
    h1 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; }
    .grupo-header-card {
        background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%);
        color: white; padding: 12px; border-radius: 8px 8px 0px 0px;
        font-weight: bold; font-size: 18px; margin-top: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .info-comodin-card {
        background: white; border-left: 5px solid #ED1C24; padding: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
if os.path.exists("logo_wurth.jpg"):
    st.image("logo_wurth.jpg", width=180)
else:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING", "🔒 ADMIN"])

# --- TAB 1: PRONÓSTICOS ---
with menu[0]:
    df_fixture = cargar_fixture()
    st.subheader("👤 Registro de Colaborador")
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom = c1.text_input("Nombre:").strip()
    u_ape = c2.text_input("Apellido:").strip()
    u_wn = c3.text_input("Código WN:").strip().upper()
    u_sec = c4.selectbox("Sector:", ["Ventas", "Marketing", "Logística", "IT", "Administración", "RRHH", "Otros"])

    if u_nom and u_ape and u_wn:
        # Recuperar datos
        db_conn = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db_conn)
        db_conn.close()

        # Lógica de Pop-up Comodín
        v_com_registrado = 0.0
        if not df_u.empty:
            p_com = df_u[df_u['partido_id'] == 999]
            if not p_com.empty: v_com_registrado = float(p_com.iloc[0]['g1'])
        
        if 'comodin_temp' not in st.session_state and v_com_registrado == 0.0:
            modal_comodin(0.0)
        
        cur_com = st.session_state.get('comodin_temp', v_com_registrado)
        st.markdown(f'<div class="info-comodin-card"><b>🃏 Comodín Ventas:</b> Tu pronóstico es del <b>{cur_com}%</b>.</div>', unsafe_allow_html=True)

        f_tabs = st.tabs(["Fase de Grupos", "Octavos", "Cuartos", "Final"])
        
        # --- SUB-TAB: GRUPOS ---
        with f_tabs[0]:
            df_g = df_fixture[df_fixture['fase'] == "Grupos"]
            dias = sorted(df_g['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            tabs_dias = st.tabs([f"📅 {d}" for d in dias])

            with st.form("penca_sqlite_v2"):
                for i, dia in enumerate(dias):
                    with tabs_dias[i]:
                        partidos_dia = df_g[df_g['fecha'] == dia]
                        for _, row in partidos_dia.iterrows():
                            # Verificar si este partido específico está lleno
                            v1, v2, partido_lleno = 0, 0, False
                            if not df_u.empty:
                                prev = df_u[df_u['partido_id'] == row['id']]
                                if not prev.empty:
                                    v1, v2 = int(prev.iloc[0]['g1']), int(prev.iloc[0]['g2'])
                                    partido_lleno = True

                            # Encabezado: Solo muestra ✅ si el partido está guardado
                            st.markdown(f'''
                                <div class="grupo-header-card">
                                    <span>GRUPO {row["grupo"]} {"✅" if partido_lleno else ""}</span>
                                    <span style="font-size: 13px; opacity: 0.8;">{row["hora"]} hs</span>
                                </div>''', unsafe_allow_html=True)
                            
                            cp, cg1, cg2 = st.columns([4, 1, 1])
                            cp.markdown(f"<div style='padding-top:20px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                            st.session_state[f"g1_{row['id']}"] = cg1.number_input("L", 0, 20, v1, key=f"in_g1_{row['id']}")
                            st.session_state[f"g2_{row['id']}"] = cg2.number_input("V", 0, 20, v2, key=f"in_e2_{row['id']}")

                if st.form_submit_button("💾 GUARDAR PRONÓSTICOS"):
                    db_conn = sqlite3.connect('penca.db')
                    c = db_conn.cursor()
                    c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}'")
                    # Guardar partidos
                    for _, row in df_fixture[df_fixture['fase'] == "Grupos"].iterrows():
                        g1 = st.session_state.get(f"g1_{row['id']}", 0)
                        g2 = st.session_state.get(f"g2_{row['id']}", 0)
                        c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                                 (u_wn, u_nom, u_ape, u_sec, row['id'], g1, g2, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    # Guardar comodín
                    c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                             (u_wn, u_nom, u_ape, u_sec, 999, cur_com, 0, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    db_conn.commit()
                    db_conn.close()
                    st.success("¡Datos guardados!")
                    st.rerun()

        # --- SUB-TABS: ELIMINATORIAS (Placeholder visual) ---
        with f_tabs[1]:
            st.info("⚽ **Octavos de Final:** Los cruces se habilitarán automáticamente cuando finalice la fase de grupos el 27 de Junio.")
        with f_tabs[2]:
            st.info("⚽ **Cuartos de Final:** Próximamente.")
        with f_tabs[3]:
            st.info("⚽ **Gran Final:** 19 de Julio - Estadio MetLife.")

# --- TAB: ADMIN ---
with menu[3]:
    st.subheader("🔒 Panel de Administración")
    clave = st.text_input("Contraseña:", type="password")
    if clave == "wurth2026":
        db_conn = sqlite3.connect('penca.db')
        df_admin = pd.read_sql("SELECT * FROM apuestas", db_conn)
        db_conn.close()
        if not df_admin.empty:
            csv = df_admin.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Base de Datos (CSV)", csv, "penca_final.csv", "text/csv")
            st.dataframe(df_admin)
