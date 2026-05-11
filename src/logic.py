import pandas as pd

def calcular_ganadores_ventas(df_apuestas, resultado_real):
    """
    df_apuestas: DataFrame con columnas ['usuario', 'apuesta']
    resultado_real: float (ej: 101.60)
    """
    # Calculamos la diferencia absoluta con 2 decimales
    df_apuestas['error'] = abs(df_apuestas['apuesta'] - resultado_real).round(2)
    
    # Buscamos el error mínimo registrado
    error_minimo = df_apuestas['error'].min()
    
    # Identificamos ganadores (pueden ser varios)
    ganadores = df_apuestas[df_apuestas['error'] == error_minimo]
    
    return ganadores['usuario'].tolist(), error_minimo
