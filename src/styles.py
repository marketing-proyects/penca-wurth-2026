import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Fondo y tipografía general */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Encabezados con estilo Würth */
        h1, h2, h3 {
            color: #CC0000 !important;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            text-transform: uppercase;
            font-weight: 800;
        }

        /* Personalización de botones */
        .stButton>button {
            background-color: #CC0000;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #000000;
            color: white;
        }

        /* Métricas (KPIs) en rojo */
        [data-testid="stMetricValue"] {
            color: #CC0000;
        }

        /* Tablas de resultados */
        .styled-table {
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            min-width: 400px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
        }
        </style>
    """, unsafe_allow_html=True)
