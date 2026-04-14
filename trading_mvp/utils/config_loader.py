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
    """
    config = load_watchlist_config()
    return config.get("DEFAULT_WATCHLIST_ID", 1)


def get_default_watchlist_info() -> Dict[str, Any]:
    """
    Obtiene información de la watchlist por defecto.

    Returns:
        Dict con info de la watchlist o dict vacío si no existe
    """
    config = load_watchlist_config()
    return config.get("DEFAULT_WATCHLIST", {})


# Variables globales cargadas al inicio (caching simple)
_WATCHLIST_CONFIG_CACHE = None


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

    # Test watchlist config
    default_id = get_default_watchlist_id()
    print(f"Default watchlist ID: {default_id}")

    # Test default watchlist info
    info = get_default_watchlist_info()
    print(f"Default watchlist info: {info}")

    print("✅ Config loader working!")
