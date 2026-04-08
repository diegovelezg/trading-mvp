from alpaca_news import fetch_news
from gemini_sentiment import analyze_sentiment
from db_manager import insert_news, insert_sentiment

def ingest_and_analyze(symbols):
    """
    Ingiere noticias desde Alpaca, analiza su sentimiento con Gemini
    y las guarda en la base de datos.
    """
    print(f"Buscando noticias para: {symbols}...")
    news_items = fetch_news(symbols=symbols)
    
    for item in news_items:
        print(f"Analizando: {item['title']}...")
        analysis = analyze_sentiment(item['content'])
        
        # Guardar la noticia
        news_id = insert_news(
            external_id=item['external_id'],
            title=item['title'],
            source=item['author'],
            url=item['url'],
            summary=analysis['summary'],
            published_at=item['created_at']
        )
        
        # Guardar el sentimiento
        insert_sentiment(
            news_id=news_id,
            agent_id="macro_analyst_v1",
            score=analysis['sentiment'],
            reasoning=analysis['summary']
        )
        print(f"Guardado exitosamente con ID {news_id} y sentimiento {analysis['sentiment']}.")

if __name__ == "__main__":
    # Prueba rápida
    ingest_and_analyze(["AAPL", "TSLA"])
