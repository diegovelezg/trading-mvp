#!/usr/bin/env python3
"""Ejecutar solo el Step 1 del pipeline (fetch & store news) para evaluar arreglos."""

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
    """Ejecutar solo Step 1."""
    from trading_mvp.core.geo_macro_processor import GeoMacroProcessor

    logger.info("\n" + "="*70)
    logger.info("🚀 EJECUTANDO STEP 1: FETCH & STORE NEWS")
    logger.info("="*70 + "\n")

    try:
        processor = GeoMacroProcessor()

        # Ejecutar solo Step 1
        source_counts = processor.step1_fetch_and_store_news(hours_back=24)

        logger.info("\n" + "="*70)
        logger.info("📊 RESULTADOS STEP 1")
        logger.info("="*70)

        total_fetched = sum(source_counts.values())
        logger.info(f"📰 Total fetched: {total_fetched} items")
        logger.info("\nPor fuente:")
        for source, count in source_counts.items():
            logger.info(f"   - {source}: {count} items")

        if total_fetched == 0:
            logger.error("\n❌ CRÍTICO: No se pudo obtener ninguna noticia!")
            return 1

        logger.info("\n✅ STEP 1 COMPLETADO")
        return 0

    except Exception as e:
        logger.error(f"\n❌ Error en Step 1: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
