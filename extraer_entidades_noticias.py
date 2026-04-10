#!/usr/bin/env python3
"""Ejecutar Step 2 del pipeline: Extracción de entidades de las noticias."""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Ejecutar extracción de entidades de noticias recientes."""
    # Importar después de configurar logging
    sys.path.insert(0, os.path.abspath('.'))

    from trading_mvp.core.geo_macro_processor import GeoMacroProcessor

    logger.info("\n" + "="*70)
    logger.info("🧠 EXTRAYENDO ENTIDADES DE NOTICIAS RECIENTES")
    logger.info("="*70 + "\n")

    try:
        processor = GeoMacroProcessor()

        # Ejecutar Step 2: Extract entities & generate insights
        logger.info("🧠 Iniciando extracción de entidades...")

        all_entities, insights = processor.step2_extract_entities_and_generate_insights(
            hours_back=24,
            limit=100  # Procesar hasta 100 noticias recientes
        )

        logger.info("\n" + "="*70)
        logger.info("✅ EXTRACCIÓN DE ENTIDADES COMPLETADA")
        logger.info("="*70)

        logger.info(f"\n📊 RESULTADOS:")
        logger.info(f"   • Entidades extraídas: {len(all_entities)}")
        logger.info(f"   • Insights generados: {len(insights)}")

        if all_entities:
            logger.info(f"\n📋 Top 5 entidades:")
            for i, entity in enumerate(all_entities[:5], 1):
                logger.info(f"   {i}. {entity.get('entity_name', 'N/A')} - {entity.get('impact', 'neutral')}")

        if insights:
            logger.info(f"\n💡 Top 3 insights:")
            for i, insight in enumerate(insights[:3], 1):
                logger.info(f"   {i}. {insight.get('title', 'N/A')}")

        logger.info(f"\n✅ Ahora las noticias tienen sus entidades extraídas")
        logger.info(f"✅ La próxima ejecución de la mesa de inversiones usará estas entidades")

        return 0

    except Exception as e:
        logger.error(f"\n❌ Error extrayendo entidades: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
