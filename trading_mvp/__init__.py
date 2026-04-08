"""Trading MVP: Biblioteca compartida para la Mesa de Inversión.

Este paquete contiene código compartido reutilizable por todos los subagentes:

- core: Utilidades base (DB, configuración, utils)
- analysis: Análisis de sentimiento y razonamiento
- news: Fuentes de datos externas (Alpaca, GDELT)
- execution: Ejecución de órdenes (Alpaca API)
- reporting: Generación de reportes (Trade Cards, performance)

Los subagentes específicos están en .claude/subagents/
"""

__version__ = "0.2.0"

# Módulos compartidos disponibles
__all__ = [
    "core",
    "analysis",
    "news",
    "execution",
    "reporting",
]
