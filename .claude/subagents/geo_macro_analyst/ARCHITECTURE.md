# 🏗️ Arquitectura: Procesamiento con Embeddings Semánticos

**Fecha**: 2026-04-13
**Agente**: GeoMacro Analyst
**Modelo**: GEMINI_API_MODEL_01 (gemini-2.0-flash-exp)

---

## **1. PIPELINE DE PROCESAMIENTO**

```
┌─────────────────────────────────────────────────────────────────┐
│                      1. INGESTA DE NOTICIAS                     │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  ┌──────────┐         ┌──────────┐         ┌──────────┐
  │ Alpaca   │         │  Google  │         │ SERPAPI  │
  │   News   │         │   News   │         │          │
  │ (max 50) │         │   RSS    │         │ Search   │
  └──────────┘         └──────────┘         └──────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Normalización   │
                    │  (formato único) │
                    └──────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │       2. GENERACIÓN DE EMBEDDINGS       │
        │    (gemini-embedding-001, 768 dims)     │
        └─────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ 3. ALMACENAMIENTO │
                    │   (pgvector DB)   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  4. BÚSQUEDA      │
                    │  SEMÁNTICA       │
                    │  (Cosine Sim)    │
                    └──────────────────┘
```

---

## **2. ESQUEMA DE BASE DE DATOS**

### **2.1 Tabla: `geo_macro_news`**

```sql
CREATE TABLE geo_macro_news (
    id SERIAL PRIMARY KEY,

    -- News content
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT,

    -- Source
    source TEXT,                    -- 'alpaca_news', 'google_news', 'serpapi'
    source_type TEXT,
    author TEXT,
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Source-specific IDs
    alpaca_id INTEGER,

    -- Raw data (JSONB)
    raw_data JSONB,

    -- Prevent duplicates
    UNIQUE (source, alpaca_id)
);
```

**Índices:**
```sql
CREATE INDEX idx_geo_news_source ON geo_macro_news(source);
CREATE INDEX idx_geo_news_published ON geo_macro_news(published_at DESC);
CREATE INDEX idx_geo_news_collected ON geo_macro_news(collected_at DESC);
```

---

### **2.2 Tabla: `news_embeddings`**

```sql
CREATE TABLE news_embeddings (
    news_id INTEGER PRIMARY KEY,
    embedding vector(768),                  -- pgvector
    embedding_dim INTEGER DEFAULT 768,
    embedding_model TEXT DEFAULT 'gemini-embedding-001',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (news_id) REFERENCES geo_macro_news(id) ON DELETE CASCADE
);
```

**Índices:**
```sql
-- HNSW index para fast cosine similarity
CREATE INDEX idx_news_embeddings_hnsw
ON news_embeddings USING hnsw (embedding vector_cosine_ops);

-- Index para lookups por news_id
CREATE INDEX idx_news_embeddings_news_id
ON news_embeddings(news_id);
```

---

### **2.3 Tabla: `ticker_entity_embeddings` (ADN del Ticker)**

```sql
CREATE TABLE ticker_entity_embeddings (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    entity_text TEXT NOT NULL,
    embedding vector(768),
    entity_type TEXT,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ticker, entity_text)
);
```

**Índices:**
```sql
CREATE INDEX idx_ticker_embeddings_ticker
ON ticker_entity_embeddings(ticker);

CREATE INDEX idx_ticker_embeddings_hnsw
ON ticker_entity_embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## **3. BÚSQUEDA SEMÁNTICA**

### **3.1 Individual DNA Matching**

El ADN del ticker se compara de forma individual (MAX similarity):

```sql
WITH ticker_vectors AS (
    SELECT embedding FROM ticker_entity_embeddings WHERE ticker = 'USO'
)
SELECT
    e.news_id,
    MAX(1 - (e.embedding <=> t.embedding)) as max_similarity
FROM news_embeddings e
CROSS JOIN ticker_vectors t
GROUP BY e.news_id
HAVING MAX(1 - (e.embedding <=> t.embedding)) >= 0.80
ORDER BY max_similarity DESC
LIMIT 50;
```

**Operador `<=>`** = Cosine distance (pgvector)
**`1 - distance`** = Cosine similarity
**Threshold 0.80** = Mínimo de similitud para relevancia

---

### **3.2 Implementación en Python**

```python
def find_related_news_for_ticker(
    ticker: str,
    all_news: List[Dict],
    method: str = "semantic",
    similarity_threshold: float = 0.80
) -> Tuple[List[Dict], Dict]:
    """Búsqueda semántica de noticias relacionadas."""

    # 1. Buscar noticias similares por ADN individual
    similar_news = find_similar_news_by_ticker(
        ticker=ticker,
        threshold=similarity_threshold,
        limit=len(all_news)
    )

    if not similar_news:
        return [], {"method": "semantic_dna", "count": 0}

    # 2. Mapear a news items completos
    news_map = {news['id']: news for news in all_news}
    related_news = []

    for item in similar_news:
        news_id = item['news_id']
        similarity = item['similarity']

        if news_id in news_map:
            news_with_meta = news_map[news_id].copy()
            news_with_meta['_similarity'] = similarity
            news_with_meta['_match_method'] = 'semantic_dna_match'
            related_news.append(news_with_meta)

    return related_news, {
        "ticker": ticker,
        "method": "semantic_dna_match",
        "similarity_threshold": similarity_threshold,
        "total_count": len(related_news)
    }
