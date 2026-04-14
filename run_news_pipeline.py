#!/usr/bin/env python3
"""Ejecutar el pipeline completo de recopilación de noticias."""

import sys
import logging

# Configurar logging para ver TODO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Ejecutar pipeline completo."""
    from trading_mvp.core.geo_macro_processor import run_pipeline

    logger.info("\n" + "="*70)
    logger.info("🚀 EJECUTANDO PIPELINE COMPLETO DE NOTICIAS")
    logger.info("="*70 + "\n")

    try:
        # Ejecutar pipeline con las últimas 24 horas
        results = run_pipeline(hours_back=24)

        logger.info("\n" + "="*70)
        logger.info("📊 RESULTADOS DEL PIPELINE")
        logger.info("="*70)

        logger.info(f"⏱️  Duración: {results['duration_seconds']:.1f}s")
        logger.info(f"📰 Noticias almacenadas: {results['news_count']}")
        logger.info(f"🧠 Embeddings generados: {results['embeddings_count']}")
        logger.info(f"💡 Listos para búsqueda semántica")
        logger.info("\n📈 Por fuente:")
        for source, count in results['source_counts'].items():
            logger.info(f"   - {source}: {count} items")

        # Evaluar éxito
        if results['news_count'] == 0:
            logger.warning("\n⚠️  No se almacenaron nuevas noticias (posibles duplicados).")
            return 0

        total_fetched = sum(results['source_counts'].values())
        if results['news_count'] < total_fetched * 0.1:
            logger.info(f"\nℹ️  Baja tasa de almacenamiento ({results['news_count']}/{total_fetched}): La mayoría son noticias ya existentes.")

        logger.info("\n✅ PIPELINE COMPLETADO EXITOSAMENTE")
        return 0

    except Exception as e:
        logger.error(f"\n❌ Error ejecutando pipeline: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
