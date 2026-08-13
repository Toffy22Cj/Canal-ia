import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("API Key cargada (primeros caracteres):", api_key[:10] if api_key else "None")

if api_key:
    genai.configure(api_key=api_key)
else:
    print("¡ERROR: No se encontró la clave GEMINI_API_KEY!")

try:
    print("\nModelos disponibles:")
    for m in genai.list_models():
        print(f"- {m.name}")
except Exception as e:
    print("Error al listar modelos:", e)
