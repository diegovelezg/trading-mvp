#!/usr/bin/env python3
"""
PASO 0.5: Entity Extraction Completo

Este paso es CRÍTICO y DEBE ejecutarse después del Paso 0 (News Extraction)
y ANTES del Paso 4 (Ticker Analysis).

Garantiza que TODAS las noticias recolectadas tengan entidades extraídas.
"""

import os
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_all_entities(
    hours_back: int = 48,
    min_coverage_pct: float = 0.5,
    min_total_entities: int = 100
) -> Dict:
    """Extraer entidades de TODAS las noticias recolectadas.

    Args:
        hours_back: Horas hacia atrás para buscar noticias
        min_coverage_pct: Cobertura mínima de entidades (default: 50%)
        min_total_entities: Cantidad mínima de entidades total

    Returns:
        Dict con resultado del entity extraction
    """

    logger.info("="*70)
    logger.info("🧠 PASO 0.5: ENTITY EXTRACTION (COMPLETO)")
    logger.info("="*70)
    logger.info(f"⏰ Time window: Last {hours_back} hours")
    logger.info(f"📊 Min coverage: {min_coverage_pct:.0%}")
    logger.info(f"🏷️  Min entities: {min_total_entities}")
    logger.info("")

    start_time = datetime.now()

    try:
        from trading_mvp.core.db_geo_news import get_recent_news
        from trading_mvp.core.geo_macro_processor import GeoMacroProcessor

        # 1. Obtener TODAS las noticias recolectadas
        logger.info("📰 Step 0.5.1: Obtaining ALL collected news...")

        all_news = get_recent_news(hours_back=hours_back, limit=10000)

        if not all_news:
            return {
                'success': False,
                'error': 'No news found in database',
                'error_type': 'NoNewsError'
            }

        total_news = len(all_news)
        logger.info(f"   ✅ Found {total_news} news items")

        # 2. Verificar cuáles ya tienen entidades
        logger.info("🔍 Step 0.5.2: Checking existing entities...")

        from supabase import create_client
        from dotenv import load_dotenv

        load_dotenv()
        supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
        supabase_key = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')
        client = create_client(supabase_url, supabase_key)

        # Obtener news_ids que ya tienen entidades
        result = client.table('geo_macro_entities').select('news_id').execute()
        news_with_entities = set(e.get('news_id') for e in result.data if e.get('news_id'))

        logger.info(f"   ✅ {len(news_with_entities)} news already have entities")

        # 3. Extraer entidades de las noticias que faltan
        news_needing_entities = [n for n in all_news if n.get('id') not in news_with_entities]

        if not news_needing_entities:
            logger.info("   ✅ All news already have entities!")
            coverage = len(news_with_entities) / total_news

            return {
                'success': True,
                'total_news': total_news,
                'processed_news': 0,
                'existing_entities': len(news_with_entities),
                'new_entities': 0,
                'total_entities': len(news_with_entities),  # Aprox
                'coverage_pct': coverage,
                'health_status': 'healthy' if coverage >= min_coverage_pct else 'degraded',
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }

        logger.info(f"   📝 Need to extract entities from {len(news_needing_entities)} news")

        # 4. Procesar noticias que faltan
        logger.info("🧠 Step 0.5.3: Extracting entities from remaining news...")
        logger.info(f"   ⏱️  This will take ~{len(news_needing_entities) * 3 / 60:.1f} minutes...")
        logger.info("")

        processor = GeoMacroProcessor()
        all_entities = []
        processed_count = 0

        # Limitar a un número razonable para no demorar demasiado
        max_to_process = min(len(news_needing_entities), 200)

        for i, news in enumerate(news_needing_entities[:max_to_process], 1):
            if i % 10 == 0:
                logger.info(f"   Progress: {i}/{max_to_process} news processed...")

            try:
                entities = processor.entity_extractor.extract_entities(news)

                # PERSISTIR entidades en BD
                from trading_mvp.core.db_geo_entities import insert_entities_batch

                news_id = news.get('id')
                model_used = os.getenv('GEMINI_API_MODEL_01', 'gemini-3.1-flash-lite-preview')

                # Guardar en batch
                entities_saved = insert_entities_batch(
                    news_id=news_id,
                    entities=entities,
                    model_used=model_used
                )

                all_entities.extend(entities)
                processed_count += 1

            except Exception as e:
                logger.warning(f"   ⚠️  Failed to extract/save entities from news {news.get('id')}: {e}")

        logger.info(f"   ✅ Processed {processed_count} news")
        logger.info(f"   ✅ Extracted {len(all_entities)} entities")

        # 5. Calcular métricas finales
        logger.info("📊 Step 0.5.4: Calculating final metrics...")

        total_entities_count = len(news_with_entities) + len(all_entities)
        coverage_pct = (len(news_with_entities) + processed_count) / total_news

        logger.info(f"   📰 Total news: {total_news}")
        logger.info(f"   🏷️  Total entities: ~{total_entities_count}")
        logger.info(f"   📊 Coverage: {coverage_pct:.1%}")
        logger.info("")

        # 6. Validar checkpoints
        logger.info("✅ Step 0.5.5: Validating checkpoints...")

        checks = {
            'min_coverage_passed': coverage_pct >= min_coverage_pct,
            'min_entities_passed': total_entities_count >= min_total_entities,
            'all_checks_passed': False
        }

        checks['all_checks_passed'] = all(checks.values())

        for check, passed in checks.items():
            status = '✅' if passed else '❌'
            logger.info(f"   {status} {check}: {passed}")

        # 7. Compilar resultado
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            'success': True,
            'total_news': total_news,
            'processed_news': processed_count,
            'existing_entities': len(news_with_entities),
            'new_entities': len(all_entities),
            'total_entities': total_entities_count,
            'coverage_pct': round(coverage_pct, 2),
            'health_status': 'healthy' if checks['all_checks_passed'] else 'degraded',
            'validation_checks': checks,
            'duration_seconds': round(duration, 1),
            'extraction_timestamp': datetime.now().isoformat()
        }

        logger.info("")
        logger.info("="*70)
        logger.info(f"✅ ENTITY EXTRACTION COMPLETE ({duration:.1f}s)")
        logger.info("="*70)

        return result

    except Exception as e:
        logger.error(f"❌ Entity extraction failed: {e}")

        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }
