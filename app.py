import streamlit as st
from src.styles import inject_custom_css # Función para el look & feel

st.set_page_config(page_title="Penca Würth 2026", layout="wide")
# inject_custom_css() # Aquí meteríamos el CSS del Rojo Würth

st.title("🏆 Penca Mundialista & Negocios 2026")

tabs = st.tabs(["⚽ Pronósticos", "📊 Desafío Ventas", "🥇 Ranking General"])

with tabs[1]:
    st.header("🎯 El Día Especial: Objetivo de Ventas")
    st.info("Ingresa tu apuesta de cumplimiento para el día de ventas especial.")
    
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Tu Nombre/Vendedor")
        apuesta_v = st.number_input("Tu apuesta (%)", min_value=0.00, max_value=200.00, step=0.01, format="%.2f")
        
        if st.button("Registrar Apuesta de Ventas"):
            # Lógica para guardar en data/ventas_kpi.csv o Google Sheets
            st.success(f"¡Registrado! Apostaste un {apuesta_v:.2f}%")

with tabs[2]:
    st.header("🏆 Tabla de Posiciones")
    # Aquí leerías los CSVs y mostrarías el DataFrame final ordenado por puntos
