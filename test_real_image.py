import os
import io
import time
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
# Configurar forzando REST
genai.configure(api_key=api_key, transport='rest')

# Cargar una de las imágenes reales de WhatsApp (18 KB)
image_path = "/home/carlos/Proyectos/Canal Ia/Fts/WhatsApp Image 2026-08-13 at 11.01.50.jpeg"
print(f"Cargando imagen real: {image_path}")
img = Image.open(image_path)

# Convertir a bytes
img_byte_arr = io.BytesIO()
img.convert("RGB").save(img_byte_arr, format="JPEG")
img_bytes = img_byte_arr.getvalue()

image_part = {
    "mime_type": "image/jpeg",
    "data": img_bytes
}

prompt = """
Eres un ingeniero experto en gestión de riesgo de desastres e infraestructura pluvial en Cartagena. 
Tu tarea es analizar la imagen adjunta de un canal de agua, alcantarilla o calle y determinar el riesgo de inundación basado en obstrucciones visibles.

El JSON debe tener exactamente esta estructura:
{
  "nivel_obstruccion": "Alto" | "Medio" | "Bajo" | "Ninguno",
  "tipo_problema": "Basura" | "Escombros" | "Maleza" | "Agua estancada" | "Ninguno",
  "riesgo_inundacion_porcentaje": <numero entero entre 0 y 100>,
  "justificacion": "<Una sola oración explicando por qué diste ese porcentaje>"
}
"""

print("Enviando a gemini-3.5-flash...")
start_time = time.time()
try:
    model = genai.GenerativeModel('gemini-3.5-flash')
    response = model.generate_content(
        [prompt, image_part],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    print(f"¡ÉXITO en {time.time() - start_time:.2f}s!")
    print("\nRespuesta del modelo:")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
