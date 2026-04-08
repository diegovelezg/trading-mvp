"""Módulo de reportes.

Contiene funcionalidad para generar Trade Cards, reportes de performance
y análisis de risk management.
"""

from .trade_cards import generate_trade_card
from .performance import generate_performance_report

__all__ = ["generate_trade_card", "generate_performance_report"]
