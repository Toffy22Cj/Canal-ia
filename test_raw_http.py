import os
import base64
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

image_path = "/home/carlos/Proyectos/Canal Ia/Fts/WhatsApp Image 2026-08-13 at 11.01.50.jpeg"
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

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

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
headers = {"Content-Type": "application/json"}
payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": image_b64
                    }
                }
            ]
        }
    ],
    "generationConfig": {
        "responseMimeType": "application/json",
        "temperature": 0.2
    }
}

print("Enviando petición HTTP POST directa...")
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print("Código de respuesta:", response.status_code)
    if response.status_code == 200:
        res_json = response.json()
        print("\n--- Respuesta del Servidor ---")
        text_response = res_json['candidates'][0]['content']['parts'][0]['text']
        print(text_response)
    else:
        print("Error:", response.text)
except Exception as e:
    print("Excepción:", e)
