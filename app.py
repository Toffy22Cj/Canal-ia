import streamlit as st
import folium
from streamlit_folium import st_folium
from PIL import Image, ExifTags
import time
import requests
import pandas as pd
import numpy as np

# Importar nuestro "cerebro" local
from vision_ai import analizar_imagen_canal

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="AlertaMarea x Canal IA", layout="wide", page_icon="🌊")

# CSS personalizado (Estilo Dark GIS / MIDAS)
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
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
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        margin-bottom: 15px;
        margin-top: 15px;
    }
    
    .result-card {
        background: rgba(30, 41, 59, 0.4);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        margin-bottom: 15px;
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

# Inicializar estados de la sesión
if "resultado_ia" not in st.session_state:
    st.session_state.resultado_ia = None
if "ultimo_archivo" not in st.session_state:
    st.session_state.ultimo_archivo = None
if "barrio_seleccionado" not in st.session_state:
    st.session_state.barrio_seleccionado = "Nelson Mandela / San Fernando (Localidad 3)"
if "upload_count" not in st.session_state:
    st.session_state.upload_count = 0
if "last_upload_time" not in st.session_state:
    st.session_state.last_upload_time = 0
if "fecha_captura" not in st.session_state:
    st.session_state.fecha_captura = "Desconocida"

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

# --- BASE DE DATOS TERRITORIAL (Respaldada por POT, IDEAM y Análisis SAR) ---
BARRIOS_CARTAGENA = {
    "Olaya Herrera (Localidad 2)": {
        "coords": [10.4015, -75.4923], 
        "historial": "Crítico. Inundaciones asociadas a lluvias que incrementan el nivel de la Ciénaga de la Virgen (POT)."
    },
    "Nelson Mandela / San Fernando (Localidad 3)": {
        "coords": [10.3812, -75.4985], 
        "historial": "Alto. Inundaciones recurrentes asociadas al desbordamiento de arroyos por fuertes lluvias (Cartografía Social POT)."
    },
    "Torices / San Pedro (Localidad 1)": {
        "coords": [10.4300, -75.5300],
        "historial": "Medio-Alto. Inundaciones frecuentes debido a problemas con la red de alcantarillado y lluvias (POT)."
    },
    "Zaragocilla / La Popa": {
        "coords": [10.4025, -75.5043],
        "historial": "Riesgo Mixto. Alta vulnerabilidad a eventos de remoción en masa (deslizamientos) e inundaciones."
    },
    "Aeropuerto / Crespo": {
        "coords": [10.4435, -75.5160],
        "historial": "Crítico Estratégico. Zona recurrente de inundación detectada por radares Sentinel-1, afectando infraestructura de movilidad."
    },
    "Centro / Getsemaní": {
        "coords": [10.4236, -75.5512],
        "historial": "Alto. Riesgo de inundación en el sistema de caños y lagos (Tr 25-100 años)."
    }
}

st.markdown('<h2 class="dashboard-header">🌊 MIDAS x AlertaMarea (Visor Territorial)</h2>', unsafe_allow_html=True)
st.write("")

# --- INTERFAZ TIPO MIDAS (2 COLUMNAS) ---
# Columna izquierda: Panel de Navegación y Estadísticas (1.2)
# Columna derecha: Mapa Interactivo (2.8)
col_panel, col_mapa = st.columns([1.2, 2.8])

with col_panel:
    # 1. Buscador de Territorios
    lista_barrios = list(BARRIOS_CARTAGENA.keys())
    try:
        index_barrio = lista_barrios.index(st.session_state.barrio_seleccionado)
    except ValueError:
        index_barrio = 0
        
    nuevo_barrio = st.selectbox("🔍 Territorio / Capa de Análisis", lista_barrios, index=index_barrio)
    if nuevo_barrio != st.session_state.barrio_seleccionado:
        st.session_state.barrio_seleccionado = nuevo_barrio
        st.rerun()

    barrio = st.session_state.barrio_seleccionado
    coords = BARRIOS_CARTAGENA[barrio]["coords"]
    historial_zona = BARRIOS_CARTAGENA[barrio]["historial"]
    nombre_barrio_corto = barrio.split(' (')[0]

    # 2. Contexto Territorial y Clima (Acordeón Compacto)
    with st.expander("📚 Contexto Territorial y Clima", expanded=False):
        clima = obtener_datos_clima(coords[0], coords[1])
        st.markdown(f"""
            <div style="font-size: 1.8rem; font-weight: 700; color: #f8fafc; margin-bottom: 5px;">{clima['temp']}°C</div>
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">
                <span>💧 Humedad: {clima['hum']}%</span>
                <span>💨 Viento: {clima['viento']} km/h</span>
            </div>
        """, unsafe_allow_html=True)
        st.caption(f"**Historial {nombre_barrio_corto}:** {historial_zona}")
        
        datos_historicos = pd.DataFrame(
            np.random.randint(10, 50, size=(6, 2)),
            columns=['Inund.', 'Desliz.'],
            index=['Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago']
        )
        st.bar_chart(datos_historicos, color=["#3b82f6", "#ef4444"], height=130)

    # 3. Contenedor Principal (Reporte y Simulación)
    st.markdown('<div class="result-card"><div class="result-card-header">⛈️ Simulador y Reporte Visual</div>', unsafe_allow_html=True)
    
    default_slider_val = min(100, max(0, int(round(clima['lluvia'] / 5.0) * 5)))
    intensidad_lluvia_mm = st.slider("Simular Intensidad Lluvia (mm/h)", 0, 100, default_slider_val, 5)

    if intensidad_lluvia_mm == 0: clasif_lluvia = "☀️ Despejado"
    elif intensidad_lluvia_mm <= 20: clasif_lluvia = "🌧️ Llovizna"
    elif intensidad_lluvia_mm <= 50: clasif_lluvia = "⛈️ Lluvia Media"
    elif intensidad_lluvia_mm <= 80: clasif_lluvia = "⛈️ Lluvia Fuerte"
    else: clasif_lluvia = "🚨 Tormenta"
    
    uploaded_file = st.file_uploader("Evidencia Fotográfica", type=["jpg", "jpeg", "png"])
    
    riesgo_pct = 0
    nivel_obstruccion = "Ninguno"
    justificacion = ""
    autenticidad = "Desconocida"
    privacidad = "Segura"

    if uploaded_file is not None:
        current_time = time.time()
        file_id = f"{uploaded_file.name}_{uploaded_file.size}_{barrio}"
        
        if st.session_state.ultimo_archivo != file_id:
            if st.session_state.upload_count >= 5:
                st.error("🚫 Límite de 5 reportes por sesión alcanzado.")
            elif current_time - st.session_state.last_upload_time < 30:
                st.warning(f"⏳ Espera {30 - int(current_time - st.session_state.last_upload_time)} segs antes de enviar otro reporte.")
            else:
                st.session_state.upload_count += 1
                st.session_state.last_upload_time = current_time
                st.session_state.ultimo_archivo = file_id
                
                image = Image.open(uploaded_file)
                
                fecha_captura = "Desconocida (Sin EXIF / WhatsApp)"
                exif_data = image.getexif()
                if exif_data:
                    for tag_id in exif_data:
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag == 'DateTimeOriginal' or tag == 'DateTime':
                            fecha_captura = str(exif_data.get(tag_id))
                st.session_state.fecha_captura = fecha_captura
                
                with st.spinner("Procesando IA Forense..."):
                    st.session_state.resultado_ia = analizar_imagen_canal(image, historial_zona)
        
        st.image(Image.open(uploaded_file), caption="Evidencia", use_container_width=True)
    else:
        st.session_state.resultado_ia = None
        st.session_state.ultimo_archivo = None
        st.session_state.fecha_captura = "Desconocida"

    if st.session_state.resultado_ia is not None:
        res = st.session_state.resultado_ia
        riesgo_pct = res.get("riesgo_inundacion_porcentaje", 0)
        justificacion = res.get("justificacion", "")
        autenticidad = res.get("autenticidad", "Desconocida")
        privacidad = res.get("privacidad", "Segura")
        st.info(f"**Diagnóstico:** {justificacion}")
        
    riesgo_base_ia = riesgo_pct / 100 
    factor_lluvia = intensidad_lluvia_mm / 100
    riesgo_total_pct = int(((riesgo_base_ia * 0.6) + (factor_lluvia * 0.4)) * 100)

    if riesgo_total_pct >= 75:
        color_marcador, icono_marcador, alerta_txt = "red", "warning-sign", f"🚨 EMERGENCIA ROJA"
        estado_ui = st.error
    elif riesgo_total_pct >= 50:
        color_marcador, icono_marcador, alerta_txt = "orange", "info-sign", f"⚠️ ALERTA NARANJA"
        estado_ui = st.warning
    elif riesgo_total_pct >= 25:
        color_marcador, icono_marcador, alerta_txt = "blue", "tint", f"ℹ️ MONITOREO AZUL"
        estado_ui = st.info
    else:
        color_marcador, icono_marcador, alerta_txt = "green", "ok-circle", f"🟢 ZONA SEGURA"
        estado_ui = st.success

    st.metric(label="Riesgo Agregado", value=f"{riesgo_total_pct}%", delta=f"{clasif_lluvia}")
    estado_ui(alerta_txt)
    
    if st.session_state.resultado_ia is not None:
        with st.expander("🛡️ Auditoría Forense y Privacidad"):
            fecha_cap = st.session_state.get("fecha_captura", "Desconocida")
            if "Desconocida" in fecha_cap: st.warning("⚠️ Origen: Sin EXIF original.")
            else: st.success(f"✅ EXIF: {fecha_cap}")
                
            if autenticidad == "Real": st.success("✅ Anti-Fake: Imagen Real.")
            else: st.error(f"🚨 Anti-Fake: Sospechosa ({autenticidad}).")
                
            if privacidad == "Datos Sensibles Detectados": st.success("🛡️ Censura Biométrica Activa.")
            else: st.info("ℹ️ Privacidad: Sin rostros/placas.")
            
    st.markdown('</div>', unsafe_allow_html=True)


with col_mapa:
    # 6. Mapeo GIS Interactivo
    # Inicializar el mapa en un punto central de Cartagena
    map_center = [10.3910, -75.4794]
    # Si el usuario hace zoom out, que vea toda Cartagena
    mapa = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB dark_matter")
    
    radio_impacto = 100 + (intensidad_lluvia_mm * 4)

    # Dibujar TODOS los puntos de monitoreo
    for b_name, b_info in BARRIOS_CARTAGENA.items():
        b_coords = b_info["coords"]
        if b_name == barrio:
            # Marcador activo (Resaltado)
            folium.Marker(
                location=b_coords, 
                popup=alerta_txt, 
                tooltip=f"📍 {b_name} (ACTIVO)", 
                icon=folium.Icon(color=color_marcador, icon=icono_marcador, prefix='glyphicon')
            ).add_to(mapa)
            # Círculo de afectación
            folium.Circle(
                location=b_coords, 
                radius=radio_impacto, 
                color=color_marcador, 
                fill=True, 
                fill_opacity=0.3, 
                tooltip=f"Radio afectación: {radio_impacto}m"
            ).add_to(mapa)
        else:
            # Marcadores inactivos (Listos para recibir click)
            folium.Marker(
                location=b_coords, 
                tooltip=f"📌 {b_name} (Click para monitorear)", 
                icon=folium.Icon(color="darkblue", icon="eye-open", prefix='glyphicon')
            ).add_to(mapa)
            
    # Renderizar mapa interactivo
    map_data = st_folium(mapa, use_container_width=True, height=750)
    
    # 7. EVENTOS DE CLICK EN EL MAPA
    if map_data and map_data.get("last_object_clicked"):
        lat = map_data["last_object_clicked"]["lat"]
        lng = map_data["last_object_clicked"]["lng"]
        
        # Encontrar el barrio más cercano al click
        for b_name, b_info in BARRIOS_CARTAGENA.items():
            # Si el click es muy cerca del marcador (tolerancia geo)
            if abs(b_info["coords"][0] - lat) < 0.005 and abs(b_info["coords"][1] - lng) < 0.005:
                if st.session_state.barrio_seleccionado != b_name:
                    # Cambiar el territorio seleccionado y refrescar el Dashboard
                    st.session_state.barrio_seleccionado = b_name
                    st.rerun()
