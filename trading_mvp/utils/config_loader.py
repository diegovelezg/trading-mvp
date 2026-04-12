"""
Configuration Loader

Carga configuraciones desde archivos JSON externos.
SSOT: Configuración externalizada, no hardcoded en código.
"""

import os
import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Ruta base del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_watchlist_config() -> Dict[str, Any]:
    """
    Carga configuración de watchlists por defecto.

    Returns:
        Dict con configuración de watchlists

    Examples:
        >>> config = load_watchlist_config()
        >>> config["DEFAULT_WATCHLIST_ID"]
        2
    """
    config_path = os.path.join(CONFIG_DIR, "watchlist_config.json")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {"DEFAULT_WATCHLIST_ID": 1}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing watchlist_config.json: {e}")
        return {"DEFAULT_WATCHLIST_ID": 1}


def get_default_watchlist_id() -> int:
    """
    Obtiene el ID de la watchlist por defecto.

    Returns:
        ID de la watchlist por defecto

    Examples:
        >>> get_default_watchlist_id()
        2
    """
    config = load_watchlist_config()
    return config.get("DEFAULT_WATCHLIST_ID", 1)


def get_watchlist_info(watchlist_name: str) -> Dict[str, Any]:
    """
    Obtiene información de una watchlist por nombre.

    Args:
        watchlist_name: Nombre de la watchlist (ej: "ENERGIA_NUCLEAR")

    Returns:
        Dict con info de la watchlist o dict vacío si no existe

    Examples:
        >>> info = get_watchlist_info("ENERGIA_NUCLEAR")
        >>> info["id"]
        2
        >>> info["name"]
        'Energía Nuclear'
    """
    config = load_watchlist_config()
    return config.get("DEFAULT_WATCHLISTS", {}).get(watchlist_name, {})


# Variables globales cargadas al inicio (caching simple)
_TICKER_ENTITIES_CACHE = None
_WATCHLIST_CONFIG_CACHE = None


def get_ticker_entities_cached() -> Dict[str, List[str]]:
    """
    Obtiene entities cacheadas desde PostgreSQL (carga solo una vez).

    Returns:
        Dict con ticker → entidades
    """
    global _TICKER_ENTITIES_CACHE
    if _TICKER_ENTITIES_CACHE is None:
        _TICKER_ENTITIES_CACHE = load_ticker_entities()
    return _TICKER_ENTITIES_CACHE


def get_watchlist_config_cached() -> Dict[str, Any]:
    """
    Obtiene config de watchlists cacheada.

    Returns:
        Dict con configuración
    """
    global _WATCHLIST_CONFIG_CACHE
    if _WATCHLIST_CONFIG_CACHE is None:
        _WATCHLIST_CONFIG_CACHE = load_watchlist_config()
    return _WATCHLIST_CONFIG_CACHE


if __name__ == "__main__":
    # Tests
    print("Testing config loader...")

    # Test ticker entities
    entities = get_ticker_entities("AAPL")
    print(f"AAPL entities: {entities}")

    # Test watchlist config
    default_id = get_default_watchlist_id()
    print(f"Default watchlist ID: {default_id}")

    # Test watchlist info
    info = get_watchlist_info("ENERGIA_NUCLEAR")
    print(f"Nuclear watchlist info: {info}")

    print("✅ Config loader working!")
