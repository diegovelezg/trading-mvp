"""Dashboard API Client - SSOT wrapper que usa las APIs del dashboard.

Este módulo NO implementa lógica de negocio, solo hace fetch a las APIs del dashboard.
Toda la lógica de negocio está en: dashboard/app/api/

SSOT: Dashboard API → Supabase
"""

import os
import logging
from typing import List, Dict, Optional
import requests
from trading_mvp.utils.ticker_normalizer import normalize_ticker, normalize_tickers
from supabase import create_client

logger = logging.getLogger(__name__)

# Configuración
DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL", "http://localhost:3000")


# ============================================================================
# API HELPERS
# ============================================================================

def _api_get(endpoint: str) -> Dict:
    """Hace GET a la API del dashboard."""
    url = f"{DASHBOARD_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Extract actual data from wrapper response
        if isinstance(data, dict) and 'data' in data:
            return data['data']
        return data
    except Exception as e:
        logger.error(f"❌ GET {url} failed: {e}")
        return {}


def _api_post(endpoint: str, data: Dict) -> Dict:
    """Hace POST a la API del dashboard."""
    url = f"{DASHBOARD_BASE_URL}{endpoint}"
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        resp_data = response.json()
        # Extract actual data from wrapper response
        if isinstance(resp_data, dict) and 'data' in resp_data:
            return resp_data['data']
        return resp_data
    except Exception as e:
        logger.error(f"❌ POST {url} failed: {e}")
        return {}


def _api_delete(endpoint: str, params: Dict = None) -> bool:
    """Hace DELETE a la API del dashboard."""
    url = f"{DASHBOARD_BASE_URL}{endpoint}"
    try:
        response = requests.delete(url, params=params, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"❌ DELETE {url} failed: {e}")
        return False


# ============================================================================
# WATCHLIST OPERATIONS (via Dashboard API)
# ============================================================================

def create_watchlist(name: str, description: str = None, criteria_prompt: str = None, criteria_summary: str = None) -> Optional[int]:
    """Crear watchlist via Dashboard API."""
    data = {
        "name": name,
        "description": description,
        "criteria_prompt": criteria_prompt,
        "criteria_summary": criteria_summary
    }
    result = _api_post("/api/watchlists", data)
    return result.get("id") if result else None


def get_active_watchlists() -> List[Dict]:
    """Obtener watchlists activas via Dashboard API."""
    return _api_get("/api/watchlists")


def add_ticker_to_watchlist(watchlist_id: int, ticker: str, company_name: str = None, reason: str = None) -> bool:
    """Añadir ticker a watchlist via Dashboard API."""
    data = {
        "watchlist_id": watchlist_id,
        "ticker": ticker,
        "company_name": company_name,
        "reason": reason
    }
    result = _api_post("/api/watchlists/items", data)
    return bool(result)


def remove_ticker_from_watchlist(watchlist_id: int, ticker: str) -> bool:
    """Eliminar ticker de watchlist via Dashboard API."""
    params = {
        "watchlistId": watchlist_id,
        "ticker": ticker
    }
    return _api_delete("/api/watchlists/items", params)


# ============================================================================
# EXPLORATION OPERATIONS (via Dashboard API)
# ============================================================================

def get_recent_explorations(limit: int = 10) -> List[Dict]:
    """Obtener exploraciones recientes via Dashboard API."""
    return _api_get("/api/explorations")


def insert_exploration(prompt: str, criteria: str, tickers: list, reasoning: str = "", ticker_details: list = None) -> Optional[int]:
    """Insertar exploración directamente en Supabase (no hay API endpoint aún).

    Args:
        prompt: Prompt temático
        criteria: Criterios de búsqueda
        tickers: Lista de tickers descubiertos (solo símbolos)
        reasoning: Razónamiento de la IA
        ticker_details: Lista completa con metadatos de cada ticker [{ticker, name, sector, description_es}]

    Returns:
        exploration_id o None
    """
    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not found")
            return None

        supabase = create_client(supabase_url, supabase_key)

        # Build insert data
        insert_data = {
            'prompt': prompt,
            'criteria': criteria,
            'tickers': tickers,
            'reasoning': reasoning
        }

        # Add ticker_details if provided
        if ticker_details:
            insert_data['ticker_details'] = ticker_details
            logger.info(f"📊 Saving {len(ticker_details)} ticker details to exploration")

        result = supabase.table('explorations').insert(insert_data).execute()

        if result.data:
            exploration_id = result.data[0]['id']
            logger.info(f"✅ Saved exploration with ID {exploration_id}")
            return exploration_id
        return None
    except Exception as e:
        logger.error(f"❌ Error saving exploration: {e}")
        return None


