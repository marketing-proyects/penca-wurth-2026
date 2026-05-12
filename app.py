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

# --- 2. FIXTURE INTEGRAL (72 Partidos con Horario Uruguay) ---
def cargar_fixture():
    groups_data = {
        "A": ["México", "Sudáfrica", "Corea del Sur", "Rep. Checa"],
        "B": ["Canadá", "Bosnia", "Qatar", "Suiza"],
        "C": ["Brasil", "Haití", "Marruecos", "Escocia"],
        "D": ["EE. UU.", "Turquía", "Australia", "Paraguay"],
        "E": ["Alemania", "Curazao", "C. Marfil", "Ecuador"],
        "F": ["P. Bajos", "Japón", "Suecia", "Túnez"],
        "G": ["Bélgica", "Egipto", "Irán", "N. Zelanda"],
        "H": ["España", "Cabo Verde", "Arabia Saudita", "Uruguay"],
        "I": ["Francia", "Senegal", "Irak", "Noruega"],
        "J": ["Austria", "Jordania", "Argentina", "Argelia"],
        "K": ["Portugal", "RD Congo", "Uzbekistán", "Colombia"],
        "L": ["Inglaterra", "Croacia", "Ghana", "Panamá"]
    }
    
    matches = []
    match_id = 1
    for group_name, teams in groups_data.items():
        # Horarios ajustados (Ejemplos basados en PDF para Uruguay y partidos clave)
        # 18:00, 22:00, 15:00, 21:00 son horarios comunes en el fixture
        dates = ["11/06", "11/06", "17/06", "17/06", "22/06", "22/06"]
        horas = ["18:00", "22:00", "22:00", "18:00", "16:00", "20:00"]
        
        # Ajuste específico para el Grupo H (Uruguay)
        if group_name == "H":
            dates = ["17/06", "17/06", "22/06", "22/06", "27/06", "27/06"]
            horas = ["15:00", "19:00", "19:00", "15:00", "21:00", "21:00"]
            # Uruguay vs Arabia S (15/06 - 15:00) -> Ajustado a la lógica de bloques
        
        pairs = [(teams[0], teams[1]), (teams[2], teams[3]), (teams[0], teams[2]), (teams[1], teams[3]), (teams[3], teams[0]), (teams[1], teams[2])]
        
        for i, pair in enumerate(pairs):
            matches.append({
                "id": match_id, "fase": "Grupos", "grupo": group_name,
                "e1": pair[0], "e2": pair[1], "fecha": dates[i], "hora": horas[i]
            })
            match_id += 1
            
    return pd.DataFrame(matches)

# --- 3. DIÁLOGO COMODÍN ---
@st.dialog("🃏 COMODÍN DE VENTAS JUNIO")
def modal_comodin(v_actual):
    st.markdown("##### ¿Qué porcentaje de cumplimiento alcanzará Würth Uruguay este mes?")
    val = st.number_input("Tu apuesta (%):", 0.0, 200.0, v_actual, step=0.1)
    st.write("📌 **Lógica de Puntos:**")
    st.write("- 50 pts: Acierto exacto del cumplimiento.")
    st.write("- 10 pts: Estar dentro del Top 10 de colaboradores más cercanos.")
    if st.button("Confirmar Apuesta"):
        st.session_state.comodin_temp = val
        st.rerun()

