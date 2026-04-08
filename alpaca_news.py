import os
from dotenv import load_dotenv
from alpaca.data.historical import NewsClient
from alpaca.data.requests import NewsRequest

# Carga variables de entorno
load_dotenv()

def fetch_news(symbols=None):
    """
    Obtiene las últimas noticias para una lista de símbolos desde Alpaca News API.
    """
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")
    
    if not api_key or not secret_key:
        raise ValueError("Se requieren ALPACA_API_KEY y ALPACA_SECRET_KEY en las variables de entorno.")
    
    client = NewsClient(api_key=api_key, secret_key=secret_key)
    
    # Configurar la solicitud
    # NewsRequest expects symbols as a string or list depending on version, 
    # but error indicates it wants a string.
    symbols_str = ",".join(symbols) if isinstance(symbols, list) else symbols
    
    request_params = NewsRequest(
        symbols=symbols_str,
        limit=10  # Por defecto, limitamos a 10 noticias
    )
    
    # Ejecutar la solicitud
    response = client.get_news(request_params)
    
    # Procesar la respuesta para un formato consistente
    news_items = []
    for item in response.news:
        news_items.append({
            "title": item.title,
            "author": item.author,
            "content": item.content,
            "url": item.url,
            "external_id": str(item.id),
            "created_at": item.created_at
        })
        
    return news_items
