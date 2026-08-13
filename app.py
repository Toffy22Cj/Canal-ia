import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
from vision_ai import analizar_imagen_canal

# 1. Configurar la página de Streamlit
st.set_page_config(
    layout="wide",
    page_title="AlertaMarea x Canal IA",
    page_icon="🌊"
)

# Inyección de CSS Premium para estilo futurista, moderno y limpio
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        /* Tipografía global */
        html, body, [data-testid="stSidebar"] {
            font-family: 'Outfit', sans-serif;
        }
        
        /* Título principal de la barra lateral */
        .sidebar-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #6366f1;
            margin-bottom: 20px;
        }
        
        /* Banner de cabecera con gradiente premium */
        .premium-header-container {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
            border-radius: 16px;
            padding: 25px 30px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .premium-title {
            background: linear-gradient(90deg, #3b82f6 0%, #6366f1 50%, #a855f7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            font-size: 2.8rem;
            margin: 0;
            letter-spacing: -1px;
        }
        
        .premium-subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-top: 5px;
            margin-bottom: 0;
            font-weight: 300;
        }
        
        /* Tarjetas de resultados y métricas */
        .result-card {
            background: rgba(30, 41, 59, 0.5);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            margin-top: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }
        
        .result-card-header {
            font-size: 1.25rem;
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 8px;
        }
        
        /* Personalización de métricas de Streamlit */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 700;
            color: #f8fafc;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #94a3b8;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# Cabecera principal
st.markdown("""
    <div class="premium-header-container">
        <h1 class="premium-title">AlertaMarea x Canal IA</h1>
        <p class="premium-subtitle">Sistema Inteligente de Monitoreo de Canales y Prevención de Inundaciones | Cartagena de Indias</p>
    </div>
""", unsafe_allow_html=True)

# 2. Configurar Barra Lateral (Sidebar)
with st.sidebar:
    st.markdown('<div class="sidebar-title">🌐 Panel de Control</div>', unsafe_allow_html=True)
    
    st.write("---")
    
    # Subida de imagen
    uploaded_file = st.file_uploader(
        "Subir reporte ciudadano de canal u obstrucción:",
        type=["jpg", "png", "jpeg"]
    )
    
    st.write("---")
    
    # Checkbox para simulación de lluvia
    simular_lluvia = st.checkbox("🌧️ Simular Lluvia Fuerte", value=False)
    
    st.write("---")
    st.info("ℹ️ AlertaMarea utiliza Gemini 1.5 Flash para detectar obstrucciones físicas en la infraestructura de drenaje de Cartagena en tiempo real.")

# 3. Inicializar variables de estado del análisis
nivel_obstruccion = "Ninguno"
tipo_problema = "Ninguno"
riesgo_inundacion_porcentaje = 0
justificacion = "No se ha cargado ningún reporte para analizar."
analisis_exitoso = False
es_punto_critico = False
riesgo_extremo = False

# Crear las dos columnas principales
col1, col2 = st.columns([2, 1])

# 4. Lógica de la Aplicación (Procesamiento de IA)
if uploaded_file is not None:
    try:
        # Abrir la imagen con PIL
        imagen_pil = Image.open(uploaded_file)
        
        # Ejecutar análisis con un spinner
        with st.spinner("Analizando reporte ciudadano con Gemini IA..."):
            resultado = analizar_imagen_canal(imagen_pil)
            
            # Extraer resultados devueltos por la IA
            nivel_obstruccion = resultado.get("nivel_obstruccion", "Desconocido")
            tipo_problema = resultado.get("tipo_problema", "Desconocido")
            riesgo_inundacion_porcentaje = int(resultado.get("riesgo_inundacion_porcentaje", 0))
            justificacion = resultado.get("justificacion", "")
            analisis_exitoso = True
            
            # Evaluar si es un punto crítico
            # Condición: Obstrucción Alta o riesgo de inundación > 60%
            if nivel_obstruccion == "Alto" or riesgo_inundacion_porcentaje > 60:
                es_punto_critico = True
                
            # Riesgo es extremo si hay lluvia fuerte simulada Y es un punto crítico
            if simular_lluvia and es_punto_critico:
                riesgo_extremo = True
                
    except Exception as e:
        st.error(f"Error al analizar la imagen: {e}")

# 5. Configuración del Mapa (Columna Izquierda)
with col1:
    st.markdown('<div class="result-card-header">📍 Mapa de Riesgo en Cartagena</div>', unsafe_allow_html=True)
    
    # Determinar color de marcador e icono según estado
    if not analisis_exitoso:
        color_marcador = "blue"
        tooltip_txt = "Cartagena - Sin reportes activos"
        popup_txt = "Sube una imagen para ver el riesgo localizado"
    elif riesgo_extremo:
        color_marcador = "red"
        tooltip_txt = "🚨 RIESGO EXTREMO"
        popup_txt = f"Obstrucción: {nivel_obstruccion} | Lluvia: SI"
    elif es_punto_critico:
        color_marcador = "orange"
        tooltip_txt = "⚠️ RIESGO ALTO (Punto Crítico)"
        popup_txt = f"Obstrucción: {nivel_obstruccion} | Lluvia: NO"
    else:
        color_marcador = "green"
        tooltip_txt = "✅ ZONA SEGURA"
        popup_txt = f"Obstrucción: {nivel_obstruccion} | Sin riesgo crítico"
        
    # Inicializar mapa de Folium centrado en Cartagena
    mapa = folium.Map(
        location=[10.3997, -75.4795], 
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Añadir marcador de canal representativo (Lat 10.4050, Lon -75.4900)
    folium.Marker(
        location=[10.4050, -75.4900],
        popup=popup_txt,
        tooltip=tooltip_txt,
        icon=folium.Icon(color=color_marcador, icon="cloud")
    ).add_to(mapa)
    
    # Renderizar mapa en Streamlit
    st_folium(mapa, width=750, height=500)

# 6. Mostrar Resultados (Columna Derecha)
with col2:
    if uploaded_file is not None:
        # Mostrar imagen subida
        st.markdown('<div class="result-card-header">📸 Imagen del Reporte</div>', unsafe_allow_html=True)
        st.image(imagen_pil, width="stretch")
        
        # Mostrar panel de análisis e indicadores
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-card-header">📊 Diagnóstico del Canal</div>', unsafe_allow_html=True)
        
        # Mostrar alertas principales según estado
        if riesgo_extremo:
            st.error("🚨 ALERTA ROJA: Riesgo inminente de inundación por canal obstruido + lluvia.")
        elif es_punto_critico:
            st.warning("⚠️ ALERTA NARANJA: Punto crítico detectado por alto nivel de obstrucción.")
        else:
            st.success("✅ Zona segura.")
            
        # Métricas principales
        metric_col1, metric_col2 = st.columns(2)
        with metric_col1:
            st.metric(label="Nivel de Obstrucción", value=nivel_obstruccion)
        with metric_col2:
            st.metric(label="Tipo de Problema", value=tipo_problema)
            
        st.metric(label="Riesgo de Inundación", value=f"{riesgo_inundacion_porcentaje}%")
        
        # Justificación de la IA
        st.markdown("##### 📝 Justificación del Análisis:")
        st.write(justificacion)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Estado de espera / Bienvenida
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-card-header">📥 Esperando Reporte Ciudadano</div>', unsafe_allow_html=True)
        st.write("Sube una foto de un canal de agua, alcantarilla o vía inundada en el **Panel de Control** a la izquierda para iniciar el diagnóstico con Inteligencia Artificial.")
        st.write("Puedes simular también lluvias fuertes en la zona para ver el comportamiento del sistema de alertas en tiempo real.")
        st.markdown('</div>', unsafe_allow_html=True)
