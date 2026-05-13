import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import requests
from io import BytesIO

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "comodin_temp" not in st.session_state:
    st.session_state.comodin_temp = None

# URL DE DESCARGA DIRECTA DE GITHUB
URL_RESULTADOS_REALES = "https://github.com/marketing-proyects/penca-wurth-2026/raw/5ea13ebda06c41af8cdf217dbe63d396b9ba4bb4/Maestro_Resultados_Penca_Wurth_2026_Final.xlsx"

def init_db():
    conn = sqlite3.connect('penca.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS apuestas 
                 (wn TEXT, nombre TEXT, apellido TEXT, sector TEXT, partido_id INTEGER, 
                  g1 INTEGER, g2 INTEGER, fecha_reg TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. FIXTURE MAESTRO (104 Partidos) ---
def cargar_fixture():
    groups_data = {
        "A": ["Mexico", "Sudafrica", "Corea del Sur", "Rep. Checa"],
        "B": ["Canada", "Bosnia", "Qatar", "Suiza"],
        "C": ["Brasil", "Haiti", "Marruecos", "Escocia"],
        "D": ["EE. UU.", "Turquia", "Australia", "Paraguay"],
        "E": ["Alemania", "Curazao", "C. Marfil", "Ecuador"],
        "F": ["P. Bajos", "Japon", "Suecia", "Tunez"],
        "G": ["Belgica", "Egipto", "Iran", "N. Zelanda"],
        "H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
        "I": ["Francia", "Senegal", "Irak", "Noruega"],
        "J": ["Austria", "Jordania", "Argentina", "Argelia"],
        "K": ["Portugal", "RD Congo", "Uzbekistan", "Colombia"],
        "L": ["Inglaterra", "Croacia", "Ghana", "Panama"]
    }
    matches = []
    match_id = 1
    for group_name, teams in groups_data.items():
        dates = ["11/06", "11/06", "17/06", "17/06", "22/06", "22/06"]
        if group_name in ["D", "E", "F"]: dates = ["14/06", "15/06", "19/06", "20/06", "24/06", "25/06"]
        if group_name in ["G", "H", "I"]: dates = ["16/06", "17/06", "21/06", "22/06", "26/06", "27/06"]
        if group_name in ["J", "K", "L"]: dates = ["18/06", "19/06", "24/06", "25/06", "28/06", "29/06"]
        pairs = [(teams[0], teams[1]), (teams[2], teams[3]), (teams[0], teams[2]), (teams[1], teams[3]), (teams[3], teams[0]), (teams[1], teams[2])]
        for i, pair in enumerate(pairs):
            matches.append({"id": match_id, "fase": "Grupos", "grupo": group_name, "e1": pair[0], "e2": pair[1], "fecha": dates[i], "hora": "18:00" if i%2==0 else "22:00"})
            match_id += 1
    fases = [("Ronda de 32", 16), ("Octavos", 8), ("Cuartos", 4), ("Semis", 2), ("Tercer Puesto", 1), ("Gran Final", 1)]
    for f_nom, cant in fases:
        for _ in range(cant):
            matches.append({"id": match_id, "fase": f_nom, "grupo": "Eliminatoria", "e1": f"Clasificado {match_id}A", "e2": f"Clasificado {match_id}B", "fecha": "Julio", "hora": "20:00"})
            match_id += 1
    return pd.DataFrame(matches)

# --- 3. DIÁLOGO COMODÍN ---
@st.dialog("🃏 COMODÍN DE VENTAS JUNIO")
def modal_comodin(v_actual):
    st.markdown("##### ¿Qué porcentaje de cumplimiento alcanzará Würth Uruguay este mes?")
    val = st.number_input("Tu apuesta (%):", 0.0, 200.0, v_actual, step=0.1)
    st.info("💡 **Lógica:** 50 pts al exacto | 10 pts al Top 10 más cercano.")
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
    [data-testid="stImage"] > img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 10px; display: inline-block; margin-bottom: 20px; border: 1px solid #eee; }
    .grupo-header-card { background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%); color: white; padding: 12px; border-radius: 8px 8px 0px 0px; font-weight: bold; display: flex; justify-content: space-between; }
    .info-card { background: white; border-left: 5px solid #ED1C24; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .grupo-tabla-card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING", "🔒 ADMIN"])

# --- TAB 1: PRONÓSTICOS ---
with menu[0]:
    st.markdown('<div class="info-card"><b>🏆 PUNTOS:</b> 3 pts Exacto | 1 pt Ganador.<br><b>🃏 COMODÍN:</b> 50 pts al exacto | 10 pts al Top 10.</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom, u_ape, u_wn = c1.text_input("Nombre:").strip(), c2.text_input("Apellido:").strip(), c3.text_input("WN:").strip().upper()
    u_sec = c4.selectbox("Sector:", ["Finanzas", "Compras", "Créditos", "RRHH", "IT", "Dirección", "Logistica", "Televentas", "Tiendas", "e-Commerce", "Ventas", "Marketing", "Sales Operation", "Otro"], index=None)

    if all([u_nom, u_ape, u_wn, u_sec]):
        db_conn = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db_conn)
        db_conn.close()

        v_com = float(df_u[df_u['partido_id'] == 999].iloc[0]['g1']) if 999 in df_u['partido_id'].values else 0.0
        if st.session_state.comodin_temp is None and v_com == 0.0: modal_comodin(0.0)
        cur_com = st.session_state.comodin_temp if st.session_state.comodin_temp is not None else v_com
        st.markdown(f'<div class="info-card"><b>🃏 Tu Comodín: {cur_com}%</b></div>', unsafe_allow_html=True)

        f_tabs = st.tabs(["Fase de Grupos", "Fase Eliminatoria"])
        with f_tabs[0]:
            df_fixture = cargar_fixture()
            df_g = df_fixture[df_fixture['fase'] == "Grupos"]
            dias = sorted(df_g['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            t_dias = st.tabs([f"📅 {d}" for d in dias])
            for i, dia in enumerate(dias):
                with t_dias[i]:
                    with st.form(key=f"form_{dia}"):
                        p_dia = df_g[df_g['fecha'] == dia]
                        for _, row in p_dia.iterrows():
                            v1, v2, ok = 0, 0, False
                            if row['id'] in df_u['partido_id'].values:
                                reg = df_u[df_u['partido_id'] == row['id']].iloc[0]
                                v1, v2, ok = int(reg['g1']), int(reg['g2']), True
                            st.markdown(f'<div class="grupo-header-card"><span>GRUPO {row["grupo"]}{" ✅" if ok else ""}</span><span>{row["hora"]} hs</span></div>', unsafe_allow_html=True)
                            cp, cg1, cg2 = st.columns([4, 1, 1])
                            cp.markdown(f"<br><b>{row['e1']}</b> vs <b>{row['e2']}</b>", unsafe_allow_html=True)
                            st.session_state[f"n1_{row['id']}"] = cg1.number_input("L", 0, 20, v1, key=f"v1_{row['id']}")
                            st.session_state[f"n2_{row['id']}"] = cg2.number_input("V", 0, 20, v2, key=f"v2_{row['id']}")
                        if st.form_submit_button("💾 Guardar Día"):
                            db_conn = sqlite3.connect('penca.db'); c = db_conn.cursor()
                            c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}' AND partido_id IN ({','.join(map(str, p_dia['id']))})")
                            for pid in p_dia['id']:
                                c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", (u_wn, u_nom, u_ape, u_sec, pid, st.session_state[f"v1_{pid}"], st.session_state[f"v2_{pid}"], datetime.now().strftime("%Y-%m-%d %H:%M")))
                            c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}' AND partido_id=999")
                            c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", (u_wn, u_nom, u_ape, u_sec, 999, cur_com, 0, ""))
                            db_conn.commit(); db_conn.close(); st.rerun()
        with f_tabs[1]: st.info("⚽ Se habilita al terminar la fase de grupos.")

# --- TAB 2: TABLAS ---
with menu[1]:
    st.subheader("📊 Composición de Grupos")
    df_fix = cargar_fixture()
    grupos = sorted(df_fix[df_fix['fase']=='Grupos']['grupo'].unique())
    cols = st.columns(3)
    for i, g in enumerate(grupos):
        with cols[i % 3]:
            st.markdown(f'<div class="grupo-tabla-card"><div style="background:#ED1C24;color:white;text-align:center;font-weight:bold;padding:5px;border-radius:4px;margin-bottom:10px;">GRUPO {g}</div>', unsafe_allow_html=True)
            eqs = pd.concat([df_fix[df_fix['grupo']==g]['e1'], df_fix[df_fix['grupo']==g]['e2']]).unique()
            for e in eqs: st.write(f"⚽ {e}")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: RANKING ---
with menu[2]:
    st.subheader("🥇 Tabla de Posiciones")
    try:
        resp = requests.get(URL_RESULTADOS_REALES)
        xl = pd.read_excel(BytesIO(resp.content), sheet_name=None)
        df_real = pd.concat([xl['Fase de Grupos'], xl['Fase Eliminatoria']])
        db_conn = sqlite3.connect('penca.db'); df_ap = pd.read_sql("SELECT * FROM apuestas", db_conn); db_conn.close()
        if not df_ap.empty:
            merged = df_ap.merge(df_real[['partido_id', 'G1 Real', 'G2 Real']], on='partido_id')
            def calc(r):
                if pd.isna(r['G1 Real']): return 0
                if r['g1']==r['G1 Real'] and r['g2']==r['G2 Real']: return 3
                if (r['g1']>r['g2'] and r['G1 Real']>r['G2 Real']) or (r['g1']<r['g2'] and r['G1 Real']<r['G2 Real']) or (r['g1']==r['g2'] and r['G1 Real']==r['G2 Real']): return 1
                return 0
            merged['pts'] = merged.apply(calc, axis=1)
            rank = merged.groupby(['wn', 'nombre', 'apellido', 'sector'])['pts'].sum().reset_index().sort_values('pts', ascending=False)
            st.dataframe(rank, use_container_width=True)
        else: st.info("Esperando apuestas...")
    except: st.warning("Cargando resultados de GitHub...")

# --- TAB 4: ADMIN ---
with menu[3]:
    if not st.session_state.admin_logged:
        with st.form("admin_login"):
            pw = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Acceder"):
                # Busca exactamente admin_password en tus Secrets
                if "admin_password" in st.secrets and pw == st.secrets["admin_password"]:
                    st.session_state.admin_logged = True
                    st.rerun()
                else: st.error("Error: Revisa que el Secret sea 'admin_password' y la clave sea correcta.")
    else:
        if st.button("Cerrar Sesión"): st.session_state.admin_logged = False; st.rerun()
        db_conn = sqlite3.connect('penca.db'); df_ad = pd.read_sql("SELECT * FROM apuestas", db_conn); db_conn.close()
        st.download_button("📥 Descargar CSV", df_ad.to_csv(index=False), "penca_export.csv", "text/csv")
        st.dataframe(df_ad)
