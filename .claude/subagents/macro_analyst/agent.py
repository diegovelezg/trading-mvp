import os
import sys
import logging
import argparse
from typing import List

# Add parent directory to path to import trading_mvp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.news.alpaca_news import fetch_news
from trading_mvp.analysis.gemini_sentiment import analyze_sentiment
from trading_mvp.core.dashboard_api_client import insert_news, insert_sentiment

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
    parser = argparse.ArgumentParser(description="Ingest news and analyze sentiment for stock tickers.")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of ticker symbols.")

    args = parser.parse_args()

    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    else:
        # Default watchlist if no symbols provided
        symbols = ["AAPL", "TSLA", "MSFT"]

    ingest_and_analyze(symbols)

if __name__ == "__main__":
    main()
