"""
News Search Criteria - Independent Configuration

Criterios de búsqueda de noticias SEPARADOS de los motores de búsqueda.
Single Source of Truth para qué buscar, independientemente de dónde.
"""

# ============================================================
# CATEGORÍAS DE BÚSQUEDA DE NOTICIAS
# ============================================================

NEWS_CATEGORIES = {
    "geopolitical": [
        "geopolitical conflicts war",
        "international relations diplomacy",
        "middle east conflict",
        "ukraine russia war",
        "china taiwan tensions"
    ],

    "economic": [
        "federal reserve interest rates",
        "inflation consumer prices",
        "GDP economic growth",
        "unemployment jobs report",
        "central bank monetary policy"
    ],

    "trade_policy": [
        "trade tariffs sanctions",
        "us china trade war",
        "import export regulations",
        "trade agreements deals",
        "economic sanctions countries"
    ],

    "regulatory": [
        "government regulation policy",
        "federal regulations changes",
        "financial regulations banking",
        "technology regulation ai",
        "environmental regulations climate"
    ]
}

# ============================================================
# CONFIGURACIÓN DE BÚSQUEDA POR FUENTE
# ============================================================

# Máximo de items por categoría (distribuye el total)
MAX_ITEMS_PER_CATEGORY = 10  # Si hay 5 categorías → 50 items total

# Timeouts
FETCH_TIMEOUT_SECONDS = 30

# Deduplicación
REMOVE_DUPLICATES = True
DUPLICATE_BY = "title"  # Opciones: "title", "url"

# ============================================================
# FUENTES ACTIVAS
# ============================================================

ACTIVE_SOURCES = {
    "google_news": True,   # ✅ Activo
    "serpapi": False,      # ❌ Comentar/desactivar
    "alpaca_news": False   # ❌ Eliminar
}

# ============================================================
# FUNCIONES HELPER
# ============================================================

def get_active_categories() -> list:
    """Obtener lista de categorías activas."""
    return list(NEWS_CATEGORIES.keys())


def get_search_queries(category: str = None) -> list:
    """
    Obtregar queries de búsqueda para una categoría.

    Args:
        category: Nombre de la categoría (None = todas)

    Returns:
        Lista de queries de búsqueda
    """
    if category:
        return NEWS_CATEGORIES.get(category, [])

    # Todas las queries aplanadas
    all_queries = []
    for queries in NEWS_CATEGORIES.values():
        all_queries.extend(queries)
    return all_queries


def calculate_items_per_category(max_total_items: int, num_categories: int = None) -> int:
    """
    Calcular cuántos items por categoría buscar.

    Args:
        max_total_items: Máximo total de items deseados
        num_categories: Número de categorías (default: todas las activas)

    Returns:
        Items a buscar por categoría
    """
    if num_categories is None:
        num_categories = len(NEWS_CATEGORIES)

    return max_total_items // num_categories


def is_source_active(source_name: str) -> bool:
    """
    Verificar si una fuente está activa.

    Args:
        source_name: Nombre de la fuente ('google_news', 'serpapi', 'alpaca_news')

    Returns:
        True si la fuente está activa
    """
    return ACTIVE_SOURCES.get(source_name, False)


if __name__ == "__main__":
    """Test del módulo de criterios."""
    print("="*70)
    print("📋 NEWS CRITERIA - CONFIGURATION")
    print("="*70)
    print()

    print("Active Categories:")
    for cat, queries in NEWS_CATEGORIES.items():
        print(f"  • {cat}: {len(queries)} queries")
    print()

    print("Active Sources:")
    for source, active in ACTIVE_SOURCES.items():
        status = "✅" if active else "❌"
        print(f"  {status} {source}")
    print()

    print("Sample Queries:")
    queries = get_search_queries("geopolitical")
    for i, query in enumerate(queries[:3], 1):
        print(f"  {i}. {query}")
