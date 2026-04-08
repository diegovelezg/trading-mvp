"""Alpaca News API connector for real-time news."""

import os
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

from trading_mvp.data_sources.base_connector import BaseDataConnector

load_dotenv()
logger = logging.getLogger(__name__)

class AlpacaNewsConnector(BaseDataConnector):
    """Connector for Alpaca News API."""

    def __init__(self):
        """Initialize Alpaca News connector."""
        super().__init__("Alpaca News")

        # News API requires PAPER credentials (DATA API credentials don't work)
        self.api_key = os.getenv("ALPACA_PAPER_API_KEY")
        self.api_secret = os.getenv("PAPER_API_SECRET")
        self.base_url = "https://data.alpaca.markets"  # Fixed base URL for market data

        if not self.api_key or not self.api_secret:
            raise ValueError("Alpaca API credentials not found in environment variables")

        self.headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret
        }

        logger.info("✅ Alpaca News connector initialized")

    def fetch_data(self, hours_back: int = 24, max_items: int = 50) -> List[Dict]:
        """Fetch recent news from Alpaca v1beta1 News API.

        Note: Alpaca enforces a maximum limit of 50 items per request.

        Args:
            hours_back: Hours to look back
            max_items: Maximum number of items to fetch (max 50)

        Returns:
            List of news items
        """
        try:
            # Calculate start time (RFC3339 format for Alpaca API)
            start_time = datetime.now() - timedelta(hours=hours_back)
            start_formatted = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')  # RFC3339 format

            # Alpaca v1beta1 News API endpoint (requires PAPER credentials)
            url = f"{self.base_url}/v1beta1/news"

            params = {
                "start": start_formatted,
                "limit": max_items,
                "sort": "desc"
            }

            logger.info(f"📰 Fetching news from Alpaca v1beta1 (last {hours_back} hours)...")

            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            # v1beta1 news returns {"news": [...]}
            if response.status_code == 200:
                response_data = response.json()
                news_items = response_data.get("news", [])
                self.last_fetch = datetime.now()
                self.fetch_count += 1
                logger.info(f"✅ Fetched {len(news_items)} news items from Alpaca v1beta1")
                return news_items
            else:
                logger.warning(f"⚠️  Alpaca v1 News API returned: {response.status_code}")
                # Fallback: return empty array
                return []

        except requests.exceptions.RequestException as e:
            self.error_count += 1
            logger.warning(f"⚠️  Could not fetch Alpaca news: {e}")
            return []

    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize Alpaca news to standard format.

        Args:
            raw_data: Raw news from Alpaca

        Returns:
            Normalized news items
        """
        normalized = []

        for item in raw_data:
            try:
                normalized_item = {
                    "source": "alpaca_news",
                    "source_type": "news_api",
                    "title": item.get("headline", ""),
                    "summary": item.get("summary", "") or item.get("headline", ""),
                    "content": item.get("summary", "") or item.get("headline", ""),
                    "url": item.get("url", ""),
                    "author": item.get("author", ""),
                    "published_at": item.get("created_at", ""),
                    "symbols": item.get("symbols", []),
                    "raw_data": item
                }
                normalized.append(normalized_item)
            except Exception as e:
                logger.warning(f"⚠️  Error normalizing news item: {e}")
                continue

        return normalized

    def fetch_macro_news(self, hours_back: int = 24) -> List[Dict]:
        """Fetch macro-economic and geopolitical news.

        This filters for news related to:
        - Central banks (Fed, ECB, BOE, etc.)
        - Government actions
        - Geopolitical events
        - Economic indicators
        - Trade policies
        - Commodities

        Args:
            hours_back: Hours to look back

        Returns:
            List of macro-relevant news items
        """
        # Fetch all news (max 50 items per Alpaca limit)
        all_news = self.fetch_data(hours_back=hours_back, max_items=50)

        # Filter for macro keywords
        macro_keywords = [
            "fed", "ecb", "bank of", "central bank",
            "inflation", "interest rate", "gdp", "unemployment",
            "government", "congress", "senate", "president",
            "china", "eu", "europe", "middle east", "russia", "ukraine",
            "trade", "tariff", "sanction", "embargo",
            "oil", "gas", "commodity", "lithium", "copper",
            "geopolitic", "conflict", "war", "tension",
            "economic", "recession", "crisis", "market"
        ]

        macro_news = []
        for news in all_news:
            # Check if title or summary contains macro keywords
            title = news.get("headline", "").lower()
            summary = news.get("summary", "").lower()

            if any(keyword in title or keyword in summary for keyword in macro_keywords):
                news["macro_relevant"] = True
                macro_news.append(news)

        logger.info(f"🌍 Found {len(macro_news)} macro-relevant news items out of {len(all_news)} total")

        return macro_news

    def fetch_commodity_news(self, hours_back: int = 24) -> List[Dict]:
        """Fetch commodity-related news.

        Args:
            hours_back: Hours to look back

        Returns:
            List of commodity news items
        """
        # Fetch all news (max 50 items per Alpaca limit)
        all_news = self.fetch_data(hours_back=hours_back, max_items=50)

        # Filter for commodity keywords
        commodity_keywords = [
            "oil", "gas", "natural gas", "crude",
            "gold", "silver", "copper", "lithium",
            "commodity", "futures", "wti", "brent",
            "opec", "energy", "mining", "materials"
        ]

        commodity_news = []
        for news in all_news:
            title = news.get("headline", "").lower()
            summary = news.get("summary", "").lower()

            if any(keyword in title or keyword in summary for keyword in commodity_keywords):
                news["commodity_relevant"] = True
                commodity_news.append(news)

        logger.info(f"🛢️  Found {len(commodity_news)} commodity news items")

        return commodity_news

    def fetch_sector_news(self, sector: str, hours_back: int = 24) -> List[Dict]:
        """Fetch news for specific sector.

        Args:
            sector: Sector name (technology, energy, healthcare, etc.)
            hours_back: Hours to look back

        Returns:
            List of sector news items
        """
        # Fetch all news (max 50 items per Alpaca limit)
        all_news = self.fetch_data(hours_back=hours_back, max_items=50)

        # Filter for sector keywords
        sector_keywords = {
            "technology": ["tech", "software", "ai", "cloud", "semiconductor", "chip"],
            "energy": ["energy", "oil", "gas", "solar", "renewable", "power"],
            "healthcare": ["health", "pharma", "medical", "drug", "fda", "biotech"],
            "financial": ["bank", "financial", "insurance", "credit", "loan"],
            "consumer": ["retail", "consumer", "ecommerce", "shopping"],
            "industrial": ["industrial", "manufacturing", "factory", "construction"]
        }

        keywords = sector_keywords.get(sector.lower(), [sector.lower()])

        sector_news = []
        for news in all_news:
            title = news.get("headline", "").lower()
            summary = news.get("summary", "").lower()

            if any(keyword in title or keyword in summary for keyword in keywords):
                news["sector_relevant"] = True
                news["sector"] = sector
                sector_news.append(news)

        logger.info(f"📊 Found {len(sector_news)} {sector} news items")

        return sector_news

    def get_status(self) -> Dict:
        """Get connector status."""
        status = super().get_status()
        status["api_endpoint"] = f"{self.base_url}/v1beta1/news"
        status["credentials"] = "PAPER_API"  # Using PAPER credentials
        return status
