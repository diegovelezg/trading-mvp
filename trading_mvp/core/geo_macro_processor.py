"""GeoMacro News Processing Pipeline: Steps 1 & 2

Step 1: Ingesta de noticias → geo_macro_news (raw)
Step 2: Extracción de entities + Generación de insights (sin guardar)
"""

import os
import logging
from typing import List, Dict, Tuple
from datetime import datetime

from trading_mvp.data_sources import AlpacaNewsConnector, GoogleNewsConnector, SerpApiConnector
from trading_mvp.analysis.entity_extractor import EntityExtractor
from trading_mvp.core.db_geo_news import (
    create_geo_macro_news_table,
    insert_geo_news_batch,
    get_recent_news,
    get_news_count_by_source
)
from trading_mvp.core.db_geo_entities import (
    create_geo_macro_entities_table,
    insert_entities_batch,
    get_entities_for_news
)

logger = logging.getLogger(__name__)

class GeoMacroProcessor:
    """Processor for geo_macro news ingestion and entity extraction."""

    def __init__(self):
        """Initialize processor."""
        # Initialize connectors
        self.alpaca_connector = AlpacaNewsConnector()
        self.google_connector = GoogleNewsConnector()
        self.serpapi_connector = SerpApiConnector()

        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()

        logger.info("✅ GeoMacroProcessor initialized")

    def step1_fetch_and_store_news(self, hours_back: int = 24) -> Dict[str, int]:
        """Step 1: Fetch news from all sources and store in geo_macro_news.

        Args:
            hours_back: Hours to look back for news

        Returns:
            Dictionary with counts per source
        """

        logger.info(f"📰 Step 1: Fetching news (last {hours_back} hours)...")

        all_news = []
        source_counts = {}
        fetch_errors = {}

        # 1.1: Fetch from Alpaca
        try:
            logger.info("  📰 Fetching from Alpaca News...")
            alpaca_news = self.alpaca_connector.fetch_macro_news(hours_back=hours_back)
            if not alpaca_news:
                logger.warning("  ⚠️  Alpaca returned empty results")
                fetch_errors['alpaca'] = "empty_results"
            alpaca_normalized = self.alpaca_connector.normalize_data(alpaca_news)
            if not alpaca_normalized:
                logger.warning("  ⚠️  Alpaca normalization produced 0 items")
                fetch_errors['alpaca'] = "normalization_failed"
            all_news.extend(alpaca_normalized)
            source_counts['alpaca'] = len(alpaca_normalized)
            logger.info(f"  ✅ Alpaca: {len(alpaca_normalized)} items")
        except Exception as e:
            logger.error(f"  ❌ Alpaca failed completely: {e}")
            fetch_errors['alpaca'] = str(e)
            source_counts['alpaca'] = 0

        # 1.2: Fetch from Google News
        try:
            logger.info("  🌐 Fetching from Google News RSS...")
            google_geo = self.google_connector.fetch_geopolitical_news(max_items=30)
            google_econ = self.google_connector.fetch_economic_news(max_items=30)
            google_raw = google_geo + google_econ
            if not google_raw:
                logger.warning("  ⚠️  Google News returned empty results")
                fetch_errors['google'] = "empty_results"
            # IMPORTANT: normalize_data to convert FeedParserDict to JSON-serializable
            google_news = self.google_connector.normalize_data(google_raw)
            if not google_news:
                logger.warning("  ⚠️  Google normalization produced 0 items")
                fetch_errors['google'] = "normalization_failed"
            all_news.extend(google_news)
            source_counts['google'] = len(google_news)
            logger.info(f"  ✅ Google News: {len(google_news)} items")
        except Exception as e:
            logger.error(f"  ❌ Google News failed completely: {e}")
            fetch_errors['google'] = str(e)
            source_counts['google'] = 0

        # 1.3: Fetch from SERPAPI
        try:
            logger.info("  🔍 Fetching from SERPAPI...")
            serpapi_news = self.serpapi_connector.fetch_macro_news()
            if not serpapi_news:
                logger.warning("  ⚠️  SERPAPI returned empty results")
                fetch_errors['serpapi'] = "empty_results"
            # IMPORTANT: normalize_data to convert to JSON-serializable
            serpapi_normalized = self.serpapi_connector.normalize_data(serpapi_news)
            if not serpapi_normalized:
                logger.warning("  ⚠️  SERPAPI normalization produced 0 items")
                fetch_errors['serpapi'] = "normalization_failed"
            all_news.extend(serpapi_normalized)
            source_counts['serpapi'] = len(serpapi_normalized)
            logger.info(f"  ✅ SERPAPI: {len(serpapi_normalized)} items")
        except Exception as e:
            logger.error(f"  ❌ SERPAPI failed completely: {e}")
            fetch_errors['serpapi'] = str(e)
            source_counts['serpapi'] = 0

        # Summary of fetched news
        total_fetched = len(all_news)
        logger.info(f"  📊 Total fetched: {total_fetched} news items")

        if total_fetched == 0:
            logger.error("❌ CRITICAL: No news items fetched from any source!")
            return source_counts

        # 1.4: Store all news in database
        logger.info(f"  💾 Storing {total_fetched} news items in database...")
        inserted_count = insert_geo_news_batch(all_news)

        # Report storage success rate
        if inserted_count == 0:
            logger.error("❌ CRITICAL: Zero news items stored in database!")
        elif inserted_count < total_fetched:
            loss_rate = ((total_fetched - inserted_count) / total_fetched) * 100
            logger.warning(f"⚠️  Storage loss: {loss_rate:.1f}% ({total_fetched - inserted_count} items not stored)")
        else:
            logger.info(f"✅ Step 1 complete: {inserted_count} news items stored")

        return source_counts

    def step2_extract_entities_and_generate_insights(
        self,
        hours_back: int = 24,
        limit: int = 50
    ) -> Tuple[List[Dict], List[Dict]]:
        """Step 2: Extract entities and generate insights (without storing).

        Args:
            hours_back: Hours to look back for news
            limit: Maximum number of news items to process

        Returns:
            Tuple of (all_entities, insights)
        """

        logger.info(f"🧠 Step 2: Extracting entities & generating insights...")

        # 2.1: Get recent news from database
        logger.info(f"  📊 Fetching recent news from DB...")
        recent_news = get_recent_news(hours_back=hours_back, limit=limit)

        if not recent_news:
            logger.warning("  ⚠️  No recent news found in database")
            return [], []

        logger.info(f"  ✅ Found {len(recent_news)} news items")

        # 2.2: Extract entities from each news
        logger.info(f"  🧠 Extracting entities from {len(recent_news)} news items...")
        all_entities = []

        for i, news in enumerate(recent_news, 1):
            logger.info(f"    Processing {i}/{len(recent_news)}: {news.get('title', 'N/A')[:50]}...")

            # Extract entities using Gemini
            entities = self.entity_extractor.extract_entities(news)

            # Store entities in database
            news_id = news.get('id')
            if entities and news_id:
                inserted_count = insert_entities_batch(
                    news_id=news_id,
                    entities=entities,
                    model_used=self.entity_extractor.model
                )
                logger.info(f"      💾 Stored {inserted_count} entities to DB")

            # Add news_id to each entity
            for entity in entities:
                entity['news_id'] = news_id

            all_entities.extend(entities)

        logger.info(f"  ✅ Extracted {len(all_entities)} entities total")

        # 2.3: Generate insights from entities
        logger.info("  💡 Generating insights from entities...")
        insights = self._generate_insights_from_entities(recent_news, all_entities)

        logger.info(f"  ✅ Generated {len(insights)} insights")

        return all_entities, insights

    def _generate_insights_from_entities(
        self,
        news_list: List[Dict],
        entities: List[Dict]
    ) -> List[Dict]:
        """Generate insights from extracted entities.

        Args:
            news_list: List of news items
            entities: List of extracted entities

        Returns:
            List of generated insights
        """

        insights = []

        # Group entities by name
        entity_groups = {}
        for entity in entities:
            name = entity.get('entity_name', 'unknown')
            if name not in entity_groups:
                entity_groups[name] = []
            entity_groups[name].append(entity)

        # Generate insight for each high-impact entity
        for entity_name, entity_list in entity_groups.items():
            # Calculate aggregate metrics
            impacts = [e.get('impact', 'neutral') for e in entity_list]
            confidences = [e.get('confidence', 0.5) for e in entity_list]

            # Determine overall impact
            negative_count = impacts.count('negative')
            positive_count = impacts.count('positive')
            total_count = len(impacts)

            if negative_count > positive_count:
                impact_level = 'high' if negative_count >= total_count * 0.7 else 'medium'
            elif positive_count > negative_count:
                impact_level = 'positive' if positive_count >= total_count * 0.7 else 'medium'
            else:
                impact_level = 'medium'

            # Average confidence
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

            # Collect all affected sectors/regions (NO tickers - those will be mapped separately)
            all_sectors = set()
            all_regions = set()
            source_news_ids = set()

            for entity in entity_list:
                all_sectors.update(entity.get('sectors', []))
                all_regions.update(entity.get('regions', []))
                source_news_ids.add(entity.get('news_id'))

            # Generate insight (without tickers - those are mapped separately via ticker entities)
            insight = {
                'title': f"{entity_name}: {'Risk' if impact_level in ['high', 'medium'] else 'Opportunity'} Analysis",
                'summary': self._generate_insight_summary(entity_name, entity_list),
                'impact_level': impact_level,
                'confidence': round(avg_confidence, 2),
                'related_entities': [entity_name],
                'related_sectors': list(all_sectors),
                'related_regions': list(all_regions),
                'affected_tickers': [],  # Empty - populated later via ticker entity mapping
                'source_news_ids': list(source_news_ids),
                'source_count': len(source_news_ids)
            }

            insights.append(insight)

        # Sort by impact level and confidence
        impact_order = {'critical': 0, 'high': 1, 'positive': 2, 'medium': 3, 'low': 4}
        insights.sort(key=lambda x: (impact_order.get(x['impact_level'], 5), -x['confidence']))

        return insights[:10]  # Top 10 insights

    def _generate_insight_summary(self, entity_name: str, entities: List[Dict]) -> str:
        """Generate insight summary from entities.

        Args:
            entity_name: Name of the entity
            entities: List of entities for this name

        Returns:
            Generated summary
        """

        # Count impacts
        negative_count = sum(1 for e in entities if e.get('impact') == 'negative')
        positive_count = sum(1 for e in entities if e.get('impact') == 'positive')

        # Get top sectors
        all_sectors = []
        for e in entities:
            all_sectors.extend(e.get('sectors', []))

        from collections import Counter
        sector_counts = Counter(all_sectors)
        top_sectors = [s for s, c in sector_counts.most_common(3)]

        # Generate summary
        if negative_count > positive_count:
            summary = f"Negative developments for {entity_name}. "
            if top_sectors:
                summary += f"Affected sectors include: {', '.join(top_sectors)}. "
            summary += f"Based on {len(entities)} news items indicating {'high' if negative_count >= len(entities) * 0.7 else 'moderate'} downside risk."
        elif positive_count > negative_count:
            summary = f"Positive developments for {entity_name}. "
            if top_sectors:
                summary += f"Beneficial sectors include: {', '.join(top_sectors)}. "
            summary += f"Based on {len(entities)} news items indicating {'strong' if positive_count >= len(entities) * 0.7 else 'moderate'} upside potential."
        else:
            summary = f"Mixed signals for {entity_name}. "
            if top_sectors:
                summary += f"Relevant sectors: {', '.join(top_sectors)}. "
            summary += f"Based on {len(entities)} news items with balanced sentiment."

        return summary

    def run_pipeline(self, hours_back: int = 24) -> Dict:
        """Run complete pipeline (steps 1 & 2).

        Args:
            hours_back: Hours to look back for news

        Returns:
            Dictionary with pipeline results
        """

        logger.info("="*70)
        logger.info("🚀 RUNNING GEOMACRO PROCESSING PIPELINE")
        logger.info("="*70)

        start_time = datetime.now()

        # Step 1: Fetch and store news
        source_counts = self.step1_fetch_and_store_news(hours_back=hours_back)

        # Step 2: Extract entities and generate insights
        all_entities, insights = self.step2_extract_entities_and_generate_insights(
            hours_back=hours_back,
            limit=100
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Results
        results = {
            'duration_seconds': duration,
            'news_stored': sum(source_counts.values()),
            'source_counts': source_counts,
            'entities_extracted': len(all_entities),
            'insights_generated': len(insights),
            'insights': insights  # Top insights (not stored yet)
        }

        logger.info("="*70)
        logger.info("✅ PIPELINE COMPLETE")
        logger.info(f"   News stored: {results['news_stored']}")
        logger.info(f"   Entities extracted: {results['entities_extracted']}")
        logger.info(f"   Insights generated: {results['insights_generated']}")
        logger.info(f"   Duration: {duration:.1f}s")
        logger.info("="*70)

        return results


def run_geomacro_pipeline(hours_back: int = 24) -> Dict:
    """Convenience function to run the complete pipeline.

    Args:
        hours_back: Hours to look back for news

    Returns:
        Dictionary with pipeline results
    """

    processor = GeoMacroProcessor()
    return processor.run_pipeline(hours_back=hours_back)
