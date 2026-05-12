import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Penca Würth 2026", page_icon="⚽", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. FIXTURE REAL (Extraído de PDF y ajustado a Hora UY) ---
def cargar_fixture():
    data = [
        {"id": 1, "grupo": "GRUPO A", "e1": "México", "e2": "Sudáfrica", "fecha": "11/06", "hora": "18:00"},
        {"id": 2, "grupo": "GRUPO A", "e1": "Corea del Sur", "e2": "Rep. Checa", "fecha": "11/06", "hora": "22:00"},
        {"id": 3, "grupo": "GRUPO B", "e1": "Canadá", "e2": "Bosnia", "fecha": "12/06", "hora": "16:00"},
        {"id": 4, "grupo": "GRUPO B", "e1": "Qatar", "e2": "Suiza", "fecha": "12/06", "hora": "20:00"},
        {"id": 5, "grupo": "GRUPO C", "e1": "Brasil", "e2": "Haití", "fecha": "13/06", "hora": "14:00"},
        {"id": 6, "grupo": "GRUPO C", "e1": "Marruecos", "e2": "Escocia", "fecha": "13/06", "hora": "19:00"},
        {"id": 7, "grupo": "GRUPO D", "e1": "EE. UU.", "e2": "Turquía", "fecha": "14/06", "hora": "17:00"},
        {"id": 8, "grupo": "GRUPO D", "e1": "Australia", "e2": "Paraguay", "fecha": "14/06", "hora": "21:00"},
        {"id": 9, "grupo": "GRUPO F", "e1": "Uruguay", "e2": "Arabia Saudita", "fecha": "15/06", "hora": "15:00"},
        # Nota: Se pueden completar los 48 partidos siguiendo el PDF.
    ]
    return pd.DataFrame(data)

