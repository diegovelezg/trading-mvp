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
    from trading_mvp.core.geo_macro_processor import run_geomacro_pipeline

    logger.info("\n" + "="*70)
    logger.info("🚀 EJECUTANDO PIPELINE COMPLETO DE NOTICIAS")
    logger.info("="*70 + "\n")

    try:
        # Ejecutar pipeline con las últimas 24 horas
        results = run_geomacro_pipeline(hours_back=24)

        logger.info("\n" + "="*70)
        logger.info("📊 RESULTADOS DEL PIPELINE")
        logger.info("="*70)

        logger.info(f"⏱️  Duración: {results['duration_seconds']:.1f}s")
        logger.info(f"📰 Noticias almacenadas: {results['news_stored']}")
        logger.info(f"🧠 Entidades extraídas: {results['entities_extracted']}")
        logger.info(f"💡 Insights generados: {results['insights_generated']}")
        logger.info("\n📈 Por fuente:")
        for source, count in results['source_counts'].items():
            logger.info(f"   - {source}: {count} items")

        # Evaluar éxito
        if results['news_stored'] == 0:
            logger.error("\n❌ CRÍTICO: No se almacenó ninguna noticia!")
            return 1

        total_fetched = sum(results['source_counts'].values())
        if results['news_stored'] < total_fetched * 0.5:
            logger.warning(f"\n⚠️  ALTA PÉRDIDA: Solo {results['news_stored']}/{total_fetched} noticias almacenadas")
            return 1

        logger.info("\n✅ PIPELINE COMPLETADO EXITOSAMENTE")
        return 0

    except Exception as e:
        logger.error(f"\n❌ Error ejecutando pipeline: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
