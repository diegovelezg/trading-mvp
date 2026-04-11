#!/usr/bin/env python3
"""
PASO 0: Extracción y Validación de Noticias

Este módulo garantiza que SIEMPRE haya noticias frescas antes de operar.
Es el PRIMER paso obligatorio del workflow y puede fallar el pipeline completo.
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NewsExtractionError(Exception):
    """Excepción cuando la extracción de noticias falla."""
    pass


class NewsValidationError(Exception):
    """Excepción cuando las noticias no pasan validación."""
    pass


def validate_news_freshness(news_items: List[Dict], max_age_hours: int = 24) -> bool:
    """Validar que las noticias sean lo suficientemente recientes.

    Args:
        news_items: Lista de noticias
        max_age_hours: Antigüedad máxima en horas (default: 24)

    Returns:
        True si las noticias son válidas

    Raises:
        NewsValidationError: Si las noticias no son válidas
    """
    if not news_items:
        raise NewsValidationError("No news items provided")

    # Validar cantidad mínima
    if len(news_items) < 10:
        raise NewsValidationError(
            f"Insufficient news items: {len(news_items)} < 10 minimum required"
        )

    # Validar antigüedad
    cutoff = datetime.now().replace(tzinfo=None) - timedelta(hours=max_age_hours)
    recent_count = 0

    for news in news_items:
        # Soportar ambos nombres de campo por compatibilidad
        published_date = news.get('published_at') or news.get('published_date')
        if published_date:
            if isinstance(published_date, str):
                published_date = datetime.fromisoformat(published_date)

            # Normalizar a naive datetime para comparación
            if published_date.tzinfo is not None:
                published_date = published_date.replace(tzinfo=None)

            if published_date > cutoff:
                recent_count += 1

    freshness_ratio = recent_count / len(news_items)

    if freshness_ratio < 0.5:
        raise NewsValidationError(
            f"News too old: {recent_count}/{len(news_items)} items "
            f"are from the last {max_age_hours}h "
            f"({freshness_ratio:.1%} < 50% required)"
        )

    logger.info(
        f"✅ News validation passed: {len(news_items)} items, "
        f"{freshness_ratio:.1%} recent (last {max_age_hours}h)"
    )

    return True


def extract_and_validate_news(
    hours_back: int = 48,
    min_news_count: int = 10,
    max_age_hours: int = 24
) -> Dict:
    """PASO 0: Extraer y validar noticias antes de operar.

    Este es el PRIMER paso obligatorio del workflow.
    Si falla, NO debe continuar con el análisis ni mucho menos operar.

    Args:
        hours_back: Horas hacia atrás para buscar noticias
        min_news_count: Cantidad mínima de noticias requeridas
        max_age_hours: Antigüedad máxima aceptable

    Returns:
        Dict con:
            - success: True si exitoso
            - news_items: Lista de noticias extraídas
            - extraction_timestamp: Timestamp de extracción
            - stats: Métricas de extracción

    Raises:
        NewsExtractionError: Si la extracción falla
        NewsValidationError: Si las noticias no validan
    """
    logger.info("="*70)
    logger.info("📰 PASO 0: NEWS EXTRACTION AND VALIDATION")
    logger.info("="*70)
    logger.info(f"⏰ Time window: Last {hours_back} hours")
    logger.info(f"📊 Min news required: {min_news_count}")
    logger.info(f"⚡ Max news age: {max_age_hours} hours")
    logger.info("")

    start_time = datetime.now()

    try:
        # 1. Extraer noticias de Supabase
        logger.info("📥 Step 0.1: Extracting news from Supabase...")

        from trading_mvp.core.db_geo_news import get_recent_news

        news_items = get_recent_news(hours_back=hours_back)

        if not news_items:
            raise NewsExtractionError(
                "No news items returned from Supabase. "
                "Check database connection or data availability."
            )

        logger.info(f"   ✅ Extracted {len(news_items)} news items")

        # 2. Validar frescura
        logger.info("🔍 Step 0.2: Validating news freshness...")

        validate_news_freshness(
            news_items=news_items,
            max_age_hours=max_age_hours
        )

        # 3. Calcular estadísticas
        logger.info("📊 Step 0.3: Computing extraction statistics...")

        sources = set(n.get('source', 'Unknown') for n in news_items)
        entities_count = sum(
            len(n.get('entities', []))
            for n in news_items
            if isinstance(n.get('entities'), list)
        )

        # Noticias únicas (por título)
        unique_titles = set(n.get('title', '') for n in news_items)
        duplicates = len(news_items) - len(unique_titles)

        stats = {
            'total_news': len(news_items),
            'unique_news': len(unique_titles),
            'duplicates': duplicates,
            'sources': list(sources),
            'source_count': len(sources),
            'total_entities': entities_count,
            'avg_entities_per_news': entities_count / len(news_items) if news_items else 0
        }

        logger.info(f"   📰 Total news: {stats['total_news']}")
        logger.info(f"   🆕 Unique news: {stats['unique_news']}")
        logger.info(f"   🔁 Duplicates: {stats['duplicates']}")
        logger.info(f"   📰 Sources: {stats['source_count']} ({', '.join(sources)})")
        logger.info(f"   🏷️  Total entities: {stats['total_entities']}")
        logger.info(f"   📊 Avg entities/news: {stats['avg_entities_per_news']:.1f}")

        # 4. Validar calidad de datos
        logger.info("✅ Step 0.4: Validating data quality...")

        required_fields = ['id', 'title', 'published_at', 'source']
        missing_fields = []

        for i, news in enumerate(news_items[:10]):  # Check first 10
            for field in required_fields:
                if not news.get(field):
                    missing_fields.append(f"News #{i} missing field: {field}")

        if missing_fields:
            raise NewsValidationError(
                f"Data quality issues detected:\n" + "\n".join(missing_fields[:5])
            )

        logger.info("   ✅ All required fields present")

        # 5. Compilar resultado
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            'success': True,
            'news_items': news_items,
            'extraction_timestamp': datetime.now().isoformat(),
            'stats': stats,
            'duration_seconds': duration,
            'validation_checks': {
                'min_count_passed': len(news_items) >= min_news_count,
                'freshness_passed': True,  # Already validated
                'data_quality_passed': True  # Already validated
            }
        }

        logger.info("")
        logger.info("="*70)
        logger.info(f"✅ NEWS EXTRACTION COMPLETE ({duration:.1f}s)")
        logger.info("="*70)

        return result

    except Exception as e:
        error_msg = f"News extraction failed: {str(e)}"
        logger.error(f"❌ {error_msg}")

        # CRÍTICO: Retornar failure explícito
        # NO debe fallar silenciosamente
        return {
            'success': False,
            'error': error_msg,
            'error_type': type(e).__name__,
            'extraction_timestamp': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }
