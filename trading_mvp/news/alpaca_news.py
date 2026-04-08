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
    # Try Paper credentials first (more likely to have News API access)
    api_key = os.getenv("ALPACA_PAPER_API_KEY")
    secret_key = os.getenv("PAPER_API_SECRET")

    if not api_key or not secret_key:
        raise ValueError("ALPACA_PAPER_API_KEY and PAPER_API_SECRET are required in environment variables.")

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

    # Access the news data from response.data['news']
    if hasattr(response, 'data') and 'news' in response.data:
        items = response.data['news']
    else:
        logger.error("No news data found in response")
        return []

    logger.info(f"Found {len(items)} news items")

    for item in items:
        # Map Alpaca news fields to our expected format
        if isinstance(item, dict):
            news_items.append({
                "title": item.get('headline', ''),
                "author": item.get('author', 'Unknown'),
                "content": item.get('summary', ''),
                "url": item.get('url', ''),
                "external_id": str(item.get('id', '')),
                "created_at": item.get('created_at', None)
            })
        elif hasattr(item, 'headline'):
            # Handle Alpaca News objects
            news_items.append({
                "title": getattr(item, 'headline', ''),
                "author": getattr(item, 'author', 'Unknown'),
                "content": getattr(item, 'summary', ''),
                "url": getattr(item, 'url', ''),
                "external_id": str(getattr(item, 'id', '')),
                "created_at": getattr(item, 'created_at', None)
            })
        else:
            logger.warning(f"Unexpected item type: {type(item)}")

    return news_items
        
    return news_items
