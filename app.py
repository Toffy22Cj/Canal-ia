import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests
import pandas as pd
import numpy as np

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
    
    /* Tarjeta de clima premium */
    .weather-card {
        background: rgba(30, 41, 59, 0.6);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<h1 class="dashboard-header">🌊 AlertaMarea x Canal IA</h1>', unsafe_allow_html=True)
st.markdown("**Sistema Inteligente de Detección Temprana y Priorización - Cartagena**")
st.write("")

def obtener_datos_clima(lat, lon):
    """Consulta la API pública de Open-Meteo para obtener datos completos del clima actual."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=precipitation,temperature_2m,relative_humidity_2m,wind_speed_10m"
        response = requests.get(url, timeout=3).json()
        current = response.get("current", {})
        return {
            "lluvia": current.get("precipitation", 0.0),
            "temp": current.get("temperature_2m", 30.2),
            "hum": current.get("relative_humidity_2m", 78),
            "viento": current.get("wind_speed_10m", 14.5)
        }
    except Exception:
        return {
            "lluvia": 0.0,
            "temp": 30.0,
            "hum": 70,
            "viento": 12.0
        }

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
    st.subheader("⛈️ Radar Meteorológico")

    # 3. Consultar datos meteorológicos en tiempo real
    clima = obtener_datos_clima(coords[0], coords[1])
    
    # Renderizar tarjeta de clima premium
    st.markdown(f"""
        <div class="weather-card">
            <h5 style="color: #6366f1; margin: 0 0 8px 0;">🌤️ Clima Real en {barrio_seleccionado.split(' ')[0]}</h5>
            <div style="font-size: 2.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 5px;">{clima['temp']}°C</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
                <span>💧 Humedad: {clima['hum']}%</span>
                <span>💨 Viento: {clima['viento']} km/h</span>
            </div>
            <div style="font-size: 0.85rem; color: #38bdf8; font-weight: bold;">🌧️ Precipitación actual: {clima['lluvia']} mm</div>
        </div>
    """, unsafe_allow_html=True)

    # Pre-configurar el deslizador según el clima real (redondeado a paso de 5)
    default_slider_val = min(100, max(0, int(round(clima['lluvia'] / 5.0) * 5)))

    # Deslizador dinámico de intensidad de lluvia
    intensidad_lluvia_mm = st.slider(
        "Intensidad de Lluvia (mm/h)", 
        min_value=0, 
        max_value=100, 
        value=default_slider_val, 
        step=5,
        help="Desliza para simular cómo evoluciona la tormenta sobre el sector."
    )

    # Clasificación del clima según el milimetraje
    if intensidad_lluvia_mm == 0:
        estado_clima = "Despejado"
    elif intensidad_lluvia_mm <= 20:
        estado_clima = "Llovizna"
    elif intensidad_lluvia_mm <= 50:
        estado_clima = "Lluvia Fuerte"
    else:
        estado_clima = "Tormenta Severa"

    st.caption(f"☁️ Pronóstico simulado: **{estado_clima}**")

# --- DISEÑO PRINCIPAL (2 Columnas) ---
col_mapa, col_resultados = st.columns([2, 1])
riesgo_pct = 0
resultado_procesado = False

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
        resultado_procesado = True

        st.metric(label="Obstrucción Canales", value=f"{nivel}")
        st.metric(
            label="Índice de Obstrucción",
            value=f"{riesgo_pct}%",
            delta=motivo,
            delta_color="inverse",
        )
        st.write(f"**Diagnóstico:** {justificacion}")

        # Datos simulados de reportes históricos por mes para vista dashboard B2G
        st.divider()
        st.caption("📊 Histórico de Reportes (Últimos 6 meses)")
        datos_historicos = pd.DataFrame(
            np.random.randint(10, 50, size=(6, 2)),
            columns=['Reportes Ciudadanos', 'Limpiezas Ejecutadas'],
            index=['Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago']
        )
        st.bar_chart(datos_historicos, color=["#6366f1", "#475569"])
    else:
        st.info("👈 Selecciona el barrio y sube una foto para analizar el riesgo.")

# --- MOTOR DE DECISIÓN MULTIVARIABLE DE ALERTAMAREA ---
# Ponderación: 60% importa cómo está el canal (IA), 40% importa cuánto llueve (Slider)
riesgo_base_ia = riesgo_pct / 100 
factor_lluvia = intensidad_lluvia_mm / 100

riesgo_total_calculado = (riesgo_base_ia * 0.6) + (factor_lluvia * 0.4)
riesgo_total_pct = int(riesgo_total_calculado * 100)

# Decisiones visuales basadas en el riesgo TOTAL
if riesgo_total_pct >= 75:
    color_marcador = "red"
    icono_marcador = "warning-sign"
    mensaje_alerta = f"🚨 ALERTA ROJA (Riesgo: {riesgo_total_pct}%): Evacuación o intervención inmediata en {barrio_seleccionado}. Canal obstruido en plena tormenta."
elif riesgo_total_pct >= 50:
    color_marcador = "orange"
    icono_marcador = "info-sign"
    mensaje_alerta = f"⚠️ ALERTA NARANJA (Riesgo: {riesgo_total_pct}%): Capacidad de drenaje comprometida en {barrio_seleccionado}. Monitoreo preventivo activo."
elif riesgo_total_pct >= 25:
    color_marcador = "blue"
    icono_marcador = "tint"
    mensaje_alerta = f"ℹ️ ALERTA AZUL (Riesgo: {riesgo_total_pct}%): Precipitaciones moderadas en {barrio_seleccionado}. Canal con flujo estable."
else:
    color_marcador = "green"
    icono_marcador = "ok-circle"
    mensaje_alerta = f"🟢 ZONA SEGURA (Riesgo: {riesgo_total_pct}%): Flujo de agua óptimo en {barrio_seleccionado}."

# --- COLUMNA IZQUIERDA: MAPA E INDICADORES ---
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
    mapa = folium.Map(
        location=coords, 
        zoom_start=14, 
        tiles="CartoDB dark_matter"
    )

    # 3. Marcador central del reporte
    folium.Marker(
        location=coords,
        popup=mensaje_alerta,
        tooltip=f"📍 Sector: {barrio_seleccionado}",
        icon=folium.Icon(color=color_marcador, icon=icono_marcador),
    ).add_to(mapa)

    # 4. Círculo de Afectación Dinámico
    # Si llueve, el radio de impacto de la inundación crece visualmente
    radio_impacto = 100 + (intensidad_lluvia_mm * 4) # Base 100m + crecimiento por lluvia
    
    folium.Circle(
        location=coords,
        radius=radio_impacto,
        color=color_marcador,
        fill=True,
        fill_opacity=0.3,
        tooltip=f"Radio de afectación estimado: {radio_impacto} metros"
    ).add_to(mapa)

    # 5. Renderizar el mapa
    st_folium(mapa, width=720, height=500)
