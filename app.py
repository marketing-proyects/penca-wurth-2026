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

# --- 2. FIXTURE COMPLETO (Basado en PDF - Grupos A al L) ---
def cargar_fixture():
    data = [
        # GRUPO A
        {"id": 1, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "fase": "Grupos", "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 13, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Corea del Sur 🇰🇷", "fecha": "17/06", "hora": "22:00"},
        {"id": 14, "fase": "Grupos", "grupo": "A", "e1": "Rep. Checa 🇨🇿", "e2": "Sudáfrica 🇿🇦", "fecha": "17/06", "hora": "18:00"},
        # GRUPO B
        {"id": 3, "fase": "Grupos", "grupo": "B", "e1": "Canadá 🇨🇦", "e2": "Bosnia 🇧🇦", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "fase": "Grupos", "grupo": "B", "e1": "Qatar 🇶🇦", "e2": "Suiza 🇨🇭", "fecha": "12/06", "hora": "20:00"},
        # GRUPO C
        {"id": 5, "fase": "Grupos", "grupo": "C", "e1": "Brasil 🇧🇷", "e2": "Haití 🇭🇹", "fecha": "13/06", "hora": "14:00"},
        {"id": 6, "fase": "Grupos", "grupo": "C", "e1": "Marruecos 🇲🇦", "e2": "Escocia 🏴󠁧󠁢󠁳󠁣󠁴󠁿", "fecha": "13/06", "hora": "19:00"},
        # GRUPO D
        {"id": 7, "fase": "Grupos", "grupo": "D", "e1": "EE. UU. 🇺🇸", "e2": "Turquía 🇹🇷", "fecha": "14/06", "hora": "17:00"},
        {"id": 8, "fase": "Grupos", "grupo": "D", "e1": "Australia 🇦🇺", "e2": "Paraguay 🇵🇾", "fecha": "14/06", "hora": "21:00"},
        # GRUPO F (Uruguay)
        {"id": 9, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia S. 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 10, "fase": "Grupos", "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        {"id": 30, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "España 🇪🇸", "fecha": "20/06", "hora": "21:00"},
        # Se pueden seguir agregando partidos hasta completar los 72 de grupos del PDF
    ]
    eliminatorias = [
        {"id": 101, "fase": "Octavos", "grupo": "Elim.", "e1": "1º Grupo A", "e2": "2º Grupo B", "fecha": "28/06", "hora": "15:00"},
        {"id": 201, "fase": "Cuartos", "grupo": "Elim.", "e1": "Ganador 101", "e2": "Ganador 102", "fecha": "04/07", "hora": "17:00"},
        {"id": 301, "fase": "Final", "grupo": "Final", "e1": "Finalista 1", "e2": "Finalista 2", "fecha": "19/07", "hora": "19:00"},
    ]
    return pd.DataFrame(data + eliminatorias)

# --- 3. DIÁLOGO COMODÍN ---
@st.dialog("🃏 COMODÍN DE VENTAS JUNIO")
def modal_comodin(v_actual):
    st.markdown("##### ¿Qué porcentaje de cumplimiento alcanzará Würth Uruguay este mes?")
    val = st.number_input("Tu apuesta (%):", 0.0, 200.0, v_actual, step=0.1)
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
        font-weight: bold; font-size: 16px; margin-top: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .status-text { font-size: 12px; color: #28a745; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
logo_path = "logo_wurth.jpg"
if os.path.exists(logo_path):
    st.image(logo_path, width=180)
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
        db_conn = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db_conn)
        db_conn.close()

        # Pop-up Comodín
        v_com_registrado = 0.0
        if not df_u.empty:
            p_com = df_u[df_u['partido_id'] == 999]
            if not p_com.empty: v_com_registrado = float(p_com.iloc[0]['g1'])
        
        if 'comodin_temp' not in st.session_state and v_com_registrado == 0.0:
            modal_comodin(0.0)
        
        cur_com = st.session_state.get('comodin_temp', v_com_registrado)
        st.info(f"🃏 **Comodín Ventas:** {cur_com}%")

        f_tabs = st.tabs(["Fase de Grupos", "Octavos", "Cuartos", "Final"])
        
        with f_tabs[0]:
            df_g = df_fixture[df_fixture['fase'] == "Grupos"]
            dias = sorted(df_g['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            tabs_dias = st.tabs([f"📅 {d}" for d in dias])

            with st.form("penca_sqlite_v3"):
                for i, dia in enumerate(dias):
                    with tabs_dias[i]:
                        partidos_dia = df_g[df_g['fecha'] == dia]
                        for _, row in partidos_dia.iterrows():
                            # Lógica de Tick INDIVIDUAL corregida
                            partido_guardado = False
                            v1, v2 = 0, 0
                            if not df_u.empty:
                                prev = df_u[df_u['partido_id'] == row['id']]
                                if not prev.empty:
                                    v1, v2 = int(prev.iloc[0]['g1']), int(prev.iloc[0]['g2'])
                                    partido_guardado = True

                            check_ui = " ✅" if partido_guardado else ""
                            status_ui = '<span class="status-text">Resultado ingresado</span>' if partido_guardado else ""

                            st.markdown(f'''
                                <div class="grupo-header-card">
                                    <span>GRUPO {row["grupo"]}{check_ui}</span>
                                    {status_ui}
                                </div>''', unsafe_allow_html=True)
                            
                            cp, cg1, cg2 = st.columns([4, 1, 1])
                            cp.markdown(f"<div style='padding-top:20px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                            st.session_state[f"g1_{row['id']}"] = cg1.number_input("L", 0, 20, v1, key=f"in_g1_{row['id']}")
                            st.session_state[f"g2_{row['id']}"] = cg2.number_input("V", 0, 20, v2, key=f"in_e2_{row['id']}")

                if st.form_submit_button("💾 GUARDAR PRONÓSTICOS"):
                    db_conn = sqlite3.connect('penca.db')
                    c = db_conn.cursor()
                    c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}'")
                    for _, row in df_fixture[df_fixture['fase'] == "Grupos"].iterrows():
                        g1 = st.session_state.get(f"g1_{row['id']}", 0)
                        g2 = st.session_state.get(f"g2_{row['id']}", 0)
                        c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                                 (u_wn, u_nom, u_ape, u_sec, row['id'], g1, g2, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                             (u_wn, u_nom, u_ape, u_sec, 999, cur_com, 0, datetime.now().strftime("%Y-%m-%d %H:%M")))
                    db_conn.commit()
                    db_conn.close()
                    st.success("¡Datos guardados!")
                    st.rerun()

# --- TAB 4: ADMIN ---
with menu[3]:
    st.subheader("🔒 Panel de Administración")
    with st.form("admin_login"):
        clave = st.text_input("Ingrese la Contraseña:", type="password")
        btn_login = st.form_submit_button("Acceder al Panel")
        
    if btn_login:
        if clave == "market1NG?":
            st.session_state.admin_auth = True
        else:
            st.error("Contraseña incorrecta")

    if st.session_state.get("admin_auth"):
        st.success("Acceso Concedido")
        db_conn = sqlite3.connect('penca.db')
        df_admin = pd.read_sql("SELECT * FROM apuestas", db_conn)
        db_conn.close()
        
        if not df_admin.empty:
            csv = df_admin.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Base de Datos (CSV)", csv, "penca_würth_2026.csv", "text/csv")
            st.dataframe(df_admin)
        else:
            st.info("No hay datos registrados aún.")
