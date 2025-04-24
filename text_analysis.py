import streamlit as st
import pandas as pd
from textblob import TextBlob
import re
from googletrans import Translator

# Configuración de la página
st.set_page_config(
    page_title="📊 Analizador de Texto Simple",
    page_icon="🕷️",
    layout="wide"
)

# Título principal
st.title("🕷️ Analizador de Texto por FNSM developers (Ganke)")
st.markdown("""
Esta aplicación realiza análisis básicos de texto utilizando **TextBlob**:
- Análisis de **sentimiento** y **subjetividad**
- Extracción de frases
- Palabras más frecuentes
""")

# Opciones en la barra lateral
st.sidebar.header("⚙️ Opciones")
modo = st.sidebar.selectbox("Selecciona el modo de entrada:", ["Texto directo", "Archivo de texto"])

# Lista básica de stopwords en español e inglés
stop_words = set([...])  # <-- mantén la lista larga de palabras vacías aquí

def contar_palabras(texto):
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_filtradas = [p for p in palabras if p not in stop_words and len(p) > 2]
    contador = {}
    for palabra in palabras_filtradas:
        contador[palabra] = contador.get(palabra, 0) + 1
    contador_ordenado = dict(sorted(contador.items(), key=lambda x: x[1], reverse=True))
    return contador_ordenado, palabras_filtradas

# Inicializar traductor
translator = Translator()

def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto, src='es', dest='en')
        return traduccion.text
    except Exception as e:
        st.error(f"❌ Error al traducir: {e}")
        return texto

def procesar_texto(texto):
    texto_original = texto
    texto_ingles = traducir_texto(texto)
    blob = TextBlob(texto_ingles)
    sentimiento = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    frases_originales = [f.strip() for f in re.split(r'[.!?]+', texto_original) if f.strip()]
    frases_traducidas = [f.strip() for f in re.split(r'[.!?]+', texto_ingles) if f.strip()]
    frases_combinadas = [{
        "original": frases_originales[i],
        "traducido": frases_traducidas[i]
    } for i in range(min(len(frases_originales), len(frases_traducidas)))]
    contador_palabras, palabras = contar_palabras(texto_ingles)
    
    return {
        "sentimiento": sentimiento,
        "subjetividad": subjetividad,
        "frases": frases_combinadas,
        "contador_palabras": contador_palabras,
        "palabras": palabras,
        "texto_original": texto_original,
        "texto_traducido": texto_ingles
    }

def crear_visualizaciones(resultados):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Análisis de Sentimiento y Subjetividad")
        sentimiento_norm = (resultados["sentimiento"] + 1) / 2
        st.write("**Sentimiento:**")
        st.progress(sentimiento_norm)

        if resultados["sentimiento"] > 0.05:
            st.success(f"✅ Positivo ({resultados['sentimiento']:.2f})")
        elif resultados["sentimiento"] < -0.05:
            st.error(f"❌ Negativo ({resultados['sentimiento']:.2f})")
        else:
            st.info(f"ℹ️ Neutral ({resultados['sentimiento']:.2f})")

        st.write("**Subjetividad:**")
        st.progress(resultados["subjetividad"])

        if resultados["subjetividad"] > 0.5:
            st.warning(f"💭 Alta subjetividad ({resultados['subjetividad']:.2f})")
        else:
            st.info(f"📋 Baja subjetividad ({resultados['subjetividad']:.2f})")

    with col2:
        st.subheader("🔠 Palabras más frecuentes")
        if resultados["contador_palabras"]:
            top = dict(list(resultados["contador_palabras"].items())[:10])
            st.bar_chart(top)

    st.subheader("🌐 Traducción del texto")
    with st.expander("Mostrar traducción"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Texto Original (Español):**")
            st.text(resultados["texto_original"])
        with col2:
            st.markdown("**Texto Traducido (Inglés):**")
            st.text(resultados["texto_traducido"])

    st.subheader("🔍 Frases detectadas")
    if resultados["frases"]:
        for i, f in enumerate(resultados["frases"][:10], 1):
            blob_frase = TextBlob(f["traducido"])
            pol = blob_frase.sentiment.polarity
            emoji = "😊" if pol > 0.05 else "😟" if pol < -0.05 else "😐"
            st.write(f"{i}. {emoji} **Original:** *\"{f['original']}\"*")
            st.write(f"   **Traducción:** *\"{f['traducido']}\"* (Sentimiento: {pol:.2f})")
            st.markdown("---")
    else:
        st.info("No se detectaron frases.")

# Entrada de texto o archivo
if modo == "Texto directo":
    st.subheader("✍️ Ingresa tu texto")
    texto = st.text_area("Texto a analizar:", height=200, placeholder="Escribe aquí tu texto...")

    if st.button("🚀 Analizar texto"):
        if texto.strip():
            with st.spinner("Analizando..."):
                resultados = procesar_texto(texto)
                crear_visualizaciones(resultados)
        else:
            st.warning("⚠️ Por favor, ingresa algún texto.")

elif modo == "Archivo de texto":
    st.subheader("📂 Carga un archivo")
    archivo = st.file_uploader("Selecciona un archivo:", type=["txt", "csv", "md"])

    if archivo:
        try:
            contenido = archivo.getvalue().decode("utf-8")
            with st.expander("📄 Ver contenido del archivo"):
                st.text(contenido[:1000] + ("..." if len(contenido) > 1000 else ""))

            if st.button("🚀 Analizar archivo"):
                with st.spinner("Analizando..."):
                    resultados = procesar_texto(contenido)
                    crear_visualizaciones(resultados)
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")

# Información adicional
with st.expander("ℹ️ Información sobre el análisis"):
    st.markdown("""
    ### 📊 Acerca del análisis
    
    - **Sentimiento**: Rango de -1 (muy negativo) a 1 (muy positivo).
    - **Subjetividad**: Rango de 0 (objetivo) a 1 (subjetivo).
    
    ### 🧪 Requisitos mínimos
    
    Este proyecto utiliza:
    ```bash
    pip install streamlit textblob pandas googletrans==4.0.0-rc1
    ```
    """)
