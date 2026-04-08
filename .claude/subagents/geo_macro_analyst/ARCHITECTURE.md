# 🏗️ Arquitectura: Procesamiento, Almacenamiento y Distribución

**Fecha**: 2026-04-08
**Agente**: GeoMacro Analyst
**Modelo**: GEMINI_API_MODEL_01 (gemini-3.1-flash-lite-preview)

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
        │       2. EXTRACCIÓN DE ENTITIES        │
        │       (GEMINI_API_MODEL_01)            │
        └─────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
      ┌─────────┐      ┌─────────┐      ┌─────────┐
      │ Entities│      │ Sectors │      │Regions  │
      │temáticas│      │         │      │         │
      └─────────┘      └─────────┘      └─────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ 3. ENRIQUECIMIENTO│
                    │   - Clustering    │
                    │   - Correlación   │
                    │   - Scoring       │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  4. ALMACENAMIENTO│
                    │   - Noticias      │
                    │   - Entities      │
                    │   - Insights      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ 5. DISTRIBUCIÓN   │
                    │   - Por ticker    │
                    │   - Por sector    │
                    │   - Por entity    │
                    └──────────────────┘
```

---

## **2. ESQUEMA DE BASE DE DATOS**

### **2.1 Tabla Principal: `geo_macro_news`**

```sql
CREATE TABLE geo_macro_news (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    content TEXT,
    url TEXT,
    source VARCHAR(50),          -- 'alpaca_news', 'google_news', 'serpapi'
    source_type VARCHAR(50),     -- 'news_api', 'rss', 'search_api'
    author VARCHAR(255),
    published_at TIMESTAMP,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Alpaca-specific
    symbols JSONB,               -- ['AAPL', 'MSFT']
    alpaca_id BIGINT,

    -- SERPAPI-specific
    serpapi_source VARCHAR(255),
    serpapi_date VARCHAR(100),

    -- Raw data
    raw_data JSONB,

    -- Indexing
    INDEX idx_source (source),
    INDEX idx_published (published_at DESC),
    INDEX idx_symbols (symbols),
    INDEX idx_collected (collected_at DESC)
);
```

### **2.2 Tabla: `geo_macro_entities`**

```sql
CREATE TABLE geo_macro_entities (
    id SERIAL PRIMARY KEY,
    news_id INTEGER REFERENCES geo_macro_news(id) ON DELETE CASCADE,

    -- Entity information
    entity_name VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50),    -- 'theme', 'commodity', 'region', 'event', 'policy'

    -- Analysis
    impact VARCHAR(20),          -- 'positive', 'negative', 'neutral'
    confidence FLOAT,            -- 0.0 to 1.0

    -- Relations
    sectors JSONB,               -- ['Energy', 'Transportation']
    regions JSONB,               -- ['Middle East', 'Iran']
    tickers JSONB,               -- ['USO', 'XLE', 'BNO']

    -- Metadata
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(100),     -- 'gemini-3.1-flash-lite-preview'

    -- Indexing
    INDEX idx_entity_name (entity_name),
    INDEX idx_entity_type (entity_type),
    INDEX idx_impact (impact),
    INDEX idx_sectors (sectors),
    INDEX idx_regions (regions),
    INDEX idx_tickers (tickers),
    UNIQUE (news_id, entity_name)  -- One entity per news item
);
```

### **2.3 Tabla: `geo_macro_insights`**

```sql
CREATE TABLE geo_macro_insights (
    id SERIAL PRIMARY KEY,

    -- Core insight
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    impact_level VARCHAR(20),    -- 'critical', 'high', 'medium', 'low', 'positive'
    confidence FLOAT,            -- 0.0 to 1.0

    -- Entities relation
    related_entities JSONB,      -- ['Oil', 'Geopolitical tension']
    related_sectors JSONB,       -- ['Energy', 'Shipping']
    related_regions JSONB,       -- ['Middle East', 'Global']

    -- Tickers relation
    affected_tickers JSONB,      -- ['USO', 'XLE', 'BNO', 'WTI']
    ticker_impacts JSONB,        -- {'USO': 'positive', 'XLE': 'positive'}

    -- Source
    source_news_ids JSONB,       -- [1, 2, 3] - IDs de noticias relacionadas
    source_count INTEGER,        -- Number of news items used

    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,        -- Insight expiration (optional)

    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'expired', 'actioned'

    -- Indexing
    INDEX idx_impact_level (impact_level),
    INDEX idx_created (created_at DESC),
    INDEX idx_entities (related_entities),
    INDEX idx_sectors (related_sectors),
    INDEX idx_tickers (affected_tickers),
    INDEX idx_status (status)
);
```

### **2.4 Tabla: `entity_relationships`**

```sql
CREATE TABLE entity_relationships (
    id SERIAL PRIMARY KEY,

    -- Related entities
    entity_a VARCHAR(255) NOT NULL,
    entity_b VARCHAR(255) NOT NULL,

    -- Relationship
    relationship_type VARCHAR(50), -- 'correlation', 'causal', 'co-occurrence'
    strength FLOAT,                -- 0.0 to 1.0
    direction VARCHAR(20),         -- 'positive', 'negative', 'neutral'

    -- Context
    co_occurrence_count INTEGER DEFAULT 1,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexing
    UNIQUE (entity_a, entity_b, relationship_type),
    INDEX idx_entity_a (entity_a),
    INDEX idx_entity_b (entity_b),
    INDEX idx_strength (strength DESC)
);
```

---

## **3. ESTRATEGIA DE EXTRACCIÓN DE ENTITIES**

### **3.1 Proceso de Extracción**

```python
def extract_entities_from_news(news: Dict) -> List[Dict]:
    """
    Extrae entities de una noticia usando Gemini.

    Args:
        news: Noticia normalizada

    Returns:
        Lista de entities extraídas
    """
    prompt = f"""
Extrae las entities de inversión clave de esta noticia:

Título: {news['title']}
Summary: {news.get('summary', '')}

Identifica:
1. ENTITIES (temas/sectores/commodities/regiones afectados)
2. ENTITY_TYPE (theme/commodity/region/event/policy)
3. IMPACT (positive/negative/neutral)
4. CONFIDENCE (0.0-1.0)
5. SECTORS (sectores específicos afectados)
6. REGIONS (regiones/países afectados)
7. TICKERS (tickers mencionados o relacionados - max 5)

Responde en JSON estricto:
{{
  "entities": [
    {{
      "entity_name": "Oil",
      "entity_type": "commodity",
      "impact": "positive",
      "confidence": 0.9,
      "sectors": ["Energy", "Transportation"],
      "regions": ["Middle East"],
      "tickers": ["USO", "XLE"]
    }}
  ]
}}
"""

    response = gemini_client.generate_content(
        model=GEMINI_API_MODEL_01,
        contents=prompt
    )

    return parse_gemini_entities_response(response)
