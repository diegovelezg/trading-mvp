"""
Semantic News Search using Embeddings

Busca noticias relacionadas usando cosine similarity de embeddings.
REEMPLAZA al sistema de entity matching.
"""

import logging
from typing import List, Dict, Tuple, Optional
from trading_mvp.core.db_ticker_embeddings import get_ticker_embeddings
from trading_mvp.core.db_news_embeddings import get_news_embeddings_batch, find_similar_news
from trading_mvp.core.db_geo_news import get_recent_news
from trading_mvp.core.gemini_embeddings import generate_embedding

logger = logging.getLogger(__name__)


class SemanticNewsSearch:
    """Búsqueda semántica de noticias usando embeddings."""

    def __init__(
        self,
        similarity_threshold: float = 0.75,
        min_news_count: int = 5
    ):
        """
        Args:
            similarity_threshold: Umbral de similitud coseno (0-1)
            min_news_count: Mínimo de noticias para considerar búsqueda exitosa
        """
        self.similarity_threshold = similarity_threshold
        self.min_news_count = min_news_count

    def find_related_news(
        self,
        ticker: str,
        all_news: List[Dict],
        method: str = "semantic"
    ) -> Tuple[List[Dict], Dict]:
        """
        Buscar noticias relacionadas con un ticker usando similarity semántica.

        Args:
            ticker: Símbolo del ticker
            all_news: Todas las noticias disponibles
            method: 'semantic' (únicamente embeddings)

        Returns:
            (related_news, stats)
        """

        # 1. Obtener embeddings del ticker (promedio de sus entities)
        ticker_embeddings_list = get_ticker_embeddings(ticker)

        if not ticker_embeddings_list:
            logger.warning(f"No embeddings found for {ticker}")
            return [], {"method": "none", "count": 0, "error": "No ticker embeddings"}

        # Calcular embedding promedio del ticker
        ticker_embedding = self._average_embedding_from_list(ticker_embeddings_list)

        # 2. Buscar noticias similares por cosine similarity
        similar_news = find_similar_news(
            query_embedding=ticker_embedding,
            threshold=self.similarity_threshold,
            limit=len(all_news)
        )

        # 3. Obtener news items completos
        news_map = {news['id']: news for news in all_news}
        related_news = []

        for item in similar_news:
            news_id = item['news_id']
            similarity = item['similarity']

            if news_id in news_map:
                news_with_meta = news_map[news_id].copy()
                news_with_meta['_similarity'] = similarity
                news_with_meta['_match_method'] = 'semantic_embedding'
                related_news.append(news_with_meta)

        # Stats
        stats = {
            "ticker": ticker,
            "method": "semantic_embedding",
            "similarity_threshold": self.similarity_threshold,
            "total_count": len(related_news),
            "avg_similarity": sum(n['_similarity'] for n in related_news) / len(related_news) if related_news else 0,
            "ticker_embeddings_count": len(ticker_embeddings_list)
        }

        logger.info(
            f"🧠 {ticker}: Semantic search - "
            f"{len(related_news)} news found (avg similarity: {stats['avg_similarity']:.2f})"
        )

        return related_news, stats

    def _average_embedding_from_list(self, embeddings_list: List[Dict]) -> List[float]:
        """Calcula el embedding promedio de una lista de embeddings.

        Args:
            embeddings_list: Lista de dicts con 'embedding' key

        Returns:
            Embedding promedio (768 dims)
        """

        if not embeddings_list:
            return [0.0] * 768

        # Extraer vectors de la lista de dicts
        embedding_vectors = [item['embedding'] for item in embeddings_list]

        # Calcular promedio dimensión por dimensión
        dim = len(embedding_vectors[0])
        avg_embedding = []

        for i in range(dim):
            sum_val = sum(emb[i] for emb in embedding_vectors)
            avg_val = sum_val / len(embedding_vectors)
            avg_embedding.append(avg_val)

        return avg_embedding


# Instancia global
default_search = SemanticNewsSearch()


def find_related_news_for_ticker(
    ticker: str,
    all_news: List[Dict],
    method: str = "semantic",
    similarity_threshold: float = 0.75
) -> Tuple[List[Dict], Dict]:
    """
    Wrapper simple para búsqueda semántica.

    Args:
        ticker: Símbolo del ticker
        all_news: Todas las noticias disponibles
        method: 'semantic' (embeddings puros)
        similarity_threshold: Umbral de similitud (0-1)

    Returns:
        (related_news, stats)
    """

    search = SemanticNewsSearch(
        similarity_threshold=similarity_threshold,
        min_news_count=5
    )

    return search.find_related_news(ticker, all_news, method=method)


def test_semantic_search():
    """Test del sistema de búsqueda semántica."""

    print("="*70)
    print("🧪 TEST: SEMANTIC NEWS SEARCH")
    print("="*70)
    print()

    # Get news
    all_news = get_recent_news(hours_back=168)
    print(f"Total news: {len(all_news)}")
    print()

    # Test tickers
    test_tickers = ['MA', 'BWXT', 'USO']

    for ticker in test_tickers:
        print(f"\n{'='*70}")
        print(f"TESTING: {ticker}")
        print(f"{'='*70}")

        related_news, stats = find_related_news_for_ticker(
            ticker,
            all_news,
            method='semantic',
            similarity_threshold=0.75
        )

        print(f"✅ Found: {len(related_news)} news")
        print(f"   Method: {stats.get('method', 'unknown')}")
        print(f"   Avg similarity: {stats.get('avg_similarity', 0):.2f}")

        if related_news:
            print(f"\n   Top 3 news:")
            for news in related_news[:3]:
                sim = news.get('_similarity', 0)
                title = news.get('title', '')[:70]
                print(f"      [{sim:.2f}] {title}...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_semantic_search()
