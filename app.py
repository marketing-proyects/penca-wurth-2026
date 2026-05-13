import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

# Estados de sesión
if "admin_logged" not in st.session_state: st.session_state.admin_logged = False
if "comodin_temp" not in st.session_state: st.session_state.comodin_temp = None

# URL RAW DE GITHUB (Resultados Reales)
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

# --- 2. FIXTURE COMPLETO (104 Partidos) ---
def cargar_fixture():
    groups = {
        "A": ["Mexico", "Sudafrica", "Corea del Sur", "Rep. Checa"], "B": ["Canada", "Bosnia", "Qatar", "Suiza"],
        "C": ["Brasil", "Haiti", "Marruecos", "Escocia"], "D": ["EE. UU.", "Turquia", "Australia", "Paraguay"],
        "E": ["Alemania", "Curazao", "C. Marfil", "Ecuador"], "F": ["P. Bajos", "Japon", "Suecia", "Tunez"],
        "G": ["Belgica", "Egipto", "Iran", "N. Zelanda"], "H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
        "I": ["Francia", "Senegal", "Irak", "Noruega"], "J": ["Austria", "Jordania", "Argentina", "Argelia"],
        "K": ["Portugal", "RD Congo", "Uzbekistan", "Colombia"], "L": ["Inglaterra", "Croacia", "Ghana", "Panama"]
    }
    matches = []
    mid = 1
    for g_name, teams in groups.items():
        dates = ["11/06", "11/06", "17/06", "17/06", "22/06", "22/06"]
        if g_name in ["D","E","F"]: dates = ["14/06", "15/06", "19/06", "20/06", "24/06", "25/06"]
        if g_name in ["G","H","I"]: dates = ["16/06", "17/06", "21/06", "22/06", "26/06", "27/06"]
        if g_name in ["J","K","L"]: dates = ["18/06", "19/06", "24/06", "25/06", "28/06", "29/06"]
        pairs = [(teams[0], teams[1]), (teams[2], teams[3]), (teams[0], teams[2]), (teams[1], teams[3]), (teams[3], teams[0]), (teams[1], teams[2])]
        for i, p in enumerate(pairs):
            matches.append({"id": mid, "fase": "Grupos", "grupo": g_name, "e1": p[0], "e2": p[1], "fecha": dates[i], "hora": "18:00" if i%2==0 else "22:00"})
            mid += 1
    # Eliminatorias
    fases = [("Ronda de 32", 16), ("Octavos", 8), ("Cuartos", 4), ("Semis", 2), ("Tercer Puesto", 1), ("Gran Final", 1)]
    for f_nom, cant in fases:
        for _ in range(cant):
            matches.append({"id": mid, "fase": f_nom, "grupo": "Eliminatoria", "e1": f"Clasificado {mid}A", "e2": f"Clasificado {mid}B", "fecha": "Julio", "hora": "20:00"})
            mid += 1
    return pd.DataFrame(matches)

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp { background: linear-gradient(to right, rgba(255,255,255,0.95), rgba(255,255,255,0.9)), url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093"); background-size: cover; background-attachment: fixed; }
    [data-testid="stImage"] > img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 10px; display: inline-block; margin-bottom: 20px; border: 1px solid #eee; }
    .info-card { background: white; border-left: 5px solid #ED1C24; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .grupo-header-card { background: linear-gradient(90deg, #ED1C24, #B21217); color: white; padding: 12px; border-radius: 8px 8px 0 0; font-weight: bold; display: flex; justify-content: space-between; margin-top: 15px;}
    .grupo-tabla-card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING", "🔒 ADMIN"])

# --- TAB 1: PRONÓSTICOS ---
with menu[0]:
    st.markdown('<div class="info-card"><b>🏆 PUNTOS:</b> 3 pts Resultado Exacto | 1 pt Ganador o Empate.<br><b>🃏 COMODÍN:</b> 50 pts al exacto | 10 pts al Top 10 más cercano.</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom, u_ape, u_wn = c1.text_input("Nombre:").strip(), c2.text_input("Apellido:").strip(), c3.text_input("WN:").strip().upper()
    u_sec = c4.selectbox("Sector:", ["Finanzas","Compras","Créditos","RRHH","IT","Dirección","Logistica","Televentas","Tiendas","e-Commerce","Ventas","Marketing","Sales Operation","Otro"], index=None)

    if all([u_nom, u_ape, u_wn, u_sec]):
        db = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db)
        db.close()

        v_com = float(df_u[df_u['partido_id']==999].iloc[0]['g1']) if 999 in df_u['partido_id'].values else 0.0
        if st.session_state.comodin_temp is None and v_com == 0.0:
            @st.dialog("🃏 COMODÍN JUNIO")
            def modal():
                val = st.number_input("Cumplimiento Würth Uruguay (%):", 0.0, 200.0, step=0.1)
                if st.button("Confirmar"): st.session_state.comodin_temp = val; st.rerun()
            modal()
        
        cur_c = st.session_state.comodin_temp if st.session_state.comodin_temp is not None else v_com
        st.markdown(f'<div class="info-card"><b>🃏 Tu Comodín: {cur_c}%</b></div>', unsafe_allow_html=True)

        f_tabs = st.tabs(["Grupos", "Eliminatorias"])
        with f_tabs[0]:
            df_fixture = cargar_fixture()
            df_g = df_fixture[df_fixture['fase']=="Grupos"]
            dias = sorted(df_g['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            t_dias = st.tabs([f"📅 {d}" for d in dias])
            for i, d in enumerate(dias):
                with t_dias[i]:
                    with st.form(f"f_{d}"):
                        p_dia = df_g[df_g['fecha']==d]
                        for _, r in p_dia.iterrows():
                            v1, v2, ok = (0,0,False)
                            if r['id'] in df_u['partido_id'].values:
                                reg = df_u[df_u['partido_id']==r['id']].iloc[0]
                                v1, v2, ok = int(reg['g1']), int(reg['g2']), True
                            st.markdown(f'<div class="grupo-header-card"><span>GRUPO {r["grupo"]}{" ✅" if ok else ""}</span><span>{r["hora"]} hs</span></div>', unsafe_allow_html=True)
                            c1p, c2p, c3p = st.columns([4,1,1])
                            c1p.markdown(f"<br><b>{r['e1']}</b> vs <b>{r['e2']}</b>", unsafe_allow_html=True)
                            st.session_state[f"g1_{r['id']}"] = c2p.number_input("L", 0, 20, v1, key=f"n1_{r['id']}")
                            st.session_state[f"g2_{r['id']}"] = c3p.number_input("V", 0, 20, v2, key=f"n2_{r['id']}")
                        if st.form_submit_button("💾 Guardar"):
                            db = sqlite3.connect('penca.db')
                            c = db.cursor()
                            c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}' AND partido_id IN ({','.join(map(str, p_dia['id']))})")
                            for pid in p_dia['id']:
                                c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", (u_wn, u_nom, u_ape, u_sec, pid, st.session_state[f"g1_{pid}"], st.session_state[f"g2_{pid}"], datetime.now().strftime("%Y-%m-%d %H:%M")))
                            c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}' AND partido_id=999")
                            c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", (u_wn, u_nom, u_ape, u_sec, 999, cur_c, 0, ""))
                            db.commit(); db.close(); st.rerun()
        with f_tabs[1]: st.info("⚽ Se habilita al terminar la Fase de Grupos.")

# --- TAB 2: TABLAS ---
with menu[1]:
    df_fix = cargar_fixture()
    cols = st.columns(3)
    for i, g in enumerate(sorted(df_fix[df_fix['fase']=="Grupos"]['grupo'].unique())):
        with cols[i%3]:
            st.markdown(f'<div class="grupo-tabla-card"><div style="background:#ED1C24;color:white;text-align:center;font-weight:bold;padding:5px;border-radius:4px;margin-bottom:10px;">GRUPO {g}</div>', unsafe_allow_html=True)
            eqs = pd.concat([df_fix[df_fix['grupo']==g]['e1'], df_fix[df_fix['grupo']==g]['e2']]).unique()
            for e in eqs: st.write(f"⚽ {e}")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: RANKING ---
with menu[2]:
    st.subheader("🥇 Tabla de Posiciones")
    try:
        df_real = pd.read_excel(URL_RESULTADOS_REALES)
        db = sqlite3.connect('penca.db'); df_ap = pd.read_sql("SELECT * FROM apuestas", db); db.close()
        if not df_ap.empty:
            merged = df_ap.merge(df_real[['partido_id', 'G1 Real', 'G2 Real']], on='partido_id', how='inner')
            def calc(r):
                if pd.isna(r['G1 Real']): return 0
                if r['g1'] == r['G1 Real'] and r['g2'] == r['G2 Real']: return 3
                if (r['g1'] > r['g2'] and r['G1 Real'] > r['G2 Real']) or (r['g1'] < r['g2'] and r['G1 Real'] < r['G2 Real']) or (r['g1'] == r['g2'] and r['G1 Real'] == r['G2 Real']): return 1
                return 0
            merged['pts'] = merged.apply(calc, axis=1)
            rank = merged.groupby(['wn', 'nombre', 'apellido', 'sector'])['pts'].sum().reset_index()
            st.dataframe(rank.sort_values('pts', ascending=False), use_container_width=True)
        else: st.info("Esperando apuestas...")
    except: st.warning("Resultados reales no disponibles aún.")

# --- TAB 4: ADMIN ---
with menu[3]:
    if not st.session_state.admin_logged:
        with st.form("login"):
            pw = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Acceder"):
                # SOLUCIÓN AL ERROR: No usar try/except genérico aquí
                if pw == st.secrets["admin_password"]:
                    st.session_state.admin_logged = True
                    st.rerun()
                else: st.error("Clave Incorrecta")
    else:
        if st.button("Cerrar"): st.session_state.admin_logged = False; st.rerun()
        db = sqlite3.connect('penca.db'); df = pd.read_sql("SELECT * FROM apuestas", db); db.close()
        st.download_button("📥 Descargar DB", df.to_csv(index=False), "penca.csv", "text/csv")
        st.dataframe(df)
