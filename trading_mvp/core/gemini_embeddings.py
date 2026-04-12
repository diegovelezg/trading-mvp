"""
Gemini Embeddings API Integration

Genera embeddings usando Gemini API para búsqueda semántica.
Basado en documentación oficial: https://ai.google.dev/gemini-api/docs/embeddings
"""

import os
import logging
from typing import List, Dict, Optional
import numpy as np
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Config desde ENV
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = os.getenv("GEMINI_API_EMBEDDING_MODEL", "gemini-embedding-001")
EMBEDDING_SIZE = int(os.getenv("GEMINI_API_EMBEDDING_SIZE", "768"))


def get_gemini_client() -> genai.Client:
    """Get authenticated Gemini client."""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment")

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_embedding(
    text: str,
    task_type: str = "SEMANTIC_SIMILARITY",
    output_dimensionality: int = None
) -> List[float]:
    """
    Generate embedding for a single text.

    Args:
        text: Text to embed
        task_type: Type of task (SEMANTIC_SIMILARITY, RETRIEVAL_DOCUMENT, etc.)
        output_dimensionality: Size of embedding vector (default: from env)

    Returns:
        List of float values (embedding vector)

    Examples:
        >>> embedding = generate_embedding("Nuclear Power")
        >>> len(embedding)
        768
    """
    if output_dimensionality is None:
        output_dimensionality = EMBEDDING_SIZE

    try:
        client = get_gemini_client()

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=output_dimensionality
            )
        )

        embedding_obj = result.embeddings[0]
        embedding_values = embedding_obj.values

        # Normalizar si no es 3072 (según doc oficial)
        if output_dimensionality < 3072:
            embedding_values = normalize_embedding(embedding_values)

        logger.debug(f"Generated embedding: {len(embedding_values)} dimensions for '{text[:50]}...'")
        return embedding_values

    except Exception as e:
        logger.error(f"Error generating embedding for '{text[:50]}...': {e}")
        raise


def generate_embeddings_batch(
    texts: List[str],
    task_type: str = "SEMANTIC_SIMILARITY",
    output_dimensionality: int = None
) -> List[List[float]]:
    """
    Generate embeddings for multiple texts (batch).

    Args:
        texts: List of texts to embed
        task_type: Type of task
        output_dimensionality: Size of embedding vector

    Returns:
        List of embedding vectors

    Examples:
        >>> embeddings = generate_embeddings_batch(["Oil", "Energy", "Power"])
        >>> len(embeddings)
        3
    """
    if output_dimensionality is None:
        output_dimensionality = EMBEDDING_SIZE

    try:
        client = get_gemini_client()

        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=output_dimensionality
            )
        )

        embeddings = []
        for embedding_obj in result.embeddings:
            embedding_values = embedding_obj.values

            # Normalizar si no es 3072
            if output_dimensionality < 3072:
                embedding_values = normalize_embedding(embedding_values)

            embeddings.append(embedding_values)

        logger.debug(f"Generated {len(embeddings)} embeddings (batch)")
        return embeddings

    except Exception as e:
        logger.error(f"Error generating batch embeddings: {e}")
        raise


def normalize_embedding(embedding_values: List[float]) -> List[float]:
    """
    Normalizar embedding para dimensiones < 3072.

    Según doc de Gemini: embeddings de 3072 ya están normalizados,
    pero para dimensiones menores (768, 1536) hay que normalizar manualmente.

    Args:
        embedding_values: Vector de embedding

    Returns:
        Vector normalizado (norma = 1)
    """
    embedding_array = np.array(embedding_values)
    norm = np.linalg.norm(embedding_array)

    if norm == 0:
        logger.warning("Embedding has zero norm, returning as-is")
        return embedding_values

    normalized = embedding_array / norm
    return normalized.tolist()


def cosine_similarity(
    embedding1: List[float],
    embedding2: List[float]
) -> float:
    """
    Calcular similitud coseno entre dos embeddings.

    Args:
        embedding1: Primer embedding
        embedding2: Segundo embedding

    Returns:
        Similitud coseno (0 a 1, donde 1 = idéntico)

    Examples:
        >>> sim = cosine_similarity(embed1, embed2)
        >>> 0.0 <= sim <= 1.0
        True
    """
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)

    # Producto punto
    dot_product = np.dot(vec1, vec2)

    # Normas
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    # Similitud coseno
    similarity = dot_product / (norm1 * norm2)

    return float(similarity)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)

    texts = [
        "Nuclear Power",
        "Atomic Energy",
        "Oil Prices"
    ]

    print("🧪 Testing Gemini Embeddings")
    print("="*70)

    embeddings = generate_embeddings_batch(texts)
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   Size: {len(embeddings[0])} dimensions")
    print()

    # Test similarity
    print("📊 Similarity Matrix:")
    print("-"*70)

    for i, text1 in enumerate(texts):
        for j in range(i + 1, len(texts)):
            text2 = texts[j]
            sim = cosine_similarity(embeddings[i], embeddings[j])
            print(f"   '{text1}' ↔ '{text2}': {sim:.4f}")

    print()
    print("✅ Embeddings test complete!")
