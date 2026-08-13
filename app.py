import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image

# Importar nuestro "cerebro" local que acabas de crear
from vision_ai import analizar_imagen_canal

# 1. CONFIGURACIÓN DE PÁGINA (Debe ir primero)
st.set_page_config(page_title="AlertaMarea x Canal IA", layout="wide", page_icon="🌊")

# CSS personalizado para darle un toque premium de centro de comando
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Tipografía global */
    html, body, [data-testid="stSidebar"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Estilo de métricas */
    .stMetric {
        background-color: #1a1f2c;
        padding: 18px;
        border-radius: 12px;
        border-left: 5px solid #00ffca;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        margin-bottom: 15px;
    }
    
    /* Alertas con bordes redondeados */
    .stAlert {
        border-radius: 12px !important;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    /* Cabecera con degradado de colores */
    .dashboard-header {
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<h1 class="dashboard-header">🌊 AlertaMarea x Canal IA</h1>', unsafe_allow_html=True)
st.markdown("**Sistema Inteligente de Detección Temprana y Priorización - Cartagena**")
st.write("")

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("🎛️ Centro de Operaciones")
    st.info("1. Sube una foto de un canal.\n2. La IA lo evalúa.\n3. Simula lluvia para ver la alerta combinada.")
    
    uploaded_file = st.file_uploader("📸 Reporte Ciudadano (Subir Foto)", type=["jpg", "jpeg", "png"])
    
    st.divider()
    st.subheader("⛈️ Variables Meteorológicas")
    simular_lluvia = st.checkbox("Simular Tormenta (Radar)", value=False)
    
    st.divider()
    st.caption("Prototipo B2G (Business-to-Government) - Hackathon 2026")

# --- DISEÑO PRINCIPAL (2 Columnas) ---
col_mapa, col_resultados = st.columns([2, 1])

# Variables por defecto
riesgo_alto_ia = False
color_marcador = "green"
mensaje_alerta = "🟢 ZONA SEGURA: Canales fluyendo. Sin reportes críticos en el perímetro."
icono_marcador = "ok-circle"

# --- COLUMNA DERECHA: PROCESAMIENTO DE IA ---
with col_resultados:
    st.subheader("🤖 Análisis de IA")
    
    if uploaded_file is not None:
        # 1. Mostrar foto
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen recibida", width="stretch")
        
        # 2. Procesar con tu modelo local (Ollama / OpenRouter en cascada)
        with st.spinner("Procesando imagen con IA Visión..."):
            resultado = analizar_imagen_canal(image)
            
        # 3. Extraer datos del JSON
        nivel = resultado.get("nivel_obstruccion", "Desconocido")
        motivo = resultado.get("tipo_problema", "Desconocido")
        riesgo_pct = resultado.get("riesgo_inundacion_porcentaje", 0)
        justificacion = resultado.get("justificacion", "")
        
        # 4. Mostrar métricas en la interfaz
        st.metric(label="Nivel de Obstrucción Detectado", value=f"{nivel}")
        st.metric(label="Riesgo Estructural", value=f"{riesgo_pct}%", delta=motivo, delta_color="inverse")
        st.write(f"**Decisión del Modelo:** {justificacion}")
        
        # 5. Regla de negocio
        if nivel in ["Alto", "Medio"] or riesgo_pct > 60:
            riesgo_alto_ia = True
            
    else:
        st.warning("👈 Sube un reporte fotográfico en el panel izquierdo para iniciar.")

# --- COLUMNA IZQUIERDA: MOTOR DE DECISIÓN Y MAPA ---
# Aquí combinamos "Canal IA" (La foto) con "AlertaMarea" (El Clima)
if riesgo_alto_ia and simular_lluvia:
    color_marcador = "red"
    icono_marcador = "warning-sign"
    mensaje_alerta = "🚨 ALERTA ROJA INMINENTE: Obstrucción crítica confirmada + Precipitaciones altas. Enviar cuadrilla de emergencia prioridad 1 y desviar tráfico."
elif riesgo_alto_ia and not simular_lluvia:
    color_marcador = "orange"
    icono_marcador = "info-sign"
    mensaje_alerta = "⚠️ ALERTA NARANJA: Canal taponado. Alto riesgo de inundación si inician lluvias. Programar limpieza preventiva."
elif simular_lluvia and not riesgo_alto_ia:
    color_marcador = "blue"
    icono_marcador = "tint"
    mensaje_alerta = "ℹ️ ALERTA AZUL: Fuertes lluvias. Canales despejados. Monitoreando capacidad de drenaje."

with col_mapa:
    # 1. Imprimir la barra de estado
    if color_marcador == "red":
        st.error(mensaje_alerta)
    elif color_marcador == "orange":
        st.warning(mensaje_alerta)
    elif color_marcador == "blue":
        st.info(mensaje_alerta)
    else:
        st.success(mensaje_alerta)
        
    st.subheader("🗺️ Radar Territorial Inteligente")
    
    # 2. Configurar el mapa interactivo
    # Latitud y longitud de Cartagena (centrado en la ciudad) con tiles dark_matter
    mapa = folium.Map(location=[10.3997, -75.4795], zoom_start=13, tiles="CartoDB dark_matter")
    
    # 3. Poner el pin dinámico (simulando que el reporte es en un barrio vulnerable)
    folium.Marker(
        location=[10.4050, -75.4900], # Coordenadas arbitrarias simulando un punto crítico
        popup=f"Estado: {mensaje_alerta}",
        tooltip="📍 Reporte: Canal Sector 4",
        icon=folium.Icon(color=color_marcador, icon=icono_marcador)
    ).add_to(mapa)
    
    # 4. Renderizar el mapa en la app
    st_folium(mapa, width=720, height=500)
