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

    def make_json_serializable(self, obj):
        """Convert an object to JSON-serializable format recursively.

        Args:
            obj: Any object

        Returns:
            JSON-serializable version
        """
        import datetime

        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif hasattr(obj, 'keys'):  # Dict-like
            return {k: self.make_json_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            try:
                return [self.make_json_serializable(item) for item in list(obj)]
            except:
                return str(obj)
        else:
            return str(obj)

    def parse_relative_date(self, date_str: str) -> str:
        """Convert SERPAPI relative dates to ISO format.

        Args:
            date_str: Date string like "1 day ago", "4 hours ago", "LIVE5 minutes ago"

        Returns:
            ISO formatted date string or empty string if parsing fails
        """
        from datetime import datetime, timedelta
        import re

        if not date_str or not isinstance(date_str, str):
            return ""

        # Remove LIVE prefix if present
        date_str = date_str.replace("LIVE", "").strip()

        # Try to extract relative time pattern
        # Matches: "1 day ago", "4 hours ago", "23 hours ago", "2 days ago", "3 weeks ago", "42 seconds ago", "1 month ago"
        match = re.match(r'(\d+)\s+(second|minute|hour|day|week|month)s?\s+ago', date_str.lower())

        if match:
            value = int(match.group(1))
            unit = match.group(2)

            # Calculate the date
            if unit == 'second':
                delta = timedelta(seconds=value)
            elif unit == 'minute':
                delta = timedelta(minutes=value)
            elif unit == 'hour':
                delta = timedelta(hours=value)
            elif unit == 'day':
                delta = timedelta(days=value)
            elif unit == 'week':
                delta = timedelta(weeks=value)
            elif unit == 'month':
                # Approximate month as 30 days
                delta = timedelta(days=value * 30)
            else:
                return ""

            # Calculate past date and return ISO format
            past_date = datetime.now() - delta
            return past_date.isoformat()

        # If not a relative date, return as-is (might already be ISO or other format)
        return date_str

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

                if not news_results:
                    logger.warning(f"⚠️  SERPAPI returned 200 but no news_results for query: '{query}'")
                else:
                    logger.info(f"✅ Fetched {len(news_results)} news items from SERPAPI (query: '{query}')")

                return news_results
            else:
                error_detail = response.text[:200] if response.text else "No error details"
                logger.error(f"❌ SERPAPI returned {response.status_code}: {error_detail}")
                return []

        except requests.exceptions.Timeout as e:
            self.error_count += 1
            logger.error(f"❌ SERPAPI timeout after 30s (query: '{query}'): {e}")
            return []
        except requests.exceptions.ConnectionError as e:
            self.error_count += 1
            logger.error(f"❌ SERPAPI connection error (query: '{query}'): {e}")
            return []
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            logger.error(f"❌ SERPAPI request failed (query: '{query}'): {e}")
            return []
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Unexpected error fetching SERPAPI news (query: '{query}'): {e}")
            return []

    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize SERPAPI news to standard format.

        Args:
            raw_data: Raw news from SERPAPI

        Returns:
            Normalized news items
        """
        normalized = []
        failed_items = []

        for i, item in enumerate(raw_data):
            try:
                # Validar título
                title = item.get("title", "").strip()
                if not title or title == "[Removed]":
                    failed_items.append({"index": i, "reason": "invalid_title"})
                    continue

                # Validar URL
                url = item.get("link", "").strip()
                if not url:
                    failed_items.append({"index": i, "reason": "missing_url"})
                    continue

                # Extract and parse date
                date_str = item.get("date", "")
                parsed_date = self.parse_relative_date(date_str)

                # Convert entire item to JSON-serializable recursively
                clean_raw_data = self.make_json_serializable(item)

                normalized_item = {
                    "source": "serpapi_google_news",
                    "source_type": "search_api",
                    "title": title,
                    "summary": item.get("snippet", "").strip() or title,
                    "content": item.get("snippet", "").strip() or title,
                    "url": url,
                    "author": "",
                    "published_at": parsed_date,  # ✅ PARSED TO ISO FORMAT
                    "symbols": [],  # SERPAPI doesn't provide symbols
                    "raw_data": clean_raw_data
                }
                normalized.append(normalized_item)
            except Exception as e:
                failed_items.append({"index": i, "reason": str(e)})
                logger.error(f"❌ Error normalizing SERPAPI news item {i}: {e}")

        # Reportar pérdidas
        if failed_items:
            logger.warning(f"⚠️  Failed to normalize {len(failed_items)}/{len(raw_data)} SERPAPI news items")
            for failure in failed_items[:5]:
                logger.warning(f"    - Item {failure['index']}: {failure['reason']}")

        logger.info(f"✅ Normalized {len(normalized)}/{len(raw_data)} SERPAPI news items")
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
