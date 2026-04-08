"""SERPAPI Google News connector for real-time news."""

import os
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

from trading_mvp.data_sources.base_connector import BaseDataConnector

load_dotenv()
logger = logging.getLogger(__name__)

class SerpApiConnector(BaseDataConnector):
    """Connector for SERPAPI Google News search."""

    def __init__(self):
        """Initialize SERPAPI connector."""
        super().__init__("SERPAPI Google News")

        self.api_key = os.getenv("SERPAPI_API_KEY")

        if not self.api_key:
            logger.warning("⚠️  SERPAPI_API_KEY not found in environment variables")
            raise ValueError("SERPAPI_API_KEY not found in environment variables")

        self.base_url = "https://serpapi.com/search.json"

        logger.info("✅ SERPAPI Google News connector initialized")

    def fetch_data(self, query: str = "geopolitical news", max_items: int = 50) -> List[Dict]:
        """Fetch recent news from Google News via SERPAPI.

        Args:
            query: Search query
            max_items: Maximum number of items to fetch

        Returns:
            List of news items
        """
        try:
            # SERPAPI parameters for Google News
            params = {
                "engine": "google",
                "tbm": "nws",  # News search
                "q": query,
                "api_key": self.api_key,
                "num": min(max_items, 100)  # SERPAPI max is 100
            }

            logger.info(f"📰 Fetching news from SERPAPI (query: '{query}')...")

            response = requests.get(self.base_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                news_results = data.get("news_results", [])

                self.last_fetch = datetime.now()
                self.fetch_count += 1
                logger.info(f"✅ Fetched {len(news_results)} news items from SERPAPI")
                return news_results
            else:
                logger.warning(f"⚠️  SERPAPI returned: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            self.error_count += 1
            logger.warning(f"⚠️  Could not fetch SERPAPI news: {e}")
            return []

    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize SERPAPI news to standard format.

        Args:
            raw_data: Raw news from SERPAPI

        Returns:
            Normalized news items
        """
        normalized = []

        for item in raw_data:
            try:
                # Extract date if available
                date_str = item.get("date", "")

                normalized_item = {
                    "source": "serpapi_google_news",
                    "source_type": "search_api",
                    "title": item.get("title", ""),
                    "summary": item.get("snippet", ""),
                    "content": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "author": "",
                    "published_at": date_str,
                    "symbols": [],  # SERPAPI doesn't provide symbols
                    "raw_data": item
                }
                normalized.append(normalized_item)
            except Exception as e:
                logger.warning(f"⚠️  Error normalizing news item: {e}")
                continue

        return normalized

    def fetch_geopolitical_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch geopolitical news.

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            List of geopolitical news items
        """
        queries = [
            "geopolitical news",
            "international conflicts",
            "middle east news",
            "russia ukraine news",
            "china trade news"
        ]

        all_news = []
        for query in queries:
            news = self.fetch_data(query=query, max_items=max_items // len(queries))
            all_news.extend(news)

        # Remove duplicates based on URL
        seen_urls = set()
        unique_news = []
        for item in all_news:
            url = item.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(item)

        logger.info(f"🌍 Found {len(unique_news)} unique geopolitical news items")

        return unique_news

    def fetch_economic_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch economic news.

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            List of economic news items
        """
        queries = [
            "federal reserve news",
            "inflation news",
            "economic indicators",
            "interest rates news",
            "gdp economic news"
        ]

        all_news = []
        for query in queries:
            news = self.fetch_data(query=query, max_items=max_items // len(queries))
            all_news.extend(news)

        # Remove duplicates
        seen_urls = set()
        unique_news = []
        for item in all_news:
            url = item.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(item)

        logger.info(f"💰 Found {len(unique_news)} unique economic news items")

        return unique_news

    def fetch_trade_policy_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch trade policy news.

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            List of trade policy news items
        """
        queries = [
            "trade policy news",
            "tariffs news",
            "sanctions news",
            "export import news"
        ]

        all_news = []
        for query in queries:
            news = self.fetch_data(query=query, max_items=max_items // len(queries))
            all_news.extend(news)

        # Remove duplicates
        seen_urls = set()
        unique_news = []
        for item in all_news:
            url = item.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_news.append(item)

        logger.info(f"📋 Found {len(unique_news)} unique trade policy news items")

        return unique_news

    def fetch_macro_news(self, hours_back: int = 24) -> List[Dict]:
        """Fetch all macro-relevant news.

        Args:
            hours_back: Hours to look back (not used in SERPAPI, kept for compatibility)

        Returns:
            List of macro-relevant news items
        """
        # Fetch from all categories
        geo_news = self.fetch_geopolitical_news(max_items=20)
        econ_news = self.fetch_economic_news(max_items=20)
        trade_news = self.fetch_trade_policy_news(max_items=10)

        # Combine all news
        all_news = geo_news + econ_news + trade_news

        # Remove duplicates
        seen_urls = set()
        unique_news = []
        for item in all_news:
            url = item.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                item["macro_relevant"] = True
                unique_news.append(item)

        logger.info(f"🌍 Found {len(unique_news)} total macro-relevant news items from SERPAPI")

        return unique_news

    def get_status(self) -> Dict:
        """Get connector status."""
        status = super().get_status()
        status["api_endpoint"] = self.base_url
        status["has_api_key"] = bool(self.api_key)
        return status
