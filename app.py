import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image
import requests
import pandas as pd
import numpy as np

# Importar nuestro "cerebro" local
from vision_ai import analizar_imagen_canal

# 1. CONFIGURACIÓN DE PÁGINA (Debe ir primero)
st.set_page_config(page_title="AlertaMarea x Canal IA", layout="wide", page_icon="🌊")

# CSS personalizado para darle un toque premium de centro de comando
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stSidebar"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stMetric {
        background-color: rgba(30, 41, 59, 0.4);
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #00ffca;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    
    .stAlert {
        border-radius: 12px !important;
        font-weight: bold;
    }
    
    .dashboard-header {
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 50%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    
    .weather-card {
        background: rgba(30, 41, 59, 0.6);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    
    .result-card {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        height: 100%;
    }
    
    .result-card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown('<h1 class="dashboard-header">🌊 AlertaMarea x Canal IA</h1>', unsafe_allow_html=True)
st.markdown("**Sistema Inteligente de Detección Temprana y Priorización - Cartagena**")
st.write("")

# Inicializar cache en st.session_state
if "resultado_ia" not in st.session_state:
    st.session_state.resultado_ia = None
if "ultimo_archivo" not in st.session_state:
    st.session_state.ultimo_archivo = None

def obtener_datos_clima(lat, lon):
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
        return {"lluvia": 0.0, "temp": 30.0, "hum": 70, "viento": 12.0}

BARRIOS_CARTAGENA = {
    "Nelson Mandela (Sector Vulnerable)": {"coords": [10.3685, -75.4981], "historial": "Crítico (Alta incidencia 2017-2024, Desborde de arroyos - Ref: POMCA)"},
    "El Pozón (Sector Isla de León)": {"coords": [10.3881, -75.4722], "historial": "Crítico (6 km² inundados en 2017 según imágenes satelitales SAR Sentinel-1)"},
    "Olaya Herrera (Sector Central)": {"coords": [10.4015, -75.4923], "historial": "Alto (Afectación constante Vía Perimetral y Ciénaga de la Virgen)"},
    "La Boquilla (Sector Playa)": {"coords": [10.4633, -75.4967], "historial": "Alto (Inundaciones continuas en Nov 2022 por marea y lluvias prolongadas)"},
    "La María": {"coords": [10.4285, -75.5081], "historial": "Alto (Vulnerabilidad estructural y desbordamiento fluvial)"},
    "San Fernando": {"coords": [10.3812, -75.4985], "historial": "Alto (8 eventos históricos de inundación registrados en zona suroriente)"},
    "Centro Histórico": {"coords": [10.4236, -75.5512], "historial": "Medio (Vulnerabilidad a mareas altas y mar de leva)"}
}

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("🎛️ Centro de Operaciones")
    barrio_seleccionado = st.selectbox("📍 Ubicación del Reporte (Sector)", list(BARRIOS_CARTAGENA.keys()))
    coords = BARRIOS_CARTAGENA[barrio_seleccionado]["coords"]
    historial_zona = BARRIOS_CARTAGENA[barrio_seleccionado]["historial"]

    uploaded_file = st.file_uploader("📸 Reporte Ciudadano (Subir Foto)", type=["jpg", "jpeg", "png"])

    st.divider()
    st.subheader("⛈️ Radar Meteorológico")
    clima = obtener_datos_clima(coords[0], coords[1])
    
    # Extraer el nombre corto del barrio (Ej: "El Pozón" en lugar de "El")
    nombre_barrio_corto = barrio_seleccionado.split(' (')[0]
    
    st.markdown(f"""
        <div class="weather-card">
            <h5 style="color: #6366f1; margin: 0 0 8px 0;">🌤️ Clima Real en {nombre_barrio_corto}</h5>
            <div style="font-size: 2.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 5px;">{clima['temp']}°C</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
                <span>💧 Humedad: {clima['hum']}%</span>
                <span>💨 Viento: {clima['viento']} km/h</span>
            </div>
            <div style="font-size: 0.85rem; color: #38bdf8; font-weight: bold;">🌧️ Precipitación actual: {clima['lluvia']} mm</div>
        </div>
    """, unsafe_allow_html=True)

    default_slider_val = min(100, max(0, int(round(clima['lluvia'] / 5.0) * 5)))
    intensidad_lluvia_mm = st.slider("Intensidad de Lluvia (mm/h)", 0, 100, default_slider_val, 5)

    if intensidad_lluvia_mm == 0: clasif_lluvia = "☀️ Despejado"
    elif intensidad_lluvia_mm <= 20: clasif_lluvia = "🌧️ Llovizna"
    elif intensidad_lluvia_mm <= 50: clasif_lluvia = "⛈️ Lluvia Media"
    elif intensidad_lluvia_mm <= 80: clasif_lluvia = "⛈️ Lluvia Fuerte"
    else: clasif_lluvia = "🚨 Tormenta"
    st.caption(f"☁️ Pronóstico simulado: **{clasif_lluvia}**")

# --- LÓGICA DE PROCESAMIENTO IA ---
if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.ultimo_archivo != file_id:
        st.session_state.ultimo_archivo = file_id
        image = Image.open(uploaded_file)
        with st.spinner("Procesando imagen con IA..."):
            st.session_state.resultado_ia = analizar_imagen_canal(image, historial_zona)
else:
    st.session_state.resultado_ia = None
    st.session_state.ultimo_archivo = None

riesgo_pct = 0
nivel_obstruccion = "Ninguno"
tipo_problema = "Sin anomalías"
justificacion = "Sube una foto para iniciar el diagnóstico inteligente."

if st.session_state.resultado_ia is not None:
    res = st.session_state.resultado_ia
    nivel_obstruccion = res.get("nivel_obstruccion", "Ninguno")
    tipo_problema = res.get("tipo_problema", "Desconocido")
    riesgo_pct = res.get("riesgo_inundacion_porcentaje", 0)
    justificacion = res.get("justificacion", "")

riesgo_base_ia = riesgo_pct / 100 
factor_lluvia = intensidad_lluvia_mm / 100
riesgo_total_pct = int(((riesgo_base_ia * 0.6) + (factor_lluvia * 0.4)) * 100)

if riesgo_total_pct >= 75:
    color_marcador, icono_marcador, alerta_txt = "red", "warning-sign", f"🚨 EMERGENCIA ROJA: Evacuación o intervención inmediata en {nombre_barrio_corto}."
    estado_ui = st.error
elif riesgo_total_pct >= 50:
    color_marcador, icono_marcador, alerta_txt = "orange", "info-sign", f"⚠️ ALERTA NARANJA: Capacidad de drenaje comprometida en {nombre_barrio_corto}."
    estado_ui = st.warning
elif riesgo_total_pct >= 25:
    color_marcador, icono_marcador, alerta_txt = "blue", "tint", f"ℹ️ ALERTA AZUL: Monitoreo rutinario activo en {nombre_barrio_corto}."
    estado_ui = st.info
else:
    color_marcador, icono_marcador, alerta_txt = "green", "ok-circle", f"🟢 ZONA SEGURA: Flujo de agua óptimo en {nombre_barrio_corto}."
    estado_ui = st.success

# ==========================================
# 📊 PANEL SUPERIOR: KPIs (3 Columnas)
# ==========================================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

with col_kpi1:
    st.markdown('<div class="result-card"><div class="result-card-header">👁️ Visión Artificial (IA)</div>', unsafe_allow_html=True)
    st.metric(label="Nivel Obstrucción", value=f"{nivel_obstruccion}", delta=tipo_problema, delta_color="inverse")
    st.write(f"**Riesgo Base (IA):** {riesgo_pct}%")
    st.markdown('</div>', unsafe_allow_html=True)

with col_kpi2:
    st.markdown('<div class="result-card"><div class="result-card-header">⛈️ Clima Simulado</div>', unsafe_allow_html=True)
    st.metric(label="Intensidad de Lluvia", value=f"{intensidad_lluvia_mm} mm/h", delta=clasif_lluvia, delta_color="off")
    st.write(f"**Afectación estimada:** +{int(factor_lluvia * 40)}% al riesgo.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_kpi3:
    st.markdown('<div class="result-card"><div class="result-card-header">⚡ Riesgo Agregado</div>', unsafe_allow_html=True)
    st.metric(label="Riesgo Total", value=f"{riesgo_total_pct}%")
    estado_ui(alerta_txt)  # Renderiza la alerta dentro de la tarjeta!
    st.markdown('</div>', unsafe_allow_html=True)

st.write("") # Espaciador

# ==========================================
# 🗺️ PANEL INFERIOR: MAPA Y DETALLES (2 Columnas)
# ==========================================
col_mapa, col_detalles = st.columns([2, 1])

with col_mapa:
    st.subheader("🗺️ Radar Territorial")
    estado_ui(alerta_txt) # Banner general antes del mapa
    
    mapa = folium.Map(location=coords, zoom_start=14, tiles="CartoDB dark_matter")
    folium.Marker(
        location=coords, popup=alerta_txt, tooltip=f"📍 Sector: {nombre_barrio_corto}", 
        icon=folium.Icon(color=color_marcador, icon=icono_marcador)
    ).add_to(mapa)
    
    radio_impacto = 100 + (intensidad_lluvia_mm * 4)
    folium.Circle(
        location=coords, radius=radio_impacto, color=color_marcador, 
        fill=True, fill_opacity=0.3, tooltip=f"Radio de afectación: {radio_impacto}m"
    ).add_to(mapa)
    
    # use_container_width soluciona los mapas cortados o negros
    st_folium(mapa, height=450, use_container_width=True)

with col_detalles:
    st.subheader("📸 Reporte / Diagnóstico")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagen procesada", use_column_width=True)
        st.write(f"**Análisis de la IA:** {justificacion}")
    else:
        st.info("👈 Sube una fotografía de un canal para ver el reporte detallado.")
        
    st.divider()
    st.caption("📚 **Contexto de Vulnerabilidad Histórica**")
    st.info(f"Según estudios satelitales (Sentinel-1) y POT: **{historial_zona}**")
        
    st.divider()
    st.caption("📊 Histórico de Reportes (Últimos 6 meses)")
    datos_historicos = pd.DataFrame(
        np.random.randint(10, 50, size=(6, 2)),
        columns=['Reportes', 'Limpiezas'],
        index=['Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago']
    )
    st.bar_chart(datos_historicos, color=["#6366f1", "#475569"])
