import streamlit as st
import pandas as pd
import xgboost as xgb
import pickle
import Funciones as f

# Tus funciones extraer_caracteristicas y preprocesar_caracteristicas aquí

# Carga el modelo entrenado previamente
with open('C:\Users\Carre\OneDrive\Escritorio\Proyecto_Machine_Learning\-Fishing-Phishing-\src\model\Fishing_Phishing.pkl', 'rb') as modelo:
    modelo_xgb = pickle.load(modelo)

# Función para predecir si una URL es phishing o legítima
def predecir_phishing(url):
    fila = f.extraccion_parametros(url)
    fila_preprocesada = f.preprocesar_fila(fila)
    df_fila = pd.DataFrame([fila_preprocesada])
    prediccion = modelo_xgb.predict(df_fila)
    return prediccion[0]

# Título de la aplicación
st.title("Fishing Phishing")

# Solicita al usuario que ingrese una URL
url = st.text_input("Ingrese la URL a clasificar:")

# Botón para realizar la clasificación
if st.button("Clasificar"):
    # Verifica si el usuario ha ingresado una URL
    if url:
        # Realiza la predicción
        resultado = predecir_phishing(url)

        # Muestra el resultado
        if resultado == 1:
            st.warning("La URL es phishing")
        else:
            st.success("La URL es legítima")
    else:
        st.error("Por favor, ha habido un error, ingrese una URL:")
