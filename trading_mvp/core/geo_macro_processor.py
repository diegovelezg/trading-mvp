"""GeoMacro News Processing Pipeline: Steps 1 & 2

Step 1: Ingesta de noticias → geo_macro_news (raw)
Step 2: Generación de embeddings para búsqueda semántica
"""

import os
import logging
from typing import List, Dict, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# FORZAR SSOT: Recargar .env antes de cualquier importación de conectores
load_dotenv(override=True)

# Importar criterios de búsqueda (SSOT)
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.news_criteria import is_source_active, MAX_ITEMS_PER_CATEGORY

from trading_mvp.data_sources import GoogleNewsConnector
# SerpApiConnector eliminado/renamed a .DISABLED
# from trading_mvp.data_sources import SerpApiConnector

from trading_mvp.core.db_geo_news import (
    create_geo_macro_news_table,
    insert_geo_news_batch,
    get_recent_news,
    get_news_count_by_source
)
from trading_mvp.core.db_news_embeddings import (
    get_unembedded_news,
    save_news_embeddings_batch,
    create_news_embeddings_table,
    count_news_embeddings
)
from trading_mvp.core.gemini_embeddings import generate_embedding, generate_embeddings_batch

logger = logging.getLogger(__name__)

class GeoMacroProcessor:
    """Processor for geo_macro news ingestion and embedding generation."""

    def __init__(self):
        """Initialize processor."""
        # Initialize connectors (solo activos según config)
        self.google_connector = GoogleNewsConnector()

        # SERPAPI: Comentado/desactivado por ahora
        # self.serpapi_connector = SerpApiConnector()

        # Log active sources
        logger.info("✅ GeoMacroProcessor initialized")
        logger.info(f"   📰 Google News: {'✅' if is_source_active('google_news') else '❌'}")
        logger.info(f"   🔍 SERPAPI: {'✅' if is_source_active('serpapi') else '❌ (commented)'}")
        logger.info(f"   📊 Alpaca: ❌ (eliminated)")

    def step1_fetch_and_store_news(self, hours_back: int = 24) -> Dict[str, int]:
        """Step 1: Fetch and store news from all sources.

        Args:
            hours_back: Hours to look back for news

        Returns:
            Dictionary with source counts
        """
        logger.info("="*70)
        logger.info("📰 STEP 1: FETCH AND STORE NEWS")
        logger.info("="*70)

        # Ensure table exists
        create_geo_macro_news_table()

        source_counts = {}

        # 1.1: Fetch from Google News (USANDO CRITERIOS CENTRALIZADOS)
        if is_source_active('google_news'):
            try:
                logger.info("📡 Fetching from Google News RSS...")
                logger.info("   Using centralized criteria from config/news_criteria.py")

                google_raw = self.google_connector.fetch_all_categorized_news(max_items=MAX_ITEMS_PER_CATEGORY)
                google_normalized = self.google_connector.normalize_data(google_raw)

                if google_normalized:
                    inserted = insert_geo_news_batch(google_normalized)
                    source_counts['google'] = inserted
                    logger.info(f"   ✅ Google: {inserted} news stored")
            except Exception as e:
                logger.error(f"   ❌ Google failed: {e}")
                source_counts['google'] = 0
        else:
            logger.info("⏭️  Google News: Skipped (inactive in config)")

        # 1.2: SERPAPI (COMENTADO/DESACTIVADO)
        # if is_source_active('serpapi'):
        #     try:
        #         logger.info("📡 Fetching from SERPAPI...")
        #         serpapi_raw = self.serpapi_connector.fetch_data(
        #             query="geopolitical economic news",
        #             max_items=50
        #         )
        #         serpapi_normalized = self.serpapi_connector.normalize_data(serpapi_raw)
        #
        #         if serpapi_normalized:
        #             inserted = insert_geo_news_batch(serpapi_normalized)
        #             source_counts['serpapi'] = inserted
        #             logger.info(f"   ✅ SERPAPI: {inserted} news stored")
        #     except Exception as e:
        #         logger.error(f"   ❌ SERPAPI failed: {e}")
        #         source_counts['serpapi'] = 0

        total_stored = sum(source_counts.values())
        logger.info("")
        logger.info(f"📊 STEP 1 COMPLETE: {total_stored} total news stored")
        for source, count in source_counts.items():
            logger.info(f"   - {source}: {count}")
        logger.info("")

        return source_counts

    def step2_generate_embeddings_for_news(
        self,
        hours_back: int = 24,
        limit: int = 100,
        batch_size: int = 50
    ) -> Tuple[List[Dict], int]:
        """Step 2: Generate embeddings for all news without them.

        Args:
            hours_back: Hours to look back for news
            limit: Max news to process
            batch_size: Batch size for embedding generation

        Returns:
            (all_news, embeddings_generated_count)
        """
        logger.info("="*70)
        logger.info("🧠 STEP 2: GENERATE EMBEDDINGS FOR SEMANTIC SEARCH")
        logger.info("="*70)

        # Ensure table exists
        create_news_embeddings_table()

        # Get all recent news
        all_news = get_recent_news(hours_back=hours_back, limit=limit)
        logger.info(f"📰 Total news found: {len(all_news)}")

        if not all_news:
            logger.warning("⚠️  No news found, skipping embedding generation")
            return [], 0

        # Get news without embeddings
        all_news_ids = [news['id'] for news in all_news]
        unembedded_ids = get_unembedded_news(limit=len(all_news_ids))

        if not unembedded_ids:
            logger.info("✅ All news already have embeddings!")
            return all_news, len(all_news)

        logger.info(f"🎯 News to process: {len(unembedded_ids)}")

        # Create news map
        news_map = {news['id']: news for news in all_news}

        # Process in batches
        embeddings_generated = 0
        total_batches = (len(unembedded_ids) + batch_size - 1) // batch_size

        for i in range(0, len(unembedded_ids), batch_size):
            batch_ids = unembedded_ids[i:i + batch_size]
            batch_num = i // batch_size + 1

            logger.info(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch_ids)} news)...")

            # Prepare texts for embedding
            batch_data = []
            for news_id in batch_ids:
                news = news_map.get(news_id)
                if news:
                    text = f"{news.get('title', '')} {news.get('summary', '')}"
                    batch_data.append((news_id, text))

            if not batch_data:
                continue

            try:
                # Generate embeddings
                texts = [item[1] for item in batch_data]
                embeddings = generate_embeddings_batch(
                    texts,
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=768
                )

                # Save embeddings
                embeddings_data = [
                    (news_id, str(embedding), 768, 'gemini-embedding-001')
                    for (news_id, _), embedding in zip(batch_data, embeddings)
                ]

                saved = save_news_embeddings_batch(embeddings_data)
                embeddings_generated += saved

                logger.info(f"   ✅ Saved {saved}/{len(batch_data)} embeddings")

            except Exception as e:
                logger.error(f"   ❌ Failed batch {batch_num}: {e}")
                continue

        # Final stats
        total_embeddings = count_news_embeddings()
        logger.info("")
        logger.info("📊 STEP 2 COMPLETE")
        logger.info(f"   ✅ Embeddings generated: {embeddings_generated}")
        logger.info(f"   ✅ Total embeddings in DB: {total_embeddings}")
        logger.info("")

        return all_news, embeddings_generated


def run_pipeline(hours_back: int = 24) -> Dict:
    """Run complete pipeline (Steps 1 & 2).

    Args:
        hours_back: Hours to look back for news

    Returns:
        Pipeline results
    """
    start_time = datetime.now()

    logger.info("="*70)
    logger.info("🚀 GEOMACRO NEWS PIPELINE")
    logger.info("="*70)
    logger.info("")

    processor = GeoMacroProcessor()

    # Step 1: Fetch and store news
    source_counts = processor.step1_fetch_and_store_news(hours_back=hours_back)

    # Step 2: Generate embeddings
    all_news, embeddings_count = processor.step2_generate_embeddings_for_news(
        hours_back=hours_back,
        limit=100
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("="*70)
    logger.info("✅ PIPELINE COMPLETE")
    logger.info(f"   Duration: {duration:.1f}s")
    logger.info(f"   News stored: {sum(source_counts.values())}")
    logger.info(f"   Embeddings generated: {embeddings_count}")
    logger.info("="*70)

    return {
        'success': True,
        'duration_seconds': duration,
        'news_count': sum(source_counts.values()),
        'embeddings_count': embeddings_count,
        'source_counts': source_counts
    }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s'
    )

    result = run_pipeline(hours_back=24)