# --- 3. ESTILO VISUAL (CEREBRO / LUZ) ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none;}
    .stApp {
        background: linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.92) 50%, rgba(255,255,255,0.85) 100%), 
                    url("https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=2093");
        background-size: cover; background-attachment: fixed;
    }
    [data-testid="stImage"] img { border-radius: 0px !important; }
    .logo-box { background-color: white; padding: 5px; border: 1px solid #f0f0f0; display: inline-block; margin-bottom: 20px; }
    h1, h2 { color: #ED1C24 !important; font-family: 'Arial Black', sans-serif; text-transform: uppercase; }
    .grupo-header { 
        background-color: #ED1C24; color: white; padding: 12px; border-radius: 4px; 
        margin-top: 25px; font-weight: bold; font-size: 18px;
    }
    .comodin-card {
        background-color: rgba(255, 255, 255, 0.9); padding: 30px;
        border-radius: 10px; margin-top: 40px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. RENDER CABECERA ---
st.markdown('<div class="logo-box">', unsafe_allow_html=True)
st.image("logo_wurth.jpg" if os.path.exists("logo_wurth.jpg") else "https://upload.wikimedia.org/wikipedia/commons/1/1e/Wuerth_Logo_2024.svg", width=200)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<h1 style='color: #ED1C24; font-size: 42px; margin-bottom: 30px;'>PENCA DIGITAL WÜRTH 2026</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ PRONÓSTICOS Y COMODÍN", "🥇 RANKING"])

with tab1:
    df_fixture = cargar_fixture()
    
    if 'paso_registro' not in st.session_state:
        st.session_state.paso_registro = False

    # REGISTRO
    st.subheader("👤 Registro del Colaborador")
    col1, col2 = st.columns(2)
    u_nombre = col1.text_input("Nombre:").strip()
    u_apellido = col2.text_input("Apellido:").strip()
    
    col3, col4 = st.columns(2)
    u_email = col3.text_input("Email:")
    u_sector = col4.selectbox("Sector:", ["RRHH", "Finanzas", "Créditos", "Compras", "IT", "Dirección", "CEO", "Logística", "Tiendas", "Telentas", "e-Commerce", "Ventas", "Otra"])

    if st.button("INGRESAR AL FIXTURE"):
        if u_nombre and u_apellido and "@" in u_email:
            st.session_state.paso_registro = True
            st.rerun()
        else:
            st.error("Por favor, completa los campos correctamente.")

    if st.session_state.paso_registro:
        st.divider()
        
        try:
            df_todas = conn.read(worksheet="apuestas", ttl=0)
            df_usu = df_todas[(df_todas['nombre'].str.lower() == u_nombre.lower()) & 
                             (df_todas['apellido'].str.lower() == u_apellido.lower())]
        except:
            df_todas = pd.DataFrame()
            df_usu = pd.DataFrame()

        with st.form("penca_grupos"):
            # FIXTURE POR GRUPOS
            grupos = df_fixture['grupo'].unique()
            for g in grupos:
                st.markdown(f'<div class="grupo-header">{g}</div>', unsafe_allow_html=True)
                partidos_grupo = df_fixture[df_fixture['grupo'] == g]
                
                for _, row in partidos_grupo.iterrows():
                    v1, v2 = 0, 0
                    if not df_usu.empty:
                        prev = df_usu[df_usu['partido_id'] == row['id']]
                        if not prev.empty:
                            v1, v2 = int(prev.iloc[0]['goles_equipo_1']), int(prev.iloc[0]['goles_equipo_2'])

                    col_p, col_g1, col_g2 = st.columns([4, 1, 1])
                    with col_p:
                        st.markdown(f"<div style='padding-top:15px;'><b>{row['e1']} vs {row['e2']}</b><br><small>{row['fecha']} - {row['hora']} hs</small></div>", unsafe_allow_html=True)
                    with col_g1:
                        st.number_input(f"Goles {row['e1']}", 0, 20, v1, key=f"e1_{row['id']}")
                    with col_g2:
                        st.number_input(f"Goles {row['e2']}", 0, 20, v2, key=f"e2_{row['id']}")
            
            # SECCIÓN COMODÍN (Integrada)
            st.markdown('<div class="comodin-card">', unsafe_allow_html=True)
            # Aquí puedes poner el st.image("comodin.jpg") cuando lo tengas
            st.subheader("🃏 COMODÍN DE VENTAS JUNIO")
            st.write("¿Qué porcentaje de cumplimiento crees que alcanzará la empresa este mes?")
            
            v_comodin = 0.0
            if not df_usu.empty:
                prev_c = df_usu[df_usu['partido_id'] == 999]
                if not prev_c.empty: v_comodin = float(prev_c.iloc[0]['goles_equipo_1'])

            u_comodin = st.number_input("Ingresa tu porcentaje (ej: 102.5):", 0.0, 200.0, v_comodin, step=0.1, key="comodin_junio")
            
            st.markdown(f"""
                <div style='text-align: left; background: #fff; padding: 15px; border-radius: 5px; margin-top: 10px; border-left: 4px solid #ED1C24;'>
                <b>Reglas de Puntaje:</b><br>
                • <b>50 Puntos:</b> Si aciertas el porcentaje exacto (con 1 decimal).<br>
                • <b>10 Puntos:</b> Si no acertaste el exacto, pero tu apuesta está dentro de las 10 más cercanas al resultado real.
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.form_submit_button("💾 GUARDAR PRONÓSTICOS Y COMODÍN"):
                nuevas = []
                for _, row in df_fixture.iterrows():
                    nuevas.append({
                        "nombre": u_nombre, "apellido": u_apellido, "email": u_email, "sector": u_sector,
                        "partido_id": row['id'], 
                        "goles_equipo_1": st.session_state[f"e1_{row['id']}"],
                        "goles_equipo_2": st.session_state[f"e2_{row['id']}"],
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                # Registro Comodín
                nuevas.append({
                    "nombre": u_nombre, "apellido": u_apellido, "email": u_email, "sector": u_sector,
                    "partido_id": 999, "goles_equipo_1": u_comodin, "goles_equipo_2": 0,
                    "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                df_envio = pd.DataFrame(nuevas)
                if not df_todas.empty:
                    df_limpio = df_todas[~((df_todas['nombre'].str.lower() == u_nombre.lower()) & (df_todas['apellido'].str.lower() == u_apellido.lower()))]
                    df_final = pd.concat([df_limpio, df_envio], ignore_index=True)
                else:
                    df_final = df_envio
                
                conn.update(worksheet="apuestas", data=df_final)
                st.success("¡Datos guardados con éxito!")
                st.balloons()

with tab2:
    st.header("🥇 Ranking")
    st.info("El ranking se calcula sumando puntos por aciertos en fútbol + el bono del comodín de ventas.")
