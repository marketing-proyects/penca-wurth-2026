import streamlit as st
import pandas as pd
from src.styles import inject_custom_css
from src.logic import calcular_ganadores_ventas

inject_custom_css()

# Simulación de base de datos de puntos
# En producción, esto se leería de st.connection("gsheets")
def mostrar_ranking():
    st.header("🥇 Ranking de la Penca Würth")
    
    # Datos de ejemplo
    data = {
        'Usuario': ['Pedrito', 'Juancito', 'Federico', 'María'],
        'Puntos Fútbol': [12, 15, 10, 14],
        'Puntos KPI Ventas': [0, 0, 10, 0], # Federico ganó el día especial
    }
    
    df = pd.DataFrame(data)
    df['Total'] = df['Puntos Fútbol'] + df['Puntos KPI Ventas']
    df = df.sort_values(by='Total', ascending=False)
    
    # Mostrar podio con métricas destacadas
    col1, col2, col3 = st.columns(3)
    col1.metric("1er Puesto", df.iloc[0]['Usuario'], f"{df.iloc[0]['Total']} pts")
    col2.metric("2do Puesto", df.iloc[1]['Usuario'], f"{df.iloc[1]['Total']} pts")
    
    st.table(df)

# Ejecución de la pestaña de ranking
mostrar_ranking()
