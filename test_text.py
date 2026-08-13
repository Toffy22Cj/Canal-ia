import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("Iniciando llamada de texto a gemini-3.5-flash...")
try:
    model = genai.GenerativeModel('gemini-3.5-flash')
    response = model.generate_content("Responde corto: ¿Cuál es la capital de Colombia?")
    print("Respuesta:")
    print(response.text)
except Exception as e:
    print("Error:", e)