def insert_news(external_id: str, title: str, source: str, url: str, summary: str, published_at: str) -> Optional[int]:
    """Insertar news directamente en Supabase.

    Args:
        external_id: ID externo de la noticia
        title: Título
        source: Fuente
        url: URL
        summary: Resumen
        published_at: Fecha de publicación

    Returns:
        news_id o None
    """
    # Validaciones críticas
    if not title or not title.strip():
        logger.error(f"❌ Cannot insert news: missing title. Source: {source}, External ID: {external_id}")
        return None

    if not external_id:
        logger.error(f"❌ Cannot insert news: missing external_id. Title: {title[:50]}")
        return None

    title_preview = title[:50] + "..." if len(title) > 50 else title

    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not found")
            return None

        supabase = create_client(supabase_url, supabase_key)

        result = supabase.table('news').insert({
            'external_id': external_id,
            'title': title.strip(),
            'source': source,
            'url': url,
            'summary': summary,
            'published_at': published_at
        }).execute()

        if result.data:
            news_id = result.data[0]['id']
            logger.info(f"✅ Saved news: {title_preview}")
            return news_id

        logger.error(f"❌ Insert returned no data for news: {title_preview}")
        return None
    except Exception as e:
        # Si es duplicado, intentar buscar el existente
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            logger.debug(f"♻️  News already exists (duplicate): {title_preview}")
            try:
                supabase = create_client(supabase_url, supabase_key)
                result = supabase.table('news').select('*').eq('external_id', external_id).execute()
                if result.data:
                    logger.debug(f"✅ Found existing news ID: {result.data[0]['id']}")
                    return result.data[0]['id']
            except Exception as retry_e:
                logger.error(f"❌ Error fetching existing news after duplicate: {retry_e}")
        else:
            logger.error(f"❌ Error saving news '{title_preview}' (source: {source}): {e}")
        return None


def insert_sentiment(news_id: int, agent_id: str, score: float, reasoning: str) -> bool:
    """Insertar sentimiento directamente en Supabase.

    Args:
        news_id: ID de la noticia
        agent_id: ID del agente
        score: Score de sentimiento
        reasoning: Razónamiento

    Returns:
        True si exitoso, False sino
    """
    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not found")
            return False

        supabase = create_client(supabase_url, supabase_key)

        supabase.table('sentiments').insert({
            'news_id': news_id,
            'agent_id': agent_id,
            'score': score,
            'reasoning': reasoning
        }).execute()

        return True
    except Exception as e:
        logger.error(f"❌ Error saving sentiment: {e}")
        return False


def save_desk_run(watchlist_id: int, theme: str, tickers: list) -> Optional[int]:
    """Guardar investment desk run en Supabase.

    Args:
        watchlist_id: ID de la watchlist
        theme: Temática de inversión
        tickers: Lista de tickers analizados

    Returns:
        desk_run_id o None
    """
    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not found")
            return None

        supabase = create_client(supabase_url, supabase_key)

        result = supabase.table('investment_runs').insert({
            'watchlist_id': watchlist_id,
            'watchlist_name': f"Theme: {theme}",
            'total_tickers': len(tickers)
        }).execute()

        if result.data:
            desk_run_id = result.data[0]['id']
            logger.info(f"✅ Saved desk run with ID {desk_run_id}")
            return desk_run_id
        return None
    except Exception as e:
        logger.error(f"❌ Error saving desk run: {e}")
        return None


def save_ticker_analysis(ticker_result: Dict, desk_run_id: int) -> Optional[int]:
    """Guardar análisis de ticker en Supabase.

    Args:
        ticker_result: Resultado del análisis
        desk_run_id: ID del desk run

    Returns:
        analysis_id o None
    """
    try:
        supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            logger.error("❌ Supabase credentials not found")
            return None

        supabase = create_client(supabase_url, supabase_key)

        result = supabase.table('ticker_analysis').insert({
            'desk_run_id': desk_run_id,
            'ticker': ticker_result.get('ticker'),
            'company_name': ticker_result.get('company_name'),
            'recommendation': ticker_result.get('recommendation'),
            'rationale': ticker_result.get('rationale'),
            'positive_ratio': ticker_result.get('positive_ratio'),
            'negative_ratio': ticker_result.get('negative_ratio'),
            'avg_confidence': ticker_result.get('avg_confidence'),
            'related_news_count': ticker_result.get('related_news_count', 0),
            'unique_entities_found': ticker_result.get('unique_entities_found', 0)
        }).execute()

        if result.data:
            analysis_id = result.data[0]['id']
            logger.info(f"✅ Saved ticker analysis for {ticker_result.get('ticker')}")
            return analysis_id
        return None
    except Exception as e:
        logger.error(f"❌ Error saving ticker analysis: {e}")
        return None


def record_decision(ticker_analysis_id: int, desk_run_id: int, ticker: str,
                   recommendation: str, desk_action: str, decision: str,
                   decision_notes: str = None, action_taken: str = None,
                   position_size: float = None, entry_price: float = None,
                   alpaca_order_id: str = None) -> Optional[int]:
    """Registrar decisión (placeholder por ahora).

    Args:
        ticker_analysis_id: ID del análisis de ticker
        desk_run_id: ID del desk run
        ticker: Símbolo del ticker
        recommendation: Recomendación original
        desk_action: Acción del desk
        decision: Decisión tomada
        decision_notes: Notas de la decisión
        action_taken: Acción tomada
        position_size: Tamaño de la posición
        entry_price: Precio de entrada
        alpaca_order_id: ID de la orden de Alpaca

    Returns:
        decision_id o None
    """
    # Placeholder - esta tabla podría no existir aún en Supabase
    logger.info(f"💾 Decision recorded for {ticker}: {decision}")
    return None


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def test_dashboard_connection() -> bool:
    """Verificar que el dashboard está corriendo."""
    try:
        response = requests.get(f"{DASHBOARD_BASE_URL}/api/watchlists", timeout=5)
        return response.status_code == 200
    except:
        return False


if __name__ == "__main__":
    if test_dashboard_connection():
        print("✅ Dashboard API connection successful")
    else:
        print("❌ Dashboard API connection failed - is the dashboard running?")