```

### **3.2 Tipos de Entities**

| Tipo | Descripción | Ejemplos |
|------|-------------|----------|
| **theme** | Temáticas macro | "Trade war", "Elections", "Brexit" |
| **commodity** | Commodities | "Oil", "Gold", "Copper", "Wheat" |
| **region** | Regiones geográficas | "Middle East", "Latin America", "APAC" |
| **event** | Eventos específicos | "Strait of Hormuz closure", "Fed meeting" |
| **policy** | Políticas públicas | "Interest rate hike", "Tariff imposition" |
| **sector** | Sectores económicos | "Technology", "Energy", "Financials" |
| **indicator** | Indicadores económicos | "Inflation", "GDP", "Unemployment" |

---

## **4. ESTRATEGIA DE DISTRIBUCIÓN**

### **4.1 Por Ticker**

```python
def get_insights_for_ticker(ticker: str) -> List[Dict]:
    """
    Obtiene insights relevantes para un ticker específico.

    Args:
        ticker: Símbolo de ticker (ej: 'AAPL')

    Returns:
        Lista de insights relevantes
    """
    query = """
        SELECT * FROM geo_macro_insights
        WHERE ticker_impacts->? IS NOT NULL
        OR ? = ANY(affected_tickers)
        ORDER BY created_at DESC
        LIMIT 20
    """

    return db.execute(query, (ticker, ticker))
```

**Uso**: Explorer Agent puede pedir insights para tickers descubiertos

### **4.2 Por Sector**

```python
def get_insights_for_sector(sector: str) -> List[Dict]:
    """
    Obtiene insights relevantes para un sector.

    Args:
        sector: Nombre del sector (ej: 'Technology')

    Returns:
        Lista de insights relevantes
    """
    query = """
        SELECT * FROM geo_macro_insights
        WHERE ? = ANY(related_sectors)
        ORDER BY impact_level DESC, created_at DESC
        LIMIT 20
    """

    return db.execute(query, (sector,))
```

**Uso**: Hypothesis Generator puede filtrar ideas por sector

### **4.3 Por Entity Temática**

```python
def get_insights_for_entity(entity_name: str) -> List[Dict]:
    """
    Obtiene insights relacionados con una entity temática.

    Args:
        entity_name: Nombre de entity (ej: 'Oil', 'Fed', 'Trade war')

    Returns:
        Lista de insights relacionados
    """
    query = """
        SELECT * FROM geo_macro_insights
        WHERE ? = ANY(related_entities)
        ORDER BY created_at DESC
        LIMIT 20
    """

    return db.execute(query, (entity_name,))
