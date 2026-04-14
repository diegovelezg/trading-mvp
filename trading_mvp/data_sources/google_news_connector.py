"""Google News RSS connector for global news."""

import feedparser
import logging
from typing import List, Dict
from datetime import datetime, timedelta
from urllib.parse import quote
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.news_criteria import (
    NEWS_CATEGORIES,
    get_active_categories,
    get_search_queries,
    calculate_items_per_category,
    MAX_ITEMS_PER_CATEGORY,
    DUPLICATE_BY
)

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

    def fetch_all_categorized_news(self, max_items: int = None) -> List[Dict]:
        """
        Fetch news from ALL categories defined in news_criteria.py

        This is the MAIN method that uses the centralized criteria.

        Args:
            max_items: Maximum total items to fetch across all categories (defaults to config)

        Returns:
            List of categorized news items
        """
        if max_items is None:
            max_items = MAX_ITEMS_PER_CATEGORY

        logger.info("="*70)
        logger.info("📰 GOOGLE NEWS - CATEGORIZED SEARCH")
        logger.info("="*70)

        active_categories = get_active_categories()
        items_per_category = calculate_items_per_category(max_items, len(active_categories))

        logger.info(f"📋 Categories: {len(active_categories)}")
        logger.info(f"📊 Items per category: {items_per_category}")
        logger.info("")

        all_news = []

        for category in active_categories:
            logger.info(f"🔍 Fetching '{category}'...")

            queries = get_search_queries(category)
            category_news = []

            for query in queries:
                try:
                    news = self.fetch_data(
                        topic=query,
                        max_items=items_per_category // len(queries)
                    )
                    category_news.extend(news)
                except Exception as e:
                    logger.warning(f"   ⚠️  Query failed: {query} - {e}")
                    continue

            # Remove duplicates within category
            unique_news = self._remove_duplicates(category_news)
            logger.info(f"   ✅ {category}: {len(unique_news)} unique news")

            # Tag with category
            for news in unique_news:
                news['category'] = category
                news['search_query'] = query

            all_news.extend(unique_news)

        # Final deduplication across all categories
        final_news = self._remove_duplicates(all_news)

        logger.info("")
        logger.info(f"📊 TOTAL: {len(final_news)} unique news items across {len(active_categories)} categories")
        logger.info("="*70)

        return final_news

    def _remove_duplicates(self, news_list: List[Dict]) -> List[Dict]:
        """
        Remove duplicates from news list.

        Args:
            news_list: List of news items

        Returns:
            List with duplicates removed
        """
        if DUPLICATE_BY == "title":
            seen = set()
            unique = []
            for item in news_list:
                title_lower = item.get("title", "").lower()
                if title_lower and title_lower not in seen:
                    seen.add(title_lower)
                    unique.append(item)
            return unique
        elif DUPLICATE_BY == "url":
            seen = set()
            unique = []
            for item in news_list:
                url = item.get("url", "")
                if url and url not in seen:
                    seen.add(url)
                    unique.append(item)
            return unique
        else:
            return news_list
