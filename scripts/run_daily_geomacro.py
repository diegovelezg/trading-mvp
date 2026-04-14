#!/usr/bin/env python3
"""
Daily GeoMacro News Pipeline

Este script debe ejecutarse 1 o más veces al día para:
1. Recolectar news de todas las fuentes
2. Generar embeddings para búsqueda semántica
3. Almacenar todo en la base de datos con timestamps

Uso:
    python run_daily_geomacro.py

Cron (ejecutar cada 6 horas):
    0 */6 * * * cd /path/to/trading-mvp && .venv/bin/python run_daily_geomacro.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('geomacro_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Set up environment
os.environ['ALPACA_PAPER_API_KEY'] = 'YOUR_ALPACA_PAPER_API_KEY'
os.environ['PAPER_API_SECRET'] = 'YOUR_ALPACA_SECRET_KEY'
os.environ['SERPAPI_API_KEY'] = 'YOUR_SERPAPI_API_KEY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCutHRoCMkN02KhsVYATzu5XRPjboQZxnc'
os.environ['GEMINI_API_MODEL_01'] = 'gemini-3.1-flash-lite-preview'

from trading_mvp.core.db_geo_news import create_geo_macro_news_table
from trading_mvp.core.geo_macro_processor import GeoMacroProcessor

def main():
    """Run the daily GeoMacro news pipeline."""

    logger.info("="*70)
    logger.info("🚀 DAILY GEOMACRO NEWS PIPELINE")
    logger.info("="*70)

    start_time = datetime.now()

    try:
        # 1. Create tables if needed
        logger.info("📋 Creating tables if needed...")
        create_geo_macro_news_table()

        # 2. Run pipeline (steps 1 & 2)
        logger.info("🔄 Running pipeline...")
        processor = GeoMacroProcessor()

        # Step 1: Fetch and store news
        source_counts = processor.step1_fetch_and_store_news(hours_back=24)

        # Step 2: Generate embeddings for semantic search
        all_news, embeddings_count = processor.step2_generate_embeddings_for_news(
            hours_back=24,
            limit=100
        )

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info("="*70)
        logger.info("✅ PIPELINE COMPLETE")
        logger.info(f"   Duration: {duration:.1f}s")
        logger.info(f"   News stored: {sum(source_counts.values())}")
        logger.info(f"   - Alpaca: {source_counts.get('alpaca', 0)}")
        logger.info(f"   - Google: {source_counts.get('google', 0)}")
        logger.info(f"   - SERPAPI: {source_counts.get('serpapi', 0)}")
        logger.info(f"   News processed: {len(all_news)}")
        logger.info(f"   Embeddings generated: {embeddings_count}")
        logger.info("="*70)

        return {
            'success': True,
            'duration_seconds': duration,
            'news_count': sum(source_counts.values()),
            'embeddings_count': embeddings_count
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    result = main()

    # Exit with error code if failed
    if not result.get('success'):
        sys.exit(1)
