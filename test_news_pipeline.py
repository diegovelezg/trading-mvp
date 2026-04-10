#!/usr/bin/env python3
"""Test script para verificar que el pipeline de noticias no tiene fallos silenciosos."""

import sys
import logging
from datetime import datetime

# Configurar logging para ver TODOS los mensajes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def test_alpaca_news():
    """Test Alpaca News connector con manejo de errores robusto."""
    from trading_mvp.data_sources.alpaca_news_connector import AlpacaNewsConnector

    logger.info("=" * 70)
    logger.info("TEST 1: Alpaca News Connector")
    logger.info("=" * 70)

    try:
        connector = AlpacaNewsConnector()
        logger.info("✅ Alpaca connector inicializado")

        # Test fetch
        news = connector.fetch_data(hours_back=24, max_items=10)
        logger.info(f"📊 Fetch result: {len(news)} items")

        if not news:
            logger.warning("⚠️  No news fetched - verificar API credentials")
            return False

        # Test normalize
        normalized = connector.normalize_data(news)
        logger.info(f"📊 Normalize result: {len(normalized)}/{len(news)} items")

        # Verificar que alpaca_id está presente
        if normalized:
            first_item = normalized[0]
            if 'alpaca_id' in first_item:
                logger.info(f"✅ alpaca_id presente: {first_item['alpaca_id']}")
            else:
                logger.error("❌ alpaca_id NO presente - BUG NO ARREGLADO")
                return False

            if 'title' in first_item and first_item['title']:
                logger.info(f"✅ Título presente: {first_item['title'][:50]}")
            else:
                logger.error("❌ Título inválido")
                return False

        return True

    except Exception as e:
        logger.error(f"❌ Test Alpaca falló: {e}", exc_info=True)
        return False


def test_google_news():
    """Test Google News connector con manejo de errores robusto."""
    from trading_mvp.data_sources.google_news_connector import GoogleNewsConnector

    logger.info("=" * 70)
    logger.info("TEST 2: Google News Connector")
    logger.info("=" * 70)

    try:
        connector = GoogleNewsConnector()
        logger.info("✅ Google connector inicializado")

        # Test fetch
        news = connector.fetch_data(topic="business", max_items=10)
        logger.info(f"📊 Fetch result: {len(news)} items")

        if not news:
            logger.warning("⚠️  No news fetched - posible error de RSS")
            return False

        # Test normalize
        normalized = connector.normalize_data(news)
        logger.info(f"📊 Normalize result: {len(normalized)}/{len(news)} items")

        # Verificar campos requeridos
        if normalized:
            first_item = normalized[0]
            if 'title' in first_item and first_item['title']:
                logger.info(f"✅ Título presente: {first_item['title'][:50]}")
            else:
                logger.error("❌ Título inválido")
                return False

        return True

    except Exception as e:
        logger.error(f"❌ Test Google falló: {e}", exc_info=True)
        return False


def test_db_insertion():
    """Test inserción en BD con validaciones."""
    from trading_mvp.core.db_geo_news import insert_geo_news

    logger.info("=" * 70)
    logger.info("TEST 3: Database Insertion")
    logger.info("=" * 70)

    # Test 1: Noticia válida
    logger.info("Test 3a: Insertar noticia válida")
    valid_news = {
        "source": "test",
        "source_type": "test",
        "title": "Test News Item",
        "summary": "Test summary",
        "content": "Test content",
        "url": "https://test.com/news/1",
        "author": "Test Author",
        "published_at": datetime.now().isoformat(),
        "alpaca_id": 12345
    }

    try:
        news_id = insert_geo_news(valid_news)
        if news_id:
            logger.info(f"✅ Noticia válida insertada con ID: {news_id}")
        else:
            logger.error("❌ Noticia válida NO se insertó")
            return False
    except Exception as e:
        logger.error(f"❌ Error insertando noticia válida: {e}")
        return False

    # Test 2: Noticia inválida (sin título)
    logger.info("\nTest 3b: Intentar insertar noticia sin título (debe fallar)")
    invalid_news = {
        "source": "test",
        "title": "",  # ❌ Título vacío
        "summary": "Test summary",
        "url": "https://test.com/news/2"
    }

    try:
        news_id = insert_geo_news(invalid_news)
        if news_id:
            logger.error("❌ Noticia inválida se insertó (debió fallar)")
            return False
        else:
            logger.info("✅ Noticia inválida rechazada correctamente")
    except Exception as e:
        logger.info(f"✅ Noticia inválida generó excepción: {e}")

    # Test 3: Duplicado
    logger.info("\nTest 3c: Intentar insertar duplicado (debe ser rechazado silenciosamente)")
    try:
        dup_news_id = insert_geo_news(valid_news)
        if dup_news_id == news_id:
            logger.info(f"✅ Duplicado detectado, retornó ID existente: {dup_news_id}")
        elif dup_news_id is None:
            logger.info("✅ Duplicado rechazado (retornó None)")
        else:
            logger.warning(f"⚠️  Duplicado insertó nuevo ID: {dup_news_id} (podría ser bug)")
    except Exception as e:
        logger.info(f"✅ Duplicado generó excepción: {e}")

    return True


def main():
    """Ejecutar todos los tests."""
    logger.info("\n" + "=" * 70)
    logger.info("🚀 INICIANDO TESTS DE PIPELINE DE NOTICIAS")
    logger.info("=" * 70 + "\n")

    results = {
        "alpaca": test_alpaca_news(),
        "google": test_google_news(),
        "db": test_db_insertion()
    }

    logger.info("\n" + "=" * 70)
    logger.info("📊 RESULTADOS")
    logger.info("=" * 70)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    all_passed = all(results.values())

    if all_passed:
        logger.info("\n✅ TODOS LOS TESTS PASARON")
        return 0
    else:
        logger.error("\n❌ ALGUNOS TESTS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(main())
