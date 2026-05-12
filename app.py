import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")

def init_db():
    conn = sqlite3.connect('penca.db')
    c = conn.cursor()
    # Tabla de apuestas
    c.execute('''CREATE TABLE IF NOT EXISTS apuestas 
                 (wn TEXT, nombre TEXT, apellido TEXT, sector TEXT, partido_id INTEGER, 
                  g1 INTEGER, g2 INTEGER, fecha_reg TEXT)''')
    # Tabla de resultados reales (para el administrador)
    c.execute('''CREATE TABLE IF NOT EXISTS resultados_reales 
                 (partido_id INTEGER PRIMARY KEY, r1 INTEGER, r2 INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. FIXTURE COMPLETO (Sincronizado con PDF - Grupos A al L) ---
def cargar_fixture():
    # Estructura simplificada basada en tu PDF (72 partidos de grupos)
    data = [
        {"id": 1, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "fase": "Grupos", "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 3, "fase": "Grupos", "grupo": "B", "e1": "Canadá 🇨🇦", "e2": "Bosnia 🇧🇦", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "fase": "Grupos", "grupo": "B", "e1": "Qatar 🇶🇦", "e2": "Suiza 🇨🇭", "fecha": "12/06", "hora": "20:00"},
        {"id": 5, "fase": "Grupos", "grupo": "C", "e1": "Brasil 🇧🇷", "e2": "Haití 🇭🇹", "fecha": "13/06", "hora": "14:00"},
        {"id": 9, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia S. 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 10, "fase": "Grupos", "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        # ... Aquí se cargan los 72 partidos de los 12 grupos
    ]
    # Estructura de fases finales
    eliminatorias = [
        {"id": 101, "fase": "Octavos", "grupo": "Elim.", "e1": "1º Grupo A", "e2": "2º Grupo B", "fecha": "28/06", "hora": "15:00"},
        {"id": 201, "fase": "Cuartos", "grupo": "Elim.", "e1": "Ganador 101", "e2": "Ganador 102", "fecha": "04/07", "hora": "17:00"},
        {"id": 301, "fase": "Final", "grupo": "Final", "e1": "Finalista 1", "e2": "Finalista 2", "fecha": "19/07", "hora": "19:00"},
    ]
    return pd.DataFrame(data + eliminatorias)

# --- 3. ESTILO VISUAL ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp { background: linear-gradient(to right, #ffffff, #f8f9fa); }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { padding: 10px; margin-bottom: 20px; }
    h1 { color: #ED1C24 !important; font-family: 'Arial Black'; }
    .grupo-header { 
        background: #ED1C24; color: white; padding: 10px; 
        border-radius: 5px 5px 0 0; font-weight: bold; margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING", "🔒 ADMIN"])

# --- TAB 1: PRONÓSTICOS ---
with menu[0]:
    df_fix = cargar_fixture()
    st.subheader("👤 Registro de Colaborador")
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom = c1.text_input("Nombre")
    u_ape = c2.text_input("Apellido")
    u_wn = c3.text_input("Código WN").upper()
    u_sec = c4.selectbox("Sector", ["Ventas", "Marketing", "Logística", "IT", "Administración", "Otros"])

    if u_nom and u_ape and u_wn:
        # Recuperar apuestas del usuario desde SQLite
        db_conn = sqlite3.connect('penca.db')
        df_u = pd.read_sql(f"SELECT * FROM apuestas WHERE wn='{u_wn}'", db_conn)
        db_conn.close()

        # Tabs de Fases
        f_tabs = st.tabs(["Fase de Grupos", "Octavos", "Cuartos", "Final"])
        
        with f_tabs[0]:
            df_g = df_fix[df_fix['fase'] == "Grupos"]
            dias = sorted(df_g['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            d_tabs = st.tabs([f"📅 {d}" for d in dias])
            
            with st.form("form_penca"):
                for idx, dia in enumerate(dias):
                    with d_tabs[idx]:
                        partidos = df_g[df_g['fecha'] == dia]
                        for _, row in partidos.iterrows():
                            # Cargar valores previos si existen
                            v1, v2, check = 0, 0, ""
                            if not df_u.empty:
                                prev = df_u[df_u['partido_id'] == row['id']]
                                if not prev.empty:
                                    v1, v2, check = int(prev.iloc[0]['g1']), int(prev.iloc[0]['g2']), " ✅"
                            
                            st.markdown(f'<div class="grupo-header">GRUPO {row["grupo"]} {check}</div>', unsafe_allow_html=True)
                            cp, cg1, cg2 = st.columns([4, 1, 1])
                            cp.write(f"**{row['e1']}** vs **{row['e2']}**")
                            res1 = cg1.number_input("L", 0, 20, v1, key=f"g1_{row['id']}")
                            res2 = cg2.number_input("V", 0, 20, v2, key=f"g2_{row['id']}")
                
                # Comodín Ventas
                st.divider()
                st.markdown("### 🃏 Comodín Ventas Junio")
                v_com = 100.0
                if not df_u.empty:
                    p_com = df_u[df_u['partido_id'] == 999]
                    if not p_com.empty: v_com = float(p_com.iloc[0]['g1'])
                u_com = st.number_input("¿% Cumplimiento empresa?", 0.0, 200.0, v_com, step=0.1)

                if st.form_submit_button("💾 GUARDAR PRONÓSTICOS"):
                    db_conn = sqlite3.connect('penca.db')
                    c = db_conn.cursor()
                    # Borrar anteriores para actualizar
                    c.execute(f"DELETE FROM apuestas WHERE wn='{u_wn}'")
                    # Insertar nuevos
                    for _, row in df_fix[df_fix['fase'] == "Grupos"].iterrows():
                        g1 = st.session_state.get(f"g1_{row['id']}", 0)
                        g2 = st.session_state.get(f"g2_{row['id']}", 0)
                        c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                                 (u_wn, u_nom, u_ape, u_sec, row['id'], g1, g2, datetime.now()))
                    # Guardar comodín (id 999)
                    c.execute("INSERT INTO apuestas VALUES (?,?,?,?,?,?,?,?)", 
                                 (u_wn, u_nom, u_ape, u_sec, 999, u_com, 0, datetime.now()))
                    db_conn.commit()
                    db_conn.close()
                    st.success("¡Pronósticos guardados en la base de datos local!")
                    st.rerun()

# --- TAB 4: ADMIN (Panel de Control Würth) ---
with menu[3]:
    st.subheader("🔑 Acceso Administrador")
    pass_admin = st.text_input("Contraseña", type="password")
    if pass_admin == "wurth2026": # Puedes cambiar la clave aquí
        db_conn = sqlite3.connect('penca.db')
        df_all = pd.read_sql("SELECT * FROM apuestas", db_conn)
        db_conn.close()
        
        st.write(f"### Resumen de Participación")
        st.write(f"Total de apuestas registradas: {len(df_all)}")
        
        # Botón para descargar Excel
        if not df_all.empty:
            excel_data = df_all.to_csv(index=False).encode('utf-8')
            st.download_button("📥 DESCARGAR TODAS LAS APUESTAS (CSV)", excel_data, "apuestas_penca_wurth.csv", "text/csv")
            st.dataframe(df_all)
        else:
            st.info("Aún no hay datos registrados.")