```

---

## **4. ESTRATEGIA DE GENERACIÓN DE EMBEDDINGS**

### **4.1 Generación Batch**

```python
def generate_embeddings_for_news(
    news_list: List[Dict],
    batch_size: int = 50
) -> int:
    """Genera embeddings para noticias sin ellos."""

    # Get unembedded news
    unembedded_ids = get_unembedded_news(limit=len(news_list))

    if not unembedded_ids:
        return 0  # All news already have embeddings

    # Process in batches
    for i in range(0, len(unembedded_ids), batch_size):
        batch_ids = unembedded_ids[i:i + batch_size]

        # Prepare texts
        texts = []
        for news_id in batch_ids:
            news = next(n for n in news_list if n['id'] == news_id)
            text = f"{news.get('title', '')} {news.get('summary', '')}"
            texts.append(text)

        # Generate embeddings
        embeddings = generate_embeddings_batch(
            texts,
            task_type="SEMANTIC_SIMILARITY",
            output_dimensionality=768
        )

        # Save to DB
        embeddings_data = [
            (news_id, str(emb), 768, 'gemini-embedding-001')
            for news_id, emb in zip(batch_ids, embeddings)
        ]
        save_news_embeddings_batch(embeddings_data)

    return len(unembedded_ids)
```

---

### **4.2 Tipos de Embeddings**

| Tipo | Uso | Dimensiones | Modelo |
|------|-----|-------------|--------|
| Noticias | Búsqueda semántica | 768 | gemini-embedding-001 |
| Ticker ADN | Perfil del activo | 768 | gemini-embedding-001 |
| Queries | Búsqueda personalizada | 768 | gemini-embedding-001 |

---

## **5. WORKFLOW DE ANÁLISIS**

### **5.1 Pipeline Completo**

```python
def run_workflow(hours_back: int = 48):
    """Workflow completo de análisis."""

    # PASO 0: Extraer y validar noticias
    news_result = extract_and_validate_news(
        hours_back=hours_back,
        min_news_count=10,
        max_age_hours=24
    )

    if not news_result['success']:
        return {'success': False, 'error': 'No hay noticias frescas'}

    # PASO 1: Generar embeddings si no existen
    all_news = news_result['news_items']
    embeddings_count = generate_embeddings_for_news(all_news)

    # PASO 2: Para cada ticker, buscar noticias relacionadas
    for ticker in tickers:
        related_news, stats = find_related_news_for_ticker(
            ticker,
            all_news,
            method='semantic',
            similarity_threshold=0.80
        )

        # PASO 3: Analizar sentimiento de TOP 8 noticias
        for news in related_news[:8]:
            sentiment = analyze_sentiment(
                f"TICKER: {ticker}\nTITLE: {news['title']}\n...",
                ticker=ticker
            )

        # PASO 4: Generar recomendación (60/40 Quant/Semantic)
        recommendation = generate_recommendation(
            ticker=ticker,
            semantic_signals=semantic_signals,
            quant_indicators=quant_stats
        )

    return {
        'success': True,
        'embeddings_generated': embeddings_count,
        'analyzed_tickers': len(tickers)
    }
```

---

## **6. VENTAJAS DEL SISTEMA ACTUAL**

### **6.1 vs Sistema Anterior de Entities**

| Aspecto | Entities (Antiguo) | Embeddings (Actual) |
|---------|-------------------|---------------------|
| **Búsqueda** | Keyword matching exacto | Semantic similarity |
| **Escalabilidad** | Limited por keywords | Ilimitado |
| **Flexibilidad** | Rígido | Adaptativo |
| **Mantenimiento** | Manual | Automático |
| **Precision** | Alta solo para matches exactos | Alta incluso para variaciones |

---

### **6.2 Capacidades Únicas**

- ✅ **Búsqueda conceptual**: Encuentra "oil prices" aunque busca "crude oil"
- ✅ **Multi-idioma**: Funciona across lenguajes
- ✅ **Descubrimiento**: Encuentra relaciones no obvias
- ✅ **ADN del ticker**: Perfil semántico multi-dimensional
- ✅ **Umbral ajustable**: 0.80 default, configurable por caso de uso

---

## **7. MÉTRICAS DE ÉXITO**

### **7.1 Cobertura de Embeddings**

```
Target: ≥ 80% de noticias con embeddings
Método: count_news_embeddings() / total_news
Frecuencia: Cada ejecución de pipeline
```

### **7.2 Calidad de Búsqueda**

```
Target: ≥ 5 noticias relevantes por ticker (threshold 0.80)
Método: len(find_related_news_for_ticker(...))
Frecuencia: Cada análisis de ticker
```

### **7.3 Performance de Embeddings**

```
Target: ≤ 10s para generar 50 embeddings
Método: Medir tiempo en generate_embeddings_for_news()
Frecuencia: Monitoreo continuo
```

---

## **8. PRÓXIMOS PASOS**

1. ✅ **Implementado**: Sistema de embeddings semánticos
2. ✅ **Implementado**: Búsqueda con umbral 0.80
3. ✅ **Implementado**: ADN individual de tickers
4. ⏳ **Pendiente**: Tuning de threshold según resultados
5. ⏳ **Pendiente**: Expansión a más fuentes de noticias
6. ⏳ **Pendiente**: Métricas de precisión de búsqueda

---

**Última actualización**: 2026-04-13
**Estado**: 100% funcional
**Próxima revisión**: 2026-04-20
