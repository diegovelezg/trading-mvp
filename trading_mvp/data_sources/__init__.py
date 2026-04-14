"""Data sources for GeoMacro Analyst."""

from .base_connector import BaseDataConnector

# ELIMINADO: AlpacaNewsConnector (replaced by Google News only)
# from .alpaca_news_connector import AlpacaNewsConnector

from .google_news_connector import GoogleNewsConnector

# DESACTIVADO: SerpApiConnector (renamed to .DISABLED)
# from .serpapi_connector import SerpApiConnector

from .fred_connector import FREDConnector
from .alpha_vantage_connector import AlphaVantageConnector

__all__ = [
    'BaseDataConnector',
    # 'AlpacaNewsConnector',  # ELIMINADO
    'GoogleNewsConnector',
    # 'SerpApiConnector',    # DESACTIVADO
    'FREDConnector',
    'AlphaVantageConnector'
]
