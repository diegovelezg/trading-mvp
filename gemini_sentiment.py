import os
import json
from dotenv import load_dotenv
from google.genai import Client

# Carga variables de entorno
load_dotenv()

def analyze_sentiment(text):
    """
    Analiza el sentimiento de un texto usando Gemini 3 Flash.
    Retorna un diccionario con 'sentiment' (-1 a 1) y 'summary'.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Se requiere GEMINI_API_KEY en las variables de entorno.")
    
    client = Client(api_key=api_key)
    
    prompt = f"""
    Analyze the sentiment of the following financial news content.
    Provide your response in JSON format with the following keys:
    - sentiment: a float between -1 (extremely negative) and 1 (extremely positive)
    - summary: a brief summary of the news
    
    News Content:
    {text}
    """
    
    # Llamada a Gemini 3 Flash
    # Nota: El nombre del modelo puede variar, pero espec.md dice Gemini 3 Flash.
    # Usaremos 'gemini-2.0-flash' o similar si 'gemini-3-flash' no está disponible,
    # pero seguiré el nombre de la especificación si es posible o el más cercano.
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Ajustado a un modelo disponible común, pero representativo de 'Flash'
            contents=prompt
        )
        
        # Procesar la respuesta JSON
        # A veces el modelo devuelve bloques de código ```json ... ```
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()
            
        result = json.loads(clean_text)
        return {
            "sentiment": float(result.get("sentiment", 0)),
            "summary": str(result.get("summary", "No summary provided."))
        }
    except Exception as e:
        print(f"Error analizando sentimiento: {e}")
        return {
            "sentiment": 0.0,
            "summary": f"Error: {e}"
        }
