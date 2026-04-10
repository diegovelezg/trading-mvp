#!/usr/bin/env python3
"""Ejecutar la mesa de inversiones completa."""

import sys
import os
import logging

# Configurar logging para ver TODO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def main():
    """Ejecutar mesa de inversiones completa."""
    # Importar después de configurar logging
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'scripts')))

    from run_investment_desk import run_investment_desk, print_investment_desk_report

    logger.info("\n" + "="*70)
    logger.info("🏛️  EJECUTANDO MESA DE INVERSIONES COMPLETA")
    logger.info("="*70 + "\n")

    try:
        # Ejecutar mesa de inversiones
        # Usará la primera watchlist disponible o el portfolio actual
        result = run_investment_desk(hours_back=48)

        if result.get('success'):
            # Imprimir reporte completo
            print_investment_desk_report(result)

            logger.info("\n✅ MESA DE INVERSIONES COMPLETADA EXITOSAMENTE")
            return 0
        else:
            logger.error(f"\n❌ MESA DE INVERSIONES FALLÓ: {result.get('error')}")
            return 1

    except Exception as e:
        logger.error(f"\n❌ Error ejecutando mesa de inversiones: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
