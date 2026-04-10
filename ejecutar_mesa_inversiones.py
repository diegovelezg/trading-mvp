#!/usr/bin/env python3
"""Ejecutar la Mesa de Inversiones completa usando los Agentes."""

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
    """Ejecutar mesa de inversiones con los agentes."""

    # Importar después de configurar logging
    sys.path.insert(0, os.path.abspath('scripts'))
    sys.path.insert(0, os.path.abspath('.'))

    logger.info("\n" + "="*70)
    logger.info("🏛️  MESA DE INVERSIONES - AGENTES AUTÓNOMOS")
    logger.info("="*70 + "\n")

    try:
        # Importar el script de la mesa de inversiones
        import importlib.util
        script_path = os.path.join('scripts', 'run_investment_desk.py')

        spec = importlib.util.spec_from_file_location("run_investment_desk", script_path)
        desk_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(desk_module)

        # Ejecutar la mesa de inversiones
        # Esto ejecutará: Discovery → Macro Analysis → Bull/Bear/Risk Agents → CIO → Decision Agent → Execution
        result = desk_module.run_investment_desk(hours_back=48)

        if result.get('success'):
            logger.info("\n" + "="*70)
            logger.info("✅ MESA DE INVERSIONES COMPLETADA")
            logger.info("="*70)

            # Mostrar resumen
            logger.info(f"\n📊 RESUMEN EJECUTIVO:")
            logger.info(f"   • Tickers analizados: {result['analyzed_tickers']}/{result['total_tickers']}")
            logger.info(f"   • Sentimiento global: {result['overall_sentiment']}")
            logger.info(f"   • Confianza promedio: {result['avg_confidence']:.2%}")
            logger.info(f"   • Noticias analizadas: {result['total_news_analyzed']}")
            logger.info(f"   • Entidades detectadas: {result['total_entities_found']}")

            # Mostrar recomendaciones
            if result.get('recommendations'):
                logger.info(f"\n🎯 RECOMENDACIONES DE LA MESA:")
                for rec in result['recommendations']:
                    logger.info(f"   {rec['action']}: {', '.join(rec['tickers'])}")
                    logger.info(f"      {rec['rationale']}")

            # Mostrar decisiones del agente
            if result.get('agent_decisions'):
                logger.info(f"\n🤖 DECISIONES DEL AGENTE:")
                for decision in result['agent_decisions']:
                    logger.info(f"   {decision['ticker']}: {decision['action']}")
                    logger.info(f"      Decisión: {decision['decision']}")
                    logger.info(f"      Razón: {decision['rationale'][:80]}...")

                    if decision.get('position_size'):
                        logger.info(f"      Tamaño posición: ${decision['position_size']:.2f}")
                    if decision.get('entry_price'):
                        logger.info(f"      Precio entrada: ${decision['entry_price']:.2f}")

            logger.info(f"\n⏰ Duración: {result['duration_seconds']}s")
            logger.info(f"📝 Audit Trail ID: {result.get('desk_run_id', 'N/A')}")

            return 0
        else:
            logger.error(f"\n❌ LA MESA FALLÓ: {result.get('error')}")
            return 1

    except Exception as e:
        logger.error(f"\n❌ Error ejecutando mesa de inversiones: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