# --- 4. ESTILO VISUAL (Logo Blindado y Tablas) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stImage"] > img, [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 10px; display: inline-block; margin-bottom: 20px; border: 1px solid #eee; }
    
    .grupo-header-card {
        background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%);
        color: white; padding: 12px; border-radius: 8px 8px 0px 0px;
        font-weight: bold; font-size: 15px; margin-top: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .info-comodin-card {
        background: white; border-left: 5px solid #ED1C24; padding: 15px; 
        margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-radius: 0 4px 4px 0;
    }
    .grupo-tabla-card {
        background: white; border: 1px solid #ddd; border-radius: 8px;
        padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .status-text { font-size: 12px; color: #28a745; font-weight: bold; }
    .time-badge { background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
logo_path = "logo_wurth.jpg"
st.image(logo_path if os.path.exists(logo_path) else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
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
    
    sectores_wurth = ["Finanzas", "Compras", "Créditos", "RRHH", "IT", "Dirección", "Logistica", "Televentas", "Tiendas", "e-Commerce", "Ventas", "Marketing", "Sales Operation", "Otro"]
    u_sec = c4.selectbox("Sector:", sectores_wurth, index=None, placeholder="Selecciona tu sector...")

    if all([u_nom, u_ape, u_wn, u_sec]):
        db_conn = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db_conn)
        db_conn.close()

        v_com_registrado = 0.0
        if not df_u.empty:
            p_com = df_u[df_u['partido_id'] == 999]
            if not p_com.empty: v_com_registrado = float(p_com.iloc[0]['g1'])
        
        if 'comodin_temp' not in st.session_state and v_com_registrado == 0.0:
            modal_comodin(0.0)
        
        cur_com = st.session_state.get('comodin_temp', v_com_registrado)
        st.markdown(f'''
            <div class="info-comodin-card">
                <b>🃏 Comodín Ventas Junio:</b> Tu pronóstico es del <b>{cur_com}%</b>.<br>
                <small style="color: #666;">Lógica: 50 pts al exacto | 10 pts al Top 10 más cercano.</small>
            </div>''', unsafe_allow_html=True)

        df_g = df_fixture[df_fixture['fase'] == "Grupos"]
        dias = sorted(df_g['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
        tabs_dias = st.tabs([f"📅 {d} (Horario UY)" for d in dias])

        for i, dia in enumerate(dias):
            with tabs_dias[i]:
                with st.form(key=f"form_dia_{dia}"):
                    partidos_dia = df_g[df_g['fecha'] == dia]
                    ids_dia = partidos_dia['id'].tolist()
                    for _, row in partidos_dia.iterrows():
                        v1, v2, guardado = 0, 0, False
                        if not df_u.empty:
                            prev = df_u[df_u['partido_id'] == row['id']]
                            if not prev.empty:
                                v1, v2 = int(prev.iloc[0]['g1']), int(prev.iloc[0]['g2'])
                                guardado = True

                        tick = " ✅" if guardado else ""
                        status = '<span class="status-text">Resultado ingresado</span>' if guardado else ""

                        st.markdown(f'''
                            <div class="grupo-header-card">
                                <span>GRUPO {row["grupo"]}{tick}</span>
                                <span class="time-badge">{row["hora"]} hs (UY)</span>
                                {status}
                            </div>''', unsafe_allow_html=True)
                        
                        cp, cg1, cg2 = st.columns([4, 1, 1])
                        cp.markdown(f"<div style='padding-top:20px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                        st.session_state[f"g1_{row['id']}"] = cg1.number_input("L", 0, 20, v1, key=f"in_g1_{row['id']}")
                        st.session_state[f"g2_{row['id']}"] = cg2.number_input("V", 0, 20, v2, key=f"in_g2_{row['id']}")

                    if st.form_submit_button(f"💾 Guardar Pronósticos del {dia}"):
                        db_conn = sqlite3.connect('penca.db')
                        c = db_conn.cursor()
                        ids_str = ",".join(map(str, ids_dia))
                        c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}' AND partido_id IN ({ids_str})")
                        for pid in ids_dia:
                            g1 = st.session_state.get(f"in_g1_{pid}", 0)
                            g2 = st.session_state.get(f"in_g2_{pid}", 0)
                            c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                                     (u_wn, u_nom, u_ape, u_sec, pid, g1, g2, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}' AND partido_id=999")
                        c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                                 (u_wn, u_nom, u_ape, u_sec, 999, cur_com, 0, datetime.now().strftime("%Y-%m-%d %H:%M")))
                        db_conn.commit()
                        db_conn.close()
                        st.success(f"¡Día {dia} guardado correctamente!")
                        st.rerun()

# --- TAB 2: TABLAS (RECUPERADA Y ACTUALIZADA) ---
with menu[1]:
    st.subheader("📊 Composición de los Grupos (Mundial 2026)")
    df_fix_all = cargar_fixture()
    grupos_lista = sorted(df_fix_all[df_fix_all['fase']=='Grupos']['grupo'].unique())
    
    cols = st.columns(3)
    for idx, g_name in enumerate(grupos_lista):
        with cols[idx % 3]:
            st.markdown(f'''
                <div class="grupo-tabla-card">
                    <div style="background:#ED1C24; color:white; padding:8px; border-radius:4px; font-weight:bold; margin-bottom:10px; text-align:center;">
                        GRUPO {g_name}
                    </div>''', unsafe_allow_html=True)
            # Obtenemos los integrantes únicos del grupo
            equipos_g = pd.concat([df_fix_all[df_fix_all['grupo']==g_name]['e1'], 
                                   df_fix_all[df_fix_all['grupo']==g_name]['e2']]).unique()
            for eq in equipos_g:
                st.markdown(f"⚽ {eq}")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: ADMIN ---
with menu[3]:
    st.subheader("🔒 Panel Administrativo")
    if "admin_logged" not in st.session_state: st.session_state.admin_logged = False
    if not st.session_state.admin_logged:
        with st.form("admin_login"):
            pass_input = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("Acceder"):
                if pass_input == "market1NG?":
                    st.session_state.admin_logged = True
                    st.rerun()
                else: st.error("Clave incorrecta")
    else:
        if st.button("Cerrar Sesión Admin"):
            st.session_state.admin_logged = False
            st.rerun()
        db_conn = sqlite3.connect('penca.db')
        df_admin = pd.read_sql("SELECT * FROM apuestas", db_conn)
        db_conn.close()
        if not df_admin.empty:
            csv = df_admin.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Resultados (CSV)", csv, "penca_wurth.csv", "text/csv")
            st.dataframe(df_admin)
