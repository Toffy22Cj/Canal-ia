import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests

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

def obtener_precipitacion_real(lat, lon):
    """Consulta la API pública de Open-Meteo para obtener la lluvia actual en mm."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=precipitation"
        response = requests.get(url, timeout=3).json()
        precipitacion = response.get("current", {}).get("precipitation", 0.0)
        return precipitacion
    except Exception:
        return 0.0  # Fallback seguro si no hay internet o falla la API

# Diccionario con puntos críticos de Cartagena (Latitud, Longitud)
BARRIOS_CARTAGENA = {
    "El Pozón (Sector Isla de León)": [10.3881, -75.4722],
    "Olaya Herrera (Sector Central)": [10.4015, -75.4923],
    "La María": [10.4285, -75.5081],
    "San Fernando": [10.3812, -75.4985],
    "Centro Histórico": [10.4236, -75.5512]
}

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("🎛️ Centro de Operaciones")

    # 1. Selector de Ubicación / Barrio
    barrio_seleccionado = st.selectbox(
        "📍 Ubicación del Reporte (Sector)", 
        list(BARRIOS_CARTAGENA.keys())
    )
    coords = BARRIOS_CARTAGENA[barrio_seleccionado]

    # 2. Cargar Foto
    uploaded_file = st.file_uploader(
        "📸 Reporte Ciudadano (Subir Foto)", 
        type=["jpg", "jpeg", "png"]
    )

    st.divider()
    st.subheader("⛈️ Monitoreo Climatológico")

    # 3. Lluvia Real vs Simulación
    lluvia_real_mm = obtener_precipitacion_real(coords[0], coords[1])
    st.caption(f"流️ Precipitación actual en API: **{lluvia_real_mm} mm**")

    # Checkbox para forzar lluvia en la demo si no está lloviendo afuera
    simular_lluvia = st.checkbox(
        "⚡ Forzar Simulación de Tormenta", 
        value=(lluvia_real_mm > 1.0)
    )

# Lluvia activa si la API dice que llueve O si activaste la simulación manual
hay_lluvia_activa = (lluvia_real_mm > 1.0) or simular_lluvia

# --- DISEÑO PRINCIPAL (2 Columnas) ---
col_mapa, col_resultados = st.columns([2, 1])
riesgo_alto_ia = False

# --- COLUMNA DERECHA: PROCESAMIENTO DE IA ---
with col_resultados:
    st.subheader("🤖 Análisis de IA")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Reporte en {barrio_seleccionado}", width="stretch")

        with st.spinner("Procesando imagen con IA..."):
            resultado = analizar_imagen_canal(image)

        nivel = resultado.get("nivel_obstruccion", "Desconocido")
        motivo = resultado.get("tipo_problema", "Desconocido")
        riesgo_pct = resultado.get("riesgo_inundacion_porcentaje", 0)
        justificacion = resultado.get("justificacion", "")

        st.metric(label="Obstrucción Canales", value=f"{nivel}")
        st.metric(
            label="Índice de Obstrucción",
            value=f"{riesgo_pct}%",
            delta=motivo,
            delta_color="inverse",
        )
        st.write(f"**Diagnóstico:** {justificacion}")

        if nivel in ["Alto", "Medio"] or riesgo_pct > 60:
            riesgo_alto_ia = True
    else:
        st.info("👈 Selecciona el barrio y sube una foto para analizar el riesgo.")

# --- MOTOR DE DECISIÓN DE ALERTAMAREA ---
if riesgo_alto_ia and hay_lluvia_activa:
    color_marcador = "red"
    icono_marcador = "warning-sign"
    mensaje_alerta = f"🚨 ALERTA ROJA en {barrio_seleccionado}: Obstrucción severa + precipitaciones. Riesgo inminente de inundación."
elif riesgo_alto_ia and not hay_lluvia_activa:
    color_marcador = "orange"
    icono_marcador = "info-sign"
    mensaje_alerta = f"⚠️ ALERTA NARANJA en {barrio_seleccionado}: Obstrucción en canal detectada. Programar limpieza antes de lluvias."
elif hay_lluvia_activa and not riesgo_alto_ia:
    color_marcador = "blue"
    icono_marcador = "tint"
    mensaje_alerta = f"ℹ️ ALERTA AZUL en {barrio_seleccionado}: Lluvia en curso, pero el canal está despejado."
else:
    color_marcador = "green"
    icono_marcador = "ok-circle"
    mensaje_alerta = f"🟢 ZONA SEGURA: Sin novedades en {barrio_seleccionado}."

# --- MAPA ---
with col_mapa:
    if color_marcador == "red":
        st.error(mensaje_alerta)
    elif color_marcador == "orange":
        st.warning(mensaje_alerta)
    elif color_marcador == "blue":
        st.info(mensaje_alerta)
    else:
        st.success(mensaje_alerta)

    # El mapa se centra exactamente en las coordenadas del barrio seleccionado
    mapa = folium.Map(
        location=coords, 
        zoom_start=14, 
        tiles="CartoDB dark_matter"
    )

    folium.Marker(
        location=coords,
        popup=mensaje_alerta,
        tooltip=f"📍 Sector: {barrio_seleccionado}",
        icon=folium.Icon(color=color_marcador, icon=icono_marcador),
    ).add_to(mapa)

    st_folium(mapa, width=720, height=500)
