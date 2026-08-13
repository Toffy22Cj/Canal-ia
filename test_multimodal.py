import os
import io
import time
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key, transport='rest')

img_path = "/home/carlos/Proyectos/Canal Ia/canal_obstruido.png"
img = Image.open(img_path)

# Convertir la imagen a bytes
img_byte_arr = io.BytesIO()
img.convert("RGB").save(img_byte_arr, format="JPEG")
img_bytes = img_byte_arr.getvalue()

image_part = {
    "mime_type": "image/jpeg",
    "data": img_bytes
}

modelos_a_probar = [
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-image",
    "gemini-flash-latest"
]

for model_name in modelos_a_probar:
    print(f"\n--- Probando modelo: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        start_time = time.time()
        response = model.generate_content(
            ["Describe esta imagen en una frase muy corta.", image_part]
        )
        duration = time.time() - start_time
        print(f"¡ÉXITO en {duration:.2f}s!")
        print(f"Respuesta: {response.text.strip()}")
    except Exception as e:
        print(f"Error con {model_name}: {e}")
