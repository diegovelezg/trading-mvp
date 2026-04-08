import logging
from typing import List
from alpaca_news import fetch_news
from gemini_sentiment import analyze_sentiment
from db_manager import insert_news, insert_sentiment

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def ingest_and_analyze(symbols: List[str]) -> None:
    """
    Ingests news from Alpaca, analyzes sentiment with Gemini, and saves to the database.
    
    Args:
        symbols: A list of ticker symbols to process.
    """
    logger.info(f"Searching news for: {symbols}...")
    try:
        news_items = fetch_news(symbols=symbols)
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return
    
    for item in news_items:
        logger.info(f"Analyzing: {item['title']}...")
        try:
            analysis = analyze_sentiment(item['content'])
            
            # Save news
            news_id = insert_news(
                external_id=item['external_id'],
                title=item['title'],
                source=item['author'],
                url=item['url'],
                summary=analysis['summary'],
                published_at=str(item['created_at'])
            )
            
            # Save sentiment
            insert_sentiment(
                news_id=news_id,
                agent_id="macro_analyst_v1",
                score=analysis['sentiment'],
                reasoning=analysis['summary']
            )
            logger.info(f"Successfully saved with ID {news_id} and sentiment {analysis['sentiment']}.")
        except Exception as e:
            logger.error(f"Failed to process news item '{item['title']}': {e}")

def main() -> None:
    """Main execution point for the macro analyst script."""
    ingest_and_analyze(["AAPL", "TSLA", "MSFT"])

if __name__ == "__main__":
    main()
