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

    # Asegurar PYTHONPATH correcto para desarrollo y producción
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    scripts_dir = os.path.join(current_dir, 'scripts')
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    logger.info("\n" + "="*70)
    logger.info("🏛️  MESA DE INVERSIONES - AGENTES AUTÓNOMOS")
    logger.info("="*70 + "\n")

    try:
        # Importar el script de la mesa de inversiones (con fail-fast)
        import importlib.util
        script_path = os.path.join('scripts', 'run_investment_desk.py')

        spec = importlib.util.spec_from_file_location("run_investment_desk", script_path)
        desk_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(desk_module)

        # Ejecutar la mesa de inversiones
        # PASO 0: News Extraction (fail if fails)
        # PASO 1-7: Analysis con fail-fast
        result = desk_module.run_investment_desk(hours_back=48)

        if result.get('success'):
            logger.info("\n" + "="*70)
            logger.info("✅ MESA DE INVERSIONES COMPLETADA")
            logger.info("="*70)

            # Mostrar resumen
            logger.info(f"\n📊 RESUMEN EJECUTIVO:")
            logger.info(f"   • Tickers analizados: {result.get('analyzed_tickers', 0)}/{result.get('total_tickers', 0)}")
            
            # Count aborted
            aborted = [d for d in result.get('agent_decisions', []) if d.get('decision') == 'ABORTED']
            if aborted:
                logger.warning(f"   • Tickers ABORTADOS: {len(aborted)} (Falta ADN o Quant)")
            
            logger.info(f"   • Sentimiento global: {result.get('overall_sentiment', 'N/A')}")

            avg_conf = result.get('avg_confidence')
            if avg_conf is not None:
                logger.info(f"   • Confianza promedio: {avg_conf:.2%}")

            logger.info(f"   • Noticias analizadas: {result.get('total_news_analyzed', 0)}")
            logger.info(f"   • Entidades detectadas: {result.get('total_entities_found', 0)}")


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

            logger.info(f"\n⏰ Duración: {result.get('duration_seconds', 'N/A')}s")
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
