"""Google News RSS connector for global news."""

import feedparser
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from urllib.parse import quote

from trading_mvp.data_sources.base_connector import BaseDataConnector

logger = logging.getLogger(__name__)

class GoogleNewsConnector(BaseDataConnector):
    """Connector for Google News RSS feeds."""

    def __init__(self):
        """Initialize Google News connector."""
        super().__init__("Google News RSS")
        logger.info("✅ Google News RSS connector initialized")

    def fetch_data(self, topic: str = "world", max_items: int = 50) -> List[Dict]:
        """Fetch news from Google News RSS.

        Args:
            topic: News topic (world, business, technology, etc.)
            max_items: Maximum items to fetch

        Returns:
            List of news items
        """
        try:
            # Google News RSS URL
            encoded_topic = quote(topic)
            rss_url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"

            logger.info(f"📰 Fetching Google News RSS for topic: {topic}...")

            # Parse RSS feed
            feed = feedparser.parse(rss_url)

            # Check if feed has entries
            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"⚠️  Google News RSS returned no entries for topic: {topic}")
                return []

            # Extract news items
            news_items = []
            for entry in feed.entries[:max_items]:
                item = {
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", ""),
                    "topic": topic
                }
                news_items.append(item)

            self.last_fetch = datetime.now()
            self.fetch_count += 1

            if not news_items:
                logger.warning(f"⚠️  Google News RSS had feed but 0 valid items for topic: {topic}")
            else:
                logger.info(f"✅ Fetched {len(news_items)} items from Google News RSS (topic: {topic})")

            return news_items

        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error fetching Google News RSS (topic: {topic}): {e}")
            return []

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
        elif hasattr(obj, 'keys'):  # Dict-like (FeedParserDict, dict, etc.)
            return {k: self.make_json_serializable(v) for k, v in obj.items()}
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            # List-like but not string/bytes
            try:
                return [self.make_json_serializable(item) for item in list(obj)]
            except:
                return str(obj)
        else:
            return str(obj)

    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize Google News to standard format.

        Args:
            raw_data: Raw news from Google RSS

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

                # Clean HTML from summary
                summary = item.get("summary", "")

                # Handle case where summary is a list
                if isinstance(summary, list):
                    summary = " ".join(str(s) for s in summary)
                elif not isinstance(summary, str):
                    summary = str(summary)

                # Clean HTML tags from summary
                import re
                if "<" in summary:
                    # Remove HTML tags
                    summary = re.sub(r'<[^>]+>', ' ', summary)
                    # Clean up extra whitespace
                    summary = " ".join(summary.split())

                # Convert entire item to JSON-serializable dict recursively
                clean_raw_data = self.make_json_serializable(item)

                # Extract source from FeedParserDict
                source_dict = item.get("source", {})
                if hasattr(source_dict, 'get'):
                    author = source_dict.get('title', 'Google News')
                else:
                    author = str(source_dict) if source_dict else 'Google News'

                normalized_item = {
                    "source": "google_news",
                    "source_type": "rss_feed",
                    "title": title,
                    "summary": summary.strip() or title,
                    "content": summary.strip() or title,
                    "url": item.get("link", "").strip(),
                    "author": author,
                    "published_at": item.get("published", ""),
                    "raw_data": clean_raw_data
                }
                normalized.append(normalized_item)
            except Exception as e:
                failed_items.append({"index": i, "reason": str(e)})
                logger.error(f"❌ Error normalizing Google News item {i}: {e}")

        # Reportar pérdidas
        if failed_items:
            logger.warning(f"⚠️  Failed to normalize {len(failed_items)}/{len(raw_data)} Google News items")
            for failure in failed_items[:5]:
                logger.warning(f"    - Item {failure['index']}: {failure['reason']}")

        logger.info(f"✅ Normalized {len(normalized)}/{len(raw_data)} Google News items")
        return normalized

    def fetch_geopolitical_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch geopolitical news.

        Topics: wars, conflicts, international relations, diplomacy

        Args:
            max_items: Maximum items to fetch

        Returns:
            List of geopolitical news items
        """
        geopolitical_topics = [
            "geopolitical conflicts war",
            "international relations diplomacy",
            "middle east conflict",
            "ukraine russia war",
            "china taiwan tensions"
        ]

        all_news = []
        for topic in geopolitical_topics:
            news = self.fetch_data(topic=topic, max_items=max_items//len(geopolitical_topics))
            all_news.extend(news)

        # Remove duplicates based on title
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title_lower = item.get("title", "").lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                item["geopolitical_relevant"] = True
                unique_news.append(item)

        logger.info(f"🌍 Found {len(unique_news)} unique geopolitical news items")

        return unique_news

    def fetch_economic_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch economic news.

        Topics: inflation, interest rates, GDP, employment, central banks

        Args:
            max_items: Maximum items to fetch

        Returns:
            List of economic news items
        """
        economic_topics = [
            "federal reserve interest rates",
            "inflation consumer prices",
            "GDP economic growth",
            "unemployment jobs report",
            "central bank monetary policy"
        ]

        all_news = []
        for topic in economic_topics:
            news = self.fetch_data(topic=topic, max_items=max_items//len(economic_topics))
            all_news.extend(news)

        # Remove duplicates
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title_lower = item.get("title", "").lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                item["economic_relevant"] = True
                unique_news.append(item)

        logger.info(f"💰 Found {len(unique_news)} unique economic news items")

        return unique_news

    def fetch_trade_policy_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch trade policy news.

        Topics: tariffs, trade wars, sanctions, trade agreements

        Args:
            max_items: Maximum items to fetch

        Returns:
            List of trade policy news items
        """
        trade_topics = [
            "trade tariffs sanctions",
            "us china trade war",
            "import export regulations",
            "trade agreements deals",
            "economic sanctions countries"
        ]

        all_news = []
        for topic in trade_topics:
            news = self.fetch_data(topic=topic, max_items=max_items//len(trade_topics))
            all_news.extend(news)

        # Remove duplicates
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title_lower = item.get("title", "").lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                item["trade_relevant"] = True
                unique_news.append(item)

        logger.info(f"📦 Found {len(unique_news)} unique trade policy news items")

        return unique_news

    def fetch_regulatory_news(self, max_items: int = 50) -> List[Dict]:
        """Fetch regulatory news.

        Topics: government regulations, policy changes, laws

        Args:
            max_items: Maximum items to fetch

        Returns:
            List of regulatory news items
        """
        regulatory_topics = [
            "government regulation policy",
            "federal regulations changes",
            "financial regulations banking",
            "technology regulation ai",
            "environmental regulations climate"
        ]

        all_news = []
        for topic in regulatory_topics:
            news = self.fetch_data(topic=topic, max_items=max_items//len(regulatory_topics))
            all_news.extend(news)

        # Remove duplicates
        seen_titles = set()
        unique_news = []
        for item in all_news:
            title_lower = item.get("title", "").lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                item["regulatory_relevant"] = True
                unique_news.append(item)

        logger.info(f"🏛️  Found {len(unique_news)} unique regulatory news items")

        return unique_news
