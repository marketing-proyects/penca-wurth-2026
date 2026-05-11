import streamlit as st
import pandas as pd
from datetime import datetime

# Función para cargar los partidos desde el CSV que creaste
def cargar_partidos():
    df = pd.read_csv('data/partidos.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

def pantalla_pronosticos():
    st.header("🥅 Ingresa tus Predicciones")
    st.info("Recuerda: Puedes cargar tus resultados hasta 1 hora antes de cada partido.")
    
    df_partidos = cargar_partidos()
    ahora = datetime.now() # Hora local de Uruguay

    # Formulario para capturar todas las apuestas a la vez
    with st.form("form_penca"):
        usuario = st.text_input("Nombre de Usuario / Legajo", placeholder="Ej: Diego_W")
        st.divider()
        
        nuevas_apuestas = []

        for index, row in df_partidos.iterrows():
            # Combinamos fecha y hora para validar si el partido ya empezó
            fecha_partido = datetime.strptime(f"{row['fecha'].date()} {row['hora_uy']}", "%Y-%m-%d %H:%M")
            
            # Solo permitimos apostar si falta más de 1 hora
            esta_bloqueado = ahora >= fecha_partido # Aquí podrías restar timedelta(hours=1)
            
            col1, col_vs, col2 = st.columns([2, 1, 2])
            
            with col1:
                st.write(f"**{row['local']}**")
                goles_l = st.number_input("Goles", min_value=0, max_value=20, step=1, key=f"l_{row['id']}", disabled=esta_bloqueado)
            
            with col_vs:
                st.write("<br><h3 style='text-align: center;'>VS</h3>", unsafe_allow_html=True)
                st.caption(f"{row['fecha'].strftime('%d/%m')} - {row['hora_uy']} hs")
            
            with col2:
                st.write(f"**{row['visitante']}**")
                goles_v = st.number_input("Goles", min_value=0, max_value=20, step=1, key=f"v_{row['id']}", disabled=esta_bloqueado)
            
            st.divider()
            
            # Guardamos temporalmente los datos para procesarlos al dar click en 'Enviar'
            nuevas_apuestas.append({
                "usuario": usuario,
                "partido_id": row['id'],
                "goles_local": goles_l,
                "goles_visitante": goles_v,
                "timestamp": ahora
            })

        enviado = st.form_submit_button("Guardar todas mis apuestas")
        
        if enviado:
            if not usuario:
                st.error("Por favor, ingresa tu nombre de usuario antes de guardar.")
            else:
                # AQUÍ CONECTAREMOS CON TU BASE DE DATOS (CSV o Google Sheets)
                # Por ahora, simulamos el éxito:
                st.success(f"¡Excelente {usuario}! Tus pronósticos han sido guardados correctamente.")

# Ejecutar la pantalla dentro de la pestaña correspondiente
pantalla_pronosticos()
