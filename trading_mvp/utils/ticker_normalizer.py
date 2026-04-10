"""
Ticker Normalizer Utilities

Normalización de tickers - DRY + SSOT.
Previene bugs case-sensitive y asegura consistencia.
"""

import re
from typing import List, Set


def normalize_ticker(ticker: str) -> str:
    """
    Normaliza un ticker a formato estándar.
    - Elimina espacios
    - Convierte a uppercase
    - Valida longitud máxima

    Args:
        ticker: Ticker sin normalizar

    Returns:
        Ticker normalizado

    Raises:
        ValueError: Si el ticker es inválido

    Examples:
        >>> normalize_ticker('aapl')
        'AAPL'
        >>> normalize_ticker('  tsla  ')
        'TSLA'
        >>> normalize_ticker('MSFT')
        'MSFT'
    """
    if not ticker:
        raise ValueError("Ticker cannot be empty")

    trimmed = ticker.strip().upper()

    # Validar longitud máxima (10 caracteres es el máximo en NYSE/NASDAQ)
    if len(trimmed) > 10:
        raise ValueError(f"Ticker too long: {trimmed} (max 10 characters)")

    # Validar caracteres alfanuméricos
    if not re.match(r'^[A-Z0-9]+$', trimmed):
        raise ValueError(f"Invalid ticker characters: {trimmed} (only A-Z and 0-9 allowed)")

    return trimmed


def normalize_tickers(tickers: List[str]) -> List[str]:
    """
    Normaliza un array de tickers.

    Args:
        tickers: Lista de tickers sin normalizar

    Returns:
        Lista de tickers normalizados

    Examples:
        >>> normalize_tickers(['aapl', 'tsla', 'msft'])
        ['AAPL', 'TSLA', 'MSFT']
    """
    if not isinstance(tickers, list):
        raise ValueError("Tickers must be a list")

    return [normalize_ticker(t) for t in tickers]


def is_normalized_ticker(ticker: str) -> bool:
    """
    Valida si un ticker ya está normalizado.

    Args:
        ticker: Ticker a validar

    Returns:
        True si está normalizado
    """
    try:
        normalized = normalize_ticker(ticker)
        return normalized == ticker.strip()
    except (ValueError, AttributeError):
        return False


def are_tickers_equal(ticker1: str, ticker2: str) -> bool:
    """
    Compara dos tickers ignorando case y espacios.

    Args:
        ticker1: Primer ticker
        ticker2: Segundo ticker

    Returns:
        True si son equivalentes

    Examples:
        >>> are_tickers_equal('aapl', 'AAPL')
        True
        >>> are_tickers_equal('  tsla  ', 'TSLA')
        True
        >>> are_tickers_equal('AAPL', 'MSFT')
        False
    """
    try:
        norm1 = normalize_ticker(ticker1)
        norm2 = normalize_ticker(ticker2)
        return norm1 == norm2
    except (ValueError, AttributeError):
        return False


def contains_ticker(tickers: List[str], search_term: str) -> bool:
    """
    Busca un ticker en un array (case-insensitive).

    Args:
        tickers: Lista de tickers
        search_term: Ticker a buscar

    Returns:
        True si encuentra el ticker

    Examples:
        >>> contains_ticker(['AAPL', 'TSLA'], 'aapl')
        True
        >>> contains_ticker(['AAPL', 'TSLA'], 'msft')
        False
    """
    try:
        normalized = normalize_ticker(search_term)
        return any(are_tickers_equal(t, normalized) for t in tickers)
    except (ValueError, AttributeError):
        return False


def unique_tickers(tickers: List[str]) -> List[str]:
    """
    Elimina duplicados de un array de tickers (case-insensitive).

    Args:
        tickers: Lista de tickers con posibles duplicados

    Returns:
        Lista de tickers únicos y normalizados

    Examples:
        >>> unique_tickers(['AAPL', 'aapl', 'TSLA', 'tsla'])
        ['AAPL', 'TSLA']
    """
    seen: Set[str] = set()
    result: List[str] = []

    for ticker in tickers:
        try:
            normalized = normalize_ticker(ticker)
            if normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        except ValueError:
            # Skip invalid tickers
            continue

    return result


def is_valid_ticker(ticker: str) -> bool:
    """
    Type guard para validar que un string es un ticker válido.

    Args:
        ticker: Valor a validar

    Returns:
        True si es un ticker válido
    """
    if not isinstance(ticker, str):
        return False

    try:
        normalize_ticker(ticker)
        return True
    except ValueError:
        return False


# Aliases para compatibilidad con TypeScript
normalizeTicker = normalize_ticker
normalizeTickers = normalize_tickers
isNormalizedTicker = is_normalized_ticker
areTickersEqual = are_tickers_equal
containsTicker = contains_ticker
uniqueTickers = unique_tickers
isValidTicker = is_valid_ticker


if __name__ == "__main__":
    # Tests
    print("Testing ticker normalizer...")

    # Test normalize_ticker
    assert normalize_ticker('aapl') == 'AAPL'
    assert normalize_ticker('  tsla  ') == 'TSLA'
    assert normalize_ticker('MSFT') == 'MSFT'

    # Test are_tickers_equal
    assert are_tickers_equal('aapl', 'AAPL') is True
    assert are_tickers_equal('AAPL', 'MSFT') is False

    # Test contains_ticker
    assert contains_ticker(['AAPL', 'TSLA'], 'aapl') is True
    assert contains_ticker(['AAPL', 'TSLA'], 'msft') is False

    # Test unique_tickers
    assert unique_tickers(['AAPL', 'aapl', 'TSLA', 'tsla']) == ['AAPL', 'TSLA']

    print("✅ All tests passed!")
