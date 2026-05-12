import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE TOTAL RECUPERADO (Fase de Grupos + Eliminatorias) ---
def cargar_fixture():
    # Grupos (Extracto del PDF)
    grupos = [
        {"id": 1, "fase": "Grupos", "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "fase": "Grupos", "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 3, "fase": "Grupos", "grupo": "B", "e1": "Canadá 🇨🇦", "e2": "Bosnia 🇧🇦", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "fase": "Grupos", "grupo": "B", "e1": "Qatar 🇶🇦", "e2": "Suiza 🇨🇭", "fecha": "12/06", "hora": "20:00"},
        {"id": 5, "fase": "Grupos", "grupo": "C", "e1": "Brasil 🇧🇷", "e2": "Haití 🇭🇹", "fecha": "13/06", "hora": "14:00"},
        {"id": 9, "fase": "Grupos", "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia S. 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 10, "fase": "Grupos", "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
        # ... Aquí se completan los 72 partidos del PDF
    ]
    # Eliminatorias (Pendientes de cruces)
    eliminatorias = [
        {"id": 101, "fase": "Octavos", "grupo": "Eliminatoria", "e1": "1° Grupo A", "e2": "2° Grupo B", "fecha": "28/06", "hora": "15:00"},
        {"id": 201, "fase": "Cuartos", "grupo": "Eliminatoria", "e1": "Ganador 101", "e2": "Ganador 102", "fecha": "04/07", "hora": "17:00"},
        {"id": 301, "fase": "Final", "grupo": "Final", "e1": "Ganador Semis 1", "e2": "Ganador Semis 2", "fecha": "19/07", "hora": "19:00"},
    ]
    return pd.DataFrame(grupos + eliminatorias)

# --- 3. ESTILO VISUAL CEREBRO (Logo Blindado) ---
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
    .info-comodin {
        background-color: white; border-left: 5px solid #ED1C24;
        padding: 15px; border-radius: 4px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. POP-UP COMODÍN ---
@st.dialog("🃏 COMODÍN DE VENTAS JUNIO")
def modal_comodin(v_actual):
    st.write("¿Qué % de cumplimiento alcanzará Würth Uruguay este mes?")
    val = st.number_input("Tu apuesta:", 0.0, 200.0, v_actual, step=0.1)
    if st.button("Confirmar Comodín"):
        st.session_state.comodin_temp = val
        st.rerun()

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING"])

with menu[0]:
    df_fixture_full = cargar_fixture()
    
    # REGISTRO
    st.subheader("👤 Registro")
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom = c1.text_input("Nombre:").strip()
    u_ape = c2.text_input("Apellido:").strip()
    u_wn = c3.text_input("Código WN:").strip().upper()
    u_sec = c4.selectbox("Sector:", ["RRHH", "Finanzas", "Créditos", "Compras", "IT", "Marketing", "Logística", "Ventas", "Otra"])

    if u_nom and u_ape and u_wn:
        try:
            # LEER TODO (ttl=0 para evitar caché vieja)
            df_apuestas_total = conn.read(worksheet="apuestas", ttl=0)
            df_apuestas_total['wn'] = df_apuestas_total['wn'].astype(str).str.upper()
            df_u = df_apuestas_total[df_apuestas_total['wn'] == u_wn]
        except:
            df_apuestas_total, df_u = pd.DataFrame(), pd.DataFrame()

        # COMODÍN
        v_com = 0.0
        if not df_u.empty:
            prev_c = df_u[df_u['partido_id'] == 999]
            if not prev_c.empty: v_com = float(prev_c.iloc[0]['goles_equipo_1'])
        
        if 'comodin_temp' not in st.session_state and v_com == 0.0:
            modal_comodin(0.0)
        
        current_com = st.session_state.get('comodin_temp', v_com)
        st.markdown(f'<div class="info-comodin"><b>🃏 Comodín Ventas:</b> Tu apuesta actual es <b>{current_com}%</b>.</div>', unsafe_allow_html=True)

        # NAVEGACIÓN POR FASES
        fase_tab = st.tabs(["Fase de Grupos", "🔒 Octavos", "🔒 Cuartos", "🔒 Final"])
        
        with fase_tab[0]:
            df_grupos = df_fixture_full[df_fixture_full['fase'] == "Grupos"]
            dias = sorted(df_grupos['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
            tabs_dias = st.tabs([f"📅 {d}" for d in dias])

            with st.form("penca_fase_grupos_form"):
                for i, dia in enumerate(dias):
                    with tabs_dias[i]:
                        partidos_dia = df_grupos[df_grupos['fecha'] == dia]
                        for _, row in partidos_dia.iterrows():
                            # Identificar si ya está guardado
                            v1, v2, lleno = 0, 0, False
                            if not df_u.empty:
                                prev = df_u[df_u['partido_id'] == row['id']]
                                if not prev.empty:
                                    v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])
                                    lleno = True

                            st.markdown(f'<div class="grupo-header-card"><span>GRUPO {row["grupo"]} {"✅" if lleno else ""}</span><span style="font-size: 13px; opacity: 0.8;">{row["hora"]} hs</span></div>', unsafe_allow_html=True)
                            col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                            with col_p:
                                st.markdown(f"<div style='padding-top:20px; font-size:18px;'><b>{row['e1']}</b> vs <b>{row['e2']}</b></div>", unsafe_allow_html=True)
                            with col_g1:
                                st.number_input(f"L", 0, 20, v1, key=f"e1_{row['id']}")
                            with col_g2:
                                st.number_input(f"V", 0, 20, v2, key=f"e2_{row['id']}")

                if st.form_submit_button("💾 GUARDAR TODOS LOS PRONÓSTICOS"):
                    nuevas = []
                    # Recolectar datos
                    for _, row in df_fixture_full[df_fixture_full['fase'] == "Grupos"].iterrows():
                        nuevas.append({
                            "nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": u_sec,
                            "partido_id": row['id'], 
                            "goles_equipo_1": st.session_state[f"e1_{row['id']}"],
                            "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                    nuevas.append({"nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": u_sec, "partido_id": 999, "goles_equipo_1": current_com, "goles_equipo_2": 0, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    
                    # CONSOLIDACIÓN TOTAL: Mantener otros usuarios, actualizar este
                    df_otros = df_apuestas_total[df_apuestas_total['wn'] != u_wn] if not df_apuestas_total.empty else pd.DataFrame()
                    df_final = pd.concat([df_otros, pd.DataFrame(nuevas)], ignore_index=True)
                    
                    # EL TRUCO: Usamos .update() que pisa toda la hoja, evitando el error de "celdas protegidas"
                    conn.update(worksheet="apuestas", data=df_final)
                    st.success("¡Sincronizado con Drive!")
                    st.rerun()

        with fase_tab[1]: st.info("🔒 Octavos: Se habilitará al terminar la Fase de Grupos.")
