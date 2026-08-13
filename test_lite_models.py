import os
import io
import time
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')

img_path = "/home/carlos/Proyectos/Canal Ia/Fts/WhatsApp Image 2026-08-13 at 11.01.50.jpeg"
img = Image.open(img_path)

# Convertir a bytes
img_byte_arr = io.BytesIO()
img.convert("RGB").save(img_byte_arr, format="JPEG")
img_bytes = img_byte_arr.getvalue()

image_part = {
    "mime_type": "image/jpeg",
    "data": img_bytes
}

modelos_alternativos = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-pro"
]

for model_name in modelos_alternativos:
    print(f"\n--- Probando modelo alternativo: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        start_time = time.time()
        response = model.generate_content(
            ["Describe esta imagen en una frase corta en español.", image_part]
        )
        duration = time.time() - start_time
        print(f"¡ÉXITO con {model_name} en {duration:.2f}s!")
        print(f"Respuesta: {response.text.strip()}")
        break # Si uno tiene éxito, paramos
    except Exception as e:
        print(f"Error con {model_name}: {e}")
