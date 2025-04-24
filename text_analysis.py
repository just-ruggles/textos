import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Texto Simple",
    page_icon="📊",
    layout="wide"
)

# Función de títulos en HTML con color
def titulo_rojo(texto):
    st.markdown(f"<h1 style='color:red'>{texto}</h1>", unsafe_allow_html=True)

def subtitulo_azul(texto):
    st.markdown(f"<h3 style='color:blue'>{texto}</h3>", unsafe_allow_html=True)

# Título principal
titulo_rojo("🕷 Analizador de Texto desarrollado por FNSM developers (Ganke)")

st.markdown("""
Esta aplicación utiliza TextBlob para realizar un análisis básico de texto:
- Análisis de sentimiento y subjetividad
- Extracción de palabras clave
- Análisis de frecuencia de palabras
""")

# Barra lateral
st.sidebar.title("Opciones")
modo = st.sidebar.selectbox(
    "Selecciona el modo de entrada:",
    ["Texto directo", "Archivo de texto"]
)

# Visualizaciones
def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)
    
    with col1:
        subtitulo_azul("Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("*Sentimiento:*")
        st.progress(sentimiento_norm)
        if resultados["sentimiento"] > 0.05:
            st.success(f"📈 Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"📉 Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"📊 Neutral ({resultados['sentimiento']:.2f})")
        
        st.write("*Subjetividad:*")
        st.progress(resultados["subjetividad"])
        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")

    with col2:
        subtitulo_azul("Palabras más frecuentes")
        if resultados["contador_palabras"]:
            palabras_top = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(palabras_top)

    subtitulo_azul("Texto Traducido")
    with st.expander("Ver traducción completa"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("*Texto Original (Español):*")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("*Texto Traducido (Inglés):*")
            st.text(resultados["texto_traducido"])

    subtitulo_azul("Frases detectadas")
    if resultados["frases"]:
        for i, frase_dict in enumerate(resultados["frases"][:10], 1):
            frase_original = frase_dict["original"]
            frase_traducida = frase_dict["traducido"]
            try:
                blob_frase = TextBlob(frase_traducida)
                sentimiento = blob_frase.sentiment.polarity
                emoji = "😊" if sentimiento > 0.05 else "😟" if sentimiento < -0.05 else "😐"
                st.write(f"{i}. {emoji} *Original:* \"{frase_original}\"")
                st.write(f"   *Traducción:* \"{frase_traducida}\" (Sentimiento: {sentimiento:.2f})")
                st.write("---")
            except:
                st.write(f"{i}. *Original:* \"{frase_original}\"")
                st.write(f"   *Traducción:* \"{frase_traducida}\"")
                st.write("---")
    else:
        st.write("No se detectaron frases.")

# Lógica principal
if modo == "Texto directo":
    subtitulo_azul("Ingresa tu texto para analizar")
    texto = st.text_area("", height=200, placeholder="Escribe o pega aquí el texto que deseas analizar...")
    if st.button("Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando texto..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("Por favor, ingresa algún texto para analizar.")

elif modo == "Archivo de texto":
    subtitulo_azul("Carga un archivo de texto")
    archivo = st.file_uploader("", type=["txt", "csv", "md"])
    if archivo is not None:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("Ver contenido del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))
            if st.button("Analizar archivo"):
                with st.spinner("Analizando archivo..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")

# Información adicional
with st.expander("📚 Información sobre el análisis"):
    st.markdown("""
    ### Sobre el análisis de texto
    
    - *Sentimiento*: Varía de -1 (muy negativo) a 1 (muy positivo)  
    - *Subjetividad*: Varía de 0 (muy objetivo) a 1 (muy subjetivo)  
    
    ### Requisitos mínimos
    
    Esta aplicación utiliza únicamente:
    
    - streamlit  
    - textblob  
    - pandas  
    """)
