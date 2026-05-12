import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE COMPLETO (Basado en PDF - Ajuste Hora UY) ---
def cargar_fixture():
    data = [
        {"id": 1, "grupo": "A", "e1": "México", "e2": "Sudáfrica", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "grupo": "A", "e1": "Corea del Sur", "e2": "Rep. Checa", "fecha": "11/06", "hora": "22:00"},
        {"id": 3, "grupo": "B", "e1": "Canadá", "e2": "Bosnia", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "grupo": "B", "e1": "Qatar", "e2": "Suiza", "fecha": "12/06", "hora": "20:00"},
        {"id": 5, "grupo": "C", "e1": "Brasil", "e2": "Haití", "fecha": "13/06", "hora": "14:00"},
        {"id": 6, "grupo": "C", "e1": "Marruecos", "e2": "Escocia", "fecha": "13/06", "hora": "19:00"},
        {"id": 7, "grupo": "D", "e1": "EE. UU.", "e2": "Turquía", "fecha": "14/06", "hora": "17:00"},
        {"id": 8, "grupo": "D", "e1": "Australia", "e2": "Paraguay", "fecha": "14/06", "hora": "21:00"},
        {"id": 9, "grupo": "F", "e1": "Uruguay", "e2": "Arabia Saudita", "fecha": "15/06", "hora": "15:00"},
        # Agregar aquí el resto de los partidos del PDF...
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (Luz y Transparencia Würth) ---
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
    
    /* Pestañas de Días */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255, 255, 255, 0.6); border-radius: 4px; padding: 8px 16px; font-size: 14px;
    }
    .stTabs [aria-selected="true"] { background-color: #ED1C24 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RENDER CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<h1 style='font-size: 38px;'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS DE GRUPOS", "🥇 RANKING"])

# --- TAB 1: PRONÓSTICOS POR DÍA ---
with menu[0]:
    df_fixture = cargar_fixture()
    
    st.subheader("👤 Tu Identificación")
    c1, c2, c3 = st.columns([1,1,2])
    u_nom = c1.text_input("Nombre:").strip()
    u_ape = c2.text_input("Apellido:").strip()
    u_sec = c3.selectbox("Sector:", ["RRHH", "Finanzas", "Créditos", "Compras", "IT", "Dirección", "Logística", "Tiendas", "e-Commerce", "Ventas", "Otra"])

    if u_nom and u_ape:
        try:
            df_apuestas = conn.read(worksheet="apuestas", ttl=0)
            df_u = df_apuestas[(df_apuestas['nombre'].str.lower() == u_nom.lower()) & (df_apuestas['apellido'].str.lower() == u_ape.lower())]
        except:
            df_apuestas = pd.DataFrame()
            df_u = pd.DataFrame()

        st.markdown("### Selecciona el día para apostar:")
        dias = sorted(df_fixture['fecha'].unique())
        tabs_dias = st.tabs(dias)

        with st.form("penca_form"):
            for i, dia in enumerate(dias):
                with tabs_dias[i]:
                    partidos_dia = df_fixture[df_fixture['fecha'] == dia]
                    for _, row in partidos_dia.iterrows():
                        v1, v2 = 0, 0
                        if not df_u.empty:
                            prev = df_u[df_u['partido_id'] == row['id']]
                            if not prev.empty:
                                v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])

                        col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                        with col_p:
                            st.markdown(f"<div style='padding-top:10px;'><b>GRUPO {row['grupo']}</b>: {row['e1']} vs {row['e2']} <small>({row['hora']} hs)</small></div>", unsafe_allow_html=True)
                        with col_g1:
                            st.number_input(f"{row['e1']}", 0, 20, v1, key=f"e1_{row['id']}")
                        with col_g2:
                            st.number_input(f"{row['e2']}", 0, 20, v2, key=f"e2_{row['id']}")

            # SECCIÓN COMODÍN (Sin recuadros blancos)
            st.divider()
            st.markdown("### 🃏 COMODÍN DE VENTAS JUNIO")
            v_com = 0.0
            if not df_u.empty:
                prev_c = df_u[df_u['partido_id'] == 999]
                if not prev_c.empty: v_com = float(prev_c.iloc[0]['goles_equipo_1'])
            
            u_com = st.number_input("¿Cumplimiento estimado de la empresa? (%)", 0.0, 200.0, v_com, step=0.1, key="comodin_val")
            st.caption("Regla: 50 pts al exacto | 10 pts al Top 10 más cercano.")

            if st.form_submit_button("💾 GUARDAR TODO"):
                nuevas = []
                for _, row in df_fixture.iterrows():
                    nuevas.append({
                        "nombre": u_nom, "apellido": u_ape, "sector": u_sec, "partido_id": row['id'], 
                        "goles_equipo_1": st.session_state[f"e1_{row['id']}"], "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                nuevas.append({"nombre": u_nom, "apellido": u_ape, "sector": u_sec, "partido_id": 999, "goles_equipo_1": u_com, "goles_equipo_2": 0, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")})
                
                df_f = pd.concat([df_apuestas[~((df_apuestas['nombre'].str.lower() == u_nom.lower()) & (df_apuestas['apellido'].str.lower() == u_ape.lower()))] if not df_apuestas.empty else pd.DataFrame(), pd.DataFrame(nuevas)], ignore_index=True)
                conn.update(worksheet="apuestas", data=df_f)
                st.success("¡Pronósticos guardados!")

# --- TAB 2: TABLAS DE POSICIONES (Cálculo Automático) ---
with menu[1]:
    st.subheader("📊 Posiciones del Mundial")
    try:
        df_real = conn.read(worksheet="partidos", ttl=0) # Tu pestaña de scores reales
        fixture = cargar_fixture()
        
        if not df_real.empty:
            # Unir fixture con resultados reales
            df_m = fixture.merge(df_real[['id', 'score_1_real', 'score_2_real']], on='id')
            
            for grupo in sorted(fixture['grupo'].unique()):
                st.markdown(f"#### GRUPO {grupo}")
                res_grupo = df_m[df_m['grupo'] == grupo]
                stats = {}

                for _, r in res_grupo.iterrows():
                    for equipo, goles, contra in [(r['e1'], r['score_1_real'], r['score_2_real']), (r['e2'], r['score_2_real'], r['score_1_real'])]:
                        if equipo not in stats: stats[equipo] = {'PJ': 0, 'Pts': 0, 'DG': 0}
                        if pd.notnull(goles):
                            stats[equipo]['PJ'] += 1
                            stats[equipo]['DG'] += (goles - contra)
                            if goles > contra: stats[equipo]['Pts'] += 3
                            elif goles == contra: stats[equipo]['Pts'] += 1
                
                df_stats = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index': 'Equipo'})
                st.table(df_stats.sort_values(by=['Pts', 'DG'], ascending=False))
    except:
        st.info("Las tablas se activarán cuando se carguen los primeros resultados reales.")

# --- TAB 3: RANKING PENCA ---
with menu[2]:
    st.subheader("🥇 Ranking de Colaboradores")
    st.info("Puntos: Fútbol + Bono Comodín.")
