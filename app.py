import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE (Resumen ampliado para la prueba) ---
def cargar_fixture():
    data = [
        {"id": 1, "grupo": "A", "e1": "México 🇲🇽", "e2": "Sudáfrica 🇿🇦", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "grupo": "A", "e1": "Corea del Sur 🇰🇷", "e2": "Rep. Checa 🇨🇿", "fecha": "11/06", "hora": "22:00"},
        {"id": 3, "grupo": "B", "e1": "Canadá 🇨🇦", "e2": "Bosnia 🇧🇦", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "grupo": "B", "e1": "Qatar 🇶🇦", "e2": "Suiza 🇨🇭", "fecha": "12/06", "hora": "20:00"},
        {"id": 9, "grupo": "F", "e1": "Uruguay 🇺🇾", "e2": "Arabia Saudita 🇸🇦", "fecha": "15/06", "hora": "15:00"},
        {"id": 20, "grupo": "F", "e1": "España 🇪🇸", "e2": "Cabo Verde 🇨🇻", "fecha": "15/06", "hora": "19:00"},
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (Logo Blindado e Indicadores) ---
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
    
    /* Estilo para partidos completados */
    .partido-completado {
        background-color: rgba(0, 0, 0, 0.03);
        border-radius: 8px;
        padding: 5px;
    }
    .grupo-header-card {
        background: linear-gradient(90deg, #ED1C24 0%, #B21217 100%);
        color: white; padding: 12px; border-radius: 8px 8px 0px 0px;
        font-weight: bold; font-size: 18px; margin-top: 20px;
        display: flex; align-items: center; justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MODAL COMODÍN ---
@st.dialog("🃏 COMODÍN DE VENTAS")
def modal_comodin(v_actual):
    st.write("¿Porcentaje de cumplimiento de Würth Uruguay en Junio?")
    val = st.number_input("Tu apuesta (%):", 0.0, 200.0, v_actual, step=0.1)
    if st.button("Confirmar"):
        st.session_state.comodin_temp = val
        st.rerun()

# --- 5. CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=180)
st.markdown('</div>', unsafe_allow_html=True)

menu = st.tabs(["⚽ PRONÓSTICOS", "🏆 TABLAS", "🥇 RANKING"])

with menu[0]:
    df_fixture = cargar_fixture()
    
    st.subheader("👤 Identificación")
    c1, c2, c3, c4 = st.columns([1,1,1,2])
    u_nom = c1.text_input("Nombre:").strip()
    u_ape = c2.text_input("Apellido:").strip()
    u_wn = c3.text_input("Código WN:").strip().upper()
    u_sec = c4.selectbox("Sector:", ["RRHH", "Finanzas", "Créditos", "Compras", "IT", "Marketing", "Logística", "Ventas", "Otra"])

    if u_nom and u_ape and u_wn:
        try:
            df_apuestas = conn.read(worksheet="apuestas", ttl=0)
            # Normalizamos WN a string para evitar el error del print
            df_apuestas['wn'] = df_apuestas['wn'].astype(str).str.upper()
            df_u = df_apuestas[df_apuestas['wn'] == u_wn]
        except:
            df_apuestas, df_u = pd.DataFrame(), pd.DataFrame()

        # Comodín
        v_comodin = 0.0
        if not df_u.empty:
            prev_c = df_u[df_u['partido_id'] == 999]
            if not prev_c.empty: v_comodin = float(prev_c.iloc[0]['goles_equipo_1'])
        
        if 'comodin_temp' not in st.session_state and v_comodin == 0.0:
            modal_comodin(0.0)
        
        current_com = st.session_state.get('comodin_temp', v_comodin)
        st.info(f"🃏 **Comodín Ventas:** {current_com}%")

        dias = sorted(df_fixture['fecha'].unique(), key=lambda x: datetime.strptime(x, "%d/%m"))
        tabs_dias = st.tabs([f"📅 {d}" for d in dias])

        with st.form("penca_v_final"):
            for i, dia in enumerate(dias):
                with tabs_dias[i]:
                    partidos_dia = df_fixture[df_fixture['fecha'] == dia]
                    for _, row in partidos_dia.iterrows():
                        # VERIFICACIÓN: ¿Ya está completado?
                        es_completado = False
                        v1, v2 = 0, 0
                        if not df_u.empty:
                            prev = df_u[df_u['partido_id'] == row['id']]
                            if not prev.empty:
                                v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])
                                es_completado = True

                        # Renderizado visual
                        div_class = 'class="partido-completado"' if es_completado else ""
                        st.markdown(f'<div class="grupo-header-card"><span>GRUPO {row["grupo"]} {" ✅" if es_completado else ""}</span><span style="font-size: 13px; opacity: 0.8;">{row["hora"]} hs</span></div>', unsafe_allow_html=True)
                        
                        col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                        with col_p:
                            label = f"**{row['e1']}** vs **{row['e2']}**"
                            st.markdown(f"<div style='padding-top:20px; font-size:18px;'>{label}</div>", unsafe_allow_html=True)
                        with col_g1:
                            st.number_input(f"Goles {row['e1']}", 0, 20, v1, key=f"e1_{row['id']}")
                        with col_g2:
                            st.number_input(f"Goles {row['e2']}", 0, 20, v2, key=f"e2_{row['id']}")

            if st.form_submit_button("💾 GUARDAR TODOS LOS PRONÓSTICOS"):
                # Lógica de guardado segura (corrigiendo el error de WN)
                nuevas = []
                for _, row in df_fixture.iterrows():
                    nuevas.append({
                        "nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": u_sec,
                        "partido_id": row['id'], 
                        "goles_equipo_1": st.session_state[f"e1_{row['id']}"],
                        "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                nuevas.append({"nombre": u_nom, "apellido": u_ape, "wn": u_wn, "sector": u_sec, "partido_id": 999, "goles_equipo_1": current_com, "goles_equipo_2": 0, "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")})
                
                # Filtrar con WN como string para evitar el UnsupportedOperationError
                df_limpio = df_apuestas[df_apuestas['wn'].astype(str).str.upper() != str(u_wn).upper()] if not df_apuestas.empty else pd.DataFrame()
                df_final = pd.concat([df_limpio, pd.DataFrame(nuevas)], ignore_index=True)
                
                conn.update(worksheet="apuestas", data=df_final)
                st.success("¡Pronósticos actualizados!")
                st.rerun() # Para que se vean los ✅ inmediatamente
