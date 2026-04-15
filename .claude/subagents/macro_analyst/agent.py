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
from trading_mvp.core.dna_manager import DNAManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def ingest_and_analyze(symbols: List[str]) -> None:
    """
    Ingests news from Alpaca, analyzes sentiment with Gemini using Asset DNA, and saves to the database.

    Args:
        symbols: A list of ticker symbols to process.
    """
    logger.info(f"🧬 Initializing DNA-Aware Macro Analysis for: {symbols}...")
    
    dna_manager = DNAManager()
    
    # Pre-fetch DNA for all symbols to avoid redundant calls
    dnas = {s: dna_manager.get_dna(s) for s in symbols}

    try:
        news_items = fetch_news(symbols=symbols)
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}")
        return

    for item in news_items:
        # Identify which ticker this news belongs to (simplified)
        # In a real scenario, we might want to analyze the same news for different DNAs
        target_ticker = symbols[0] # Fallback
        for s in symbols:
            if s in item['title'].upper() or s in item['content'].upper():
                target_ticker = s
                break
        
        dna = dnas.get(target_ticker)
        logger.info(f"Analyzing: '{item['title']}' for {target_ticker} (DNA: {dna.get('asset_type')})...")
        
        try:
            # Contextual Sentiment Analysis - Concatenate Title + Content for richer context
            news_headline = item.get('title') or ""
            news_body = item.get('content') or item.get('summary') or ""
            news_text = f"HEADLINE: {news_headline}\nCONTENT: {news_body}"
            
            analysis = analyze_sentiment(news_text, ticker=target_ticker, dna=dna)

            # Save news
            news_id = insert_news(
                external_id=item['external_id'],
                title=item['title'],
                source=item['author'],
                url=item['url'],
                summary=analysis.get('summary', 'No summary available'),
                published_at=str(item['created_at'])
            )

            # Save DNA-aware sentiment
            insert_sentiment(
                news_id=news_id,
                agent_id="macro_analyst_dna_aware",
                score=analysis['sentiment_score'],
                reasoning=analysis.get('reasoning', analysis['summary'])
            )
            logger.info(f"✅ DNA-Aware Sentiment: {analysis['sentiment_score']:.2f} | Reasoning: {analysis.get('reasoning', analysis['summary'])[:50]}...")
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
