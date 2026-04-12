#!/usr/bin/env python3
"""
Generate embeddings for tickers directly from metadata (name, sector, description).

This replaces the entity-based system with direct ticker embeddings.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import logging
from trading_mvp.core.db_ticker_embeddings import (
    save_ticker_entity_embeddings_batch,
    get_ticker_embeddings,
    get_embeddings_stats
)
from trading_mvp.core.gemini_embeddings import generate_embeddings_batch
from trading_mvp.core.dashboard_api_client import get_active_watchlists

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def generate_embeddings_for_ticker_from_metadata(ticker: str, name: str, sector: str, description: str, force_regenerate: bool = False) -> bool:
    """Generate embeddings for a ticker directly from metadata.

    Args:
        ticker: Ticker symbol
        name: Company name
        sector: Industry sector
        description: Company description
        force_regenerate: Regenerate even if already exist

    Returns:
        True if successful
    """
    logger.info(f"🔄 Processing {ticker}...")

    # Create text embeddings from different aspects
    texts_to_embed = [
        f"{ticker} - {name}",
        f"{name} - {sector}",
        f"{sector}: {description}",
        description[:500]  # Truncate if too long
    ]

    # Verify if already exist
    if not force_regenerate:
        existing_embeddings = get_ticker_embeddings(ticker)
        if len(existing_embeddings) >= len(texts_to_embed):
            logger.info(f"   ⏭️  Embeddings already exist (use --force to regenerate)")
            return True

    # Generate embeddings with Gemini
    logger.info(f"   Generating {len(texts_to_embed)} embeddings with Gemini...")
    try:
        embeddings = generate_embeddings_batch(
            texts_to_embed,
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=768
        )
    except Exception as e:
        logger.error(f"   ❌ Error generating embeddings: {e}")
        return False

    # Create meaningful labels for embeddings
    entity_labels = [
        f"{ticker}_symbol",
        f"{ticker}_name_sector",
        f"{ticker}_sector_context",
        f"{ticker}_description"
    ]

    # Create dict
    ticker_embeddings = {}
    for label, embedding in zip(entity_labels, embeddings):
        ticker_embeddings[label] = embedding

    # Save to database
    logger.info(f"   Saving to database...")
    saved_count = save_ticker_entity_embeddings_batch(ticker, ticker_embeddings)

    if saved_count == len(ticker_embeddings):
        logger.info(f"   ✅ Saved {saved_count} embeddings for {ticker}")
        return True
    else:
        logger.warning(f"   ⚠️  Partial save: {saved_count}/{len(ticker_embeddings)} embeddings")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate ticker embeddings from metadata'
    )
    parser.add_argument(
        '--ticker',
        type=str,
        help='Specific ticker to process (default: all from watchlists)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Regenerate embeddings even if they exist'
    )

    args = parser.parse_args()

    logger.info("="*70)
    logger.info("🧠 TICKER EMBEDDINGS GENERATOR (Metadata-based)")
    logger.info("="*70)
    logger.info("")

    # Get tickers to process
    if args.ticker:
        # Single ticker mode - need metadata
        logger.info("Single ticker mode requires manual metadata input")
        logger.info("Please use --ticker with a specific implementation")
        logger.info("Or run without --ticker to process all watchlist tickers")
        sys.exit(1)
    else:
        # Get all tickers from watchlists
        watchlists = get_active_watchlists()
        ticker_metadata = {}

        for wl in watchlists:
            for item in wl.get('items', []):
                ticker = item.get('ticker')
                if ticker and ticker not in ticker_metadata:
                    # Get metadata from item if available
                    ticker_metadata[ticker] = {
                        'ticker': ticker,
                        'name': item.get('company_name', ticker),
                        'sector': item.get('sector', 'Unknown'),
                        'description': item.get('description', f'{ticker} stock')
                    }

        tickers_to_process = list(ticker_metadata.keys())

    if not tickers_to_process:
        logger.error("❌ No tickers found in watchlists")
        sys.exit(1)

    logger.info(f"📊 Processing {len(tickers_to_process)} ticker(s)")
    logger.info("")

    # Statistics
    successful = 0
    failed = 0
    skipped = 0

    # Process each ticker
    for ticker in tickers_to_process:
        try:
            metadata = ticker_metadata[ticker]
            if generate_embeddings_for_ticker_from_metadata(
                ticker=ticker,
                name=metadata['name'],
                sector=metadata['sector'],
                description=metadata['description'],
                force_regenerate=args.force
            ):
                successful += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Failed to process {ticker}: {e}")
            failed += 1

        logger.info("")

    # Final statistics
    logger.info("="*70)
    logger.info("📊 GENERATION COMPLETE")
    logger.info("="*70)
    logger.info(f"   ✅ Successful: {successful}")
    logger.info(f"   ❌ Failed: {failed}")
    logger.info(f"   ⏭️  Skipped: {skipped}")
    logger.info("")

    # Database stats
    stats = get_embeddings_stats()
    if stats:
        logger.info("📊 Database Stats:")
        logger.info(f"   Total embeddings: {stats.get('total_embeddings', 0)}")
        logger.info(f"   Unique tickers: {stats.get('unique_tickers', 0)}")

    logger.info("="*70)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