```

**Uso**: Descubrir oportunidades temáticas (ej: "¿qué afecta a Oil?")

### **4.4 Por Región**

```python
def get_insights_for_region(region: str) -> List[Dict]:
    """
    Obtiene insights relevantes para una región.

    Args:
        region: Nombre de región (ej: 'Middle East', 'China')

    Returns:
        Lista de insights relevantes
    """
    query = """
        SELECT * FROM geo_macro_insights
        WHERE ? = ANY(related_regions)
        ORDER BY impact_level DESC, created_at DESC
        LIMIT 20
    """

    return db.execute(query, (region,))
```

**Uso**: Análisis geográfico de riesgos/opportunities

---

## **5. WORKFLOW COMPLETO**

### **5.1 Ingesta Diaria**

```python
def daily_ingestion():
    """Ingesta noticias y extrae entities."""

    # 1. Fetch news from all sources
    alpaca_news = AlpacaNewsConnector().fetch_macro_news(hours_back=24)
    google_news = GoogleNewsConnector().fetch_geopolitical_news(max_items=50)
    serpapi_news = SerpApiConnector().fetch_macro_news()

    # 2. Normalize and store
    all_news = normalize_and_store(alpaca_news + google_news + serpapi_news)

    # 3. Extract entities from each news
    for news in all_news:
        entities = extract_entities_from_news(news)
        store_entities(news['id'], entities)

    # 4. Generate insights
    insights = generate_insights_from_entities(all_news, entities)
    store_insights(insights)

    # 5. Update entity relationships
    update_entity_relationships(entities)

    return {
        'news_count': len(all_news),
        'entities_count': sum(len(e) for e in entities),
        'insights_count': len(insights)
    }
```

### **5.2 Consulta Multi-dimensional**

```python
def query_insights(
    tickers: List[str] = None,
    sectors: List[str] = None,
    entities: List[str] = None,
    regions: List[str] = None,
    impact_level: str = None,
    hours_back: int = 24
) -> List[Dict]:
    """
    Consulta insights con múltiples filtros.

    Args:
        tickers: Lista de tickers
        sectors: Lista de sectores
        entities: Lista de entities
        regions: Lista de regiones
        impact_level: Nivel de impacto ('critical', 'high', 'medium', 'low')
        hours_back: Horas hacia atrás

    Returns:
        Lista de insights filtrados
    """
    query = "SELECT * FROM geo_macro_insights WHERE 1=1"
    params = []

    if tickers:
        query += " AND affected_tickers ?| array[{}]"
        params.extend(tickers)

    if sectors:
        query += " AND related_sectors ?| array[{}]"
        params.extend(sectors)

    if entities:
        query += " AND related_entities ?| array[{}]"
        params.extend(entities)

    if regions:
        query += " AND related_regions ?| array[{}]"
        params.extend(regions)

    if impact_level:
        query += " AND impact_level = ?"
        params.append(impact_level)

    query += " AND created_at > NOW() - INTERVAL '? hours'"
    params.append(hours_back)

    query += " ORDER BY impact_level DESC, created_at DESC LIMIT 50"

    return db.execute(query, params)
```

---

## **6. VENTAJAS DE ESTE ENFOQUE**

### **6.1 Inversión Temática**
- ✅ Descubrir oportunidades basadas en **TEMAS**, no solo tickers
- ✅ Identificar **sectores y regiones** afectados por eventos
- ✅ Correlacionar **entities diferentes** (ej: "Oil" ↔ "Inflation")

### **6.2 Análisis Cross-Asset**
- ✅ Ver cómo **un evento afecta múltiples activos**
- ✅ Entender **transmisión de impactos** entre sectores
- ✅ Identificar **oportunidades de diversificación**

### **6.3 Distribución Inteligente**
- ✅ **Por ticker**: Para Explorer/Hypothesis agents
- ✅ **Por sector**: Para análisis sectorial
- ✅ **Por entity**: Para inversión temática
- ✅ **Por región**: Para análisis geográfico

### **6.4 Escalabilidad**
- ✅ Entities como ** índice de búsqueda**
- ✅ Relaciones entre entities para **descubrimiento**
- ✅ Historial de entities para **tendencias**

---

## **7. PRÓXIMOS PASOS**

### **Inmediato**
1. ✅ Crear esquema de DB
2. ✅ Implementar extractor de entities
3. ✅ Implementar pipeline de ingesta

### **Corto Plazo**
4. ⏳ Implementar funciones de distribución
5. ⏳ Crear endpoints de consulta
6. ⏳ Integrar con otros agentes

### **Mediano Plazo**
7. ⏳ Implementar clustering de entities
8. ⏳ Sistema de recomendación de entities relacionadas
9. ⏳ Dashboard de entities trending

---

**Status**: ✅ **Arquitectura definida, lista para implementación**
**Actualización**: 2026-04-08
