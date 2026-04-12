#!/usr/bin/env python3
"""
Generate embeddings for all news items.

One-time batch process to generate embeddings for existing news.
Run this after creating the news_embeddings table.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from dotenv import load_dotenv
from tqdm import tqdm

from trading_mvp.core.db_news_embeddings import (
    create_news_embeddings_table,
    get_unembedded_news,
    save_news_embedding,
    count_news_embeddings
)
from trading_mvp.core.db_geo_news import get_recent_news
from trading_mvp.core.gemini_embeddings import generate_embeddings_batch

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def generate_news_embeddings(batch_size: int = 50):
    """Generate embeddings for all news that don't have them yet.

    Args:
        batch_size: Number of embeddings to generate per API call
    """

    # Create table if not exists
    create_news_embeddings_table()

    # Get current count
    current_count = count_news_embeddings()
    logger.info(f"Current news embeddings: {current_count}")

    # Get unembedded news
    all_news = get_recent_news(hours_back=168)  # Last 7 days
    all_news_ids = [news['id'] for news in all_news]

    unembedded_ids = get_unembedded_news(limit=len(all_news_ids))
    logger.info(f"Unembedded news: {len(unembedded_ids)}")

    if not unembedded_ids:
        logger.info("✅ All news already have embeddings!")
        return

    # Process in batches
    total_batches = (len(unembedded_ids) + batch_size - 1) // batch_size

    for i in range(0, len(unembedded_ids), batch_size):
        batch_ids = unembedded_ids[i:i + batch_size]
        batch_num = i // batch_size + 1

        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_ids)} news)...")

        # Get news content
        batch_news = []
        for news_id in batch_ids:
            news = next((n for n in all_news if n['id'] == news_id), None)
            if news:
                # Combine title + summary for embedding
                text = f"{news.get('title', '')} {news.get('summary', '')}"
                batch_news.append({
                    'id': news_id,
                    'text': text
                })

        if not batch_news:
            continue

        # Generate embeddings
        try:
            texts = [item['text'] for item in batch_news]
            embeddings = generate_embeddings_batch(
                texts,
                task_type="SEMANTIC_SIMILARITY",
                output_dimensionality=768
            )

            # Save embeddings
            saved_count = 0
            for item, embedding in zip(batch_news, embeddings):
                if save_news_embedding(item['id'], embedding):
                    saved_count += 1

            logger.info(f"  ✅ Saved {saved_count}/{len(batch_news)} embeddings")

        except Exception as e:
            logger.error(f"  ❌ Failed to generate embeddings for batch {batch_num}: {e}")
            continue

    # Final count
    final_count = count_news_embeddings()
    logger.info(f"\n✅ EMBEDDING GENERATION COMPLETE")
    logger.info(f"   Before: {current_count}")
    logger.info(f"   After: {final_count}")
    logger.info(f"   Generated: {final_count - current_count} new embeddings")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate embeddings for news")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for API calls")
    parser.add_argument("--hours-back", type=int, default=168, help="Hours to look back for news")

    args = parser.parse_args()

    logger.info("="*70)
    logger.info("🔄 NEWS EMBEDDING GENERATION")
    logger.info("="*70)
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Time window: Last {args.hours_back} hours")
    logger.info("")

    generate_news_embeddings(batch_size=args.batch_size)
