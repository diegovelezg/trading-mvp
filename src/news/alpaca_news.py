import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from alpaca.data.historical import NewsClient
from alpaca.data.requests import NewsRequest

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fetch_news(symbols: Optional[List[str]] = None) -> List[Dict]:
    """
    Fetches the latest news for a list of symbols from the Alpaca News API.
    
    Args:
        symbols: A list of ticker symbols to fetch news for.
        
    Returns:
        A list of dictionaries containing news item details.
    """
    api_key = os.getenv("ALPACA_DATA_API_KEY")
    secret_key = os.getenv("ALPACA_DATA_API_SECRET")

    if not api_key:
        raise ValueError("ALPACA_DATA_API_KEY is required in environment variables.")

    # Try with empty secret if not provided (Alpaca may have changed auth requirements)
    if not secret_key:
        secret_key = ""
        logger.info("Attempting connection with API Key only (no secret provided)")

    client = NewsClient(api_key=api_key, secret_key=secret_key)
    
    # Configure the request
    # NewsRequest expects symbols as a comma-separated string in current library version.
    symbols_str = ",".join(symbols) if isinstance(symbols, list) else symbols
    
    request_params = NewsRequest(
        symbols=symbols_str,
        limit=10
    )
    
    # Execute the request
    response = client.get_news(request_params)
    
    # Process the response into a consistent format
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
