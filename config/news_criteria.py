"""
News Search Criteria - Elite Institutional 360 Vision

Configuración de búsqueda de alto nivel para analistas institucionales.
Cubre 10 categorías estratégicas para una visión total del mercado global.
Límite de 13 items por categoría para un muestreo profundo (130 noticias total).
"""

# ============================================================
# CATEGORÍAS DE BÚSQUEDA DE NOTICIAS (Elite 10-Category Vision)
# ============================================================

NEWS_CATEGORIES = {
    "macro_monetary": [
        "central bank interest rate hawk dove signals fed ecb boj",
        "inflation CPI PPI data prints global deflationary risks sticky inflation",
        "yield curve inversion recession probability GDP contraction economic slowdown",
        "quantitative tightening easing monetary policy stagflation risks growth forecast",
        "currency volatility DXY dollar strength global FX intervention disinflation trends"
    ],

    "geopolitical_strategic": [
        "geopolitical tensions strategic resource competition sovereignty",
        "trade barriers sanctions export controls dual-use technology",
        "supply chain regionalization protectionism nearshoring friendshoring",
        "diplomatic shifts economic impact global alliance realignment",
        "maritime security trade route disruptions chokepoints defense escalation",
        "cyber warfare state-sponsored infrastructure attacks national security"
    ],

    "tech_ai_semiconductors": [
        "semiconductor demand artificial intelligence chips foundry capacity",
        "cloud infrastructure enterprise technology spending SaaS growth",
        "AI capital expenditure hyperscalers hardware compute efficiency",
        "quantum computing robotics automation frontier models benchmark",
        "tech regulation antitrust platform dominance digital sovereignty"
    ],

    "energy_nuclear_transition": [
        "nuclear energy uranium supply chain SMR modular reactors",
        "renewables energy transition carbon credit policy green hydrogen",
        "commodity price cycles energy security strategic petroleum reserve",
        "fossil fuel supply disruption exploration CAPEX oil gas inventory",
        "power grid stability electricity demand data center energy consumption"
    ],

    "commodities_resources": [
        "copper demand electrification renewable energy infrastructure supply gap",
        "lithium cobalt rare earth elements supply chain strategic minerals",
        "gold price drivers real yields sovereign central bank buying hedging",
        "agricultural commodities grain supply food inflation global fertilizer",
        "industrial metals warehouse levels LME inventories global demand signals"
    ],

    "digital_assets_crypto": [
        "bitcoin institutional adoption spot ETF inflows outflows asset management",
        "ethereum network upgrades layer 2 scalability defi TVL",
        "crypto regulatory framework SEC stablecoin legislation digital asset policy",
        "digital asset liquidity risk-on proxy venture capital crypto funding",
        "blockchain enterprise integration tokenization real world assets RWA"
    ],

    "pharma_healthcare": [
        "biotech M&A clinical trial results phase 1 2 3 efficacy",
        "FDA regulatory approval pipeline pharma therapeutic breakthroughs",
        "healthcare policy reform drug pricing negotiation Medicare impact",
        "genomic medicine CRISPR obesity drugs GLP-1 market share",
        "medical device innovation healthtech telemedicine adoption"
    ],

    "industrial_automotive": [
        "manufacturing PMI contractionary territory new orders vs inventory",
        "industrial production slump capacity utilization factory output data",
        "automotive electrification EV supply chain battery metals lithium",
        "industrial automation robotics manufacturing productivity gains",
        "defense procurement aerospace spending cycles military modernization",
        "global construction infrastructure spending urban development projects"
    ],

    "financial_stability": [
        "banking system capital ratios credit quality non-performing loans",
        "fintech disruption payment systems digital currencies CBDC",
        "private equity exit environment M&A volume IPO market window",
        "credit market spreads default risks corporate bankruptcy trends",
        "shadow banking systemic risk leverage financial contagion monitoring"
    ],

    "consumer_retail_dynamics": [
        "consumer confidence retail sales trends discretionary spending slowdown",
        "household debt personal spending data savings rate exhaustion cost of living",
        "consumer default trends credit card delinquency rates negative wealth effect",
        "housing market slowdown mortgage rates affordability index residential real estate",
        "labor market tightness real wage growth unemployment claims impact layoffs"
    ]
}

# ============================================================
# CONFIGURACIÓN DE BÚSQUEDA POR FUENTE
# ============================================================

# Límite estricto por categoría solicitado por el usuario
MAX_ITEMS_PER_CATEGORY = 13  

# Timeouts
FETCH_TIMEOUT_SECONDS = 45

# Deduplicación
REMOVE_DUPLICATES = True
DUPLICATE_BY = "title"  # Opciones: "title", "url"

# ============================================================
# FUENTES ACTIVAS
# ============================================================

ACTIVE_SOURCES = {
    "google_news": True,   # ✅ Activo
    "serpapi": False,      # ❌ Inactivo
    "alpaca_news": False   # ❌ Inactivo
}

# ============================================================
# FUNCIONES HELPER
# ============================================================

def get_active_categories() -> list:
    """Obtener lista de categorías activas."""
    return list(NEWS_CATEGORIES.keys())


def get_search_queries(category: str = None) -> list:
    """
    Obtener queries de búsqueda para una categoría.
    """
    if category:
        return NEWS_CATEGORIES.get(category, [])

    all_queries = []
    for queries in NEWS_CATEGORIES.values():
        all_queries.extend(queries)
    return all_queries


def calculate_items_per_category(max_total_items: int = None, num_categories: int = None) -> int:
    """
    Retorna el límite estricto de 13 items por categoría.
    """
    return MAX_ITEMS_PER_CATEGORY


def is_source_active(source_name: str) -> bool:
    """
    Verificar si una fuente está activa.
    """
    return ACTIVE_SOURCES.get(source_name, False)


if __name__ == "__main__":
    """Test del módulo de criterios."""
    print("="*70)
    print("📋 NEWS CRITERIA - ELITE 10-CATEGORY 360 VISION")
    print("="*70)
    print()

    print(f"Total Categories: {len(NEWS_CATEGORIES)}")
    print(f"Items per Category: {MAX_ITEMS_PER_CATEGORY}")
    print(f"Potential Total News: {len(NEWS_CATEGORIES) * MAX_ITEMS_PER_CATEGORY}")
    print()

    for cat, queries in NEWS_CATEGORIES.items():
        print(f"  • {cat}: {len(queries)} intelligent queries")
