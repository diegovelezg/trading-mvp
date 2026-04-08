# 🏗️ Arquitectura: Entities WITHOUT Tickers

## **🔄 SEPARACIÓN DE CONCERNS**

```python
# ANTES (acoplado)
News → Entities + Tickers (todo en uno)

# AHORA (separado)
News → Entities (temas/commodities/sectores/regiones)
Ticker → Entities (mapping separada)
```

---

## **📊 ENTITY EXTRACTION (SIN TICKERS)**

### **Entidades que extraemos:**

| Tipo | Descripción | Ejemplos |
|------|-------------|----------|
| **theme** | Temáticas macro | "Trade war", "Elections", "Brexit" |
| **commodity** | Commodities | "Oil", "Gold", "Copper", "Wheat" |
| **region** | Regiones geográficas | "Middle East", "Latin America", "APAC" |
| **event** | Eventos específicos | "Strait of Hormuz closure", "Fed meeting" |
| **policy** | Políticas públicas | "Interest rate hike", "Tariff imposition" |
| **sector** | Sectores económicos | "Technology", "Energy", "Financials" |
| **indicator** | Indicadores económicos | "Inflation", "GDP", "Unemployment" |

### **NO extraemos:**
- ❌ Ticker symbols (AAPL, USO, XLE)
- ❌ ETF names
- ❌ Company-specific entities

---

## **🎯 TICKER → ENTITY MAPPING (SEPARADO)**

### **Opción 1: Static Mapping**

```python
# ticker_entities.py
TICKER_TO_ENTITIES = {
    "USO": ["Crude Oil", "Oil", "Energy", "Commodities"],
    "XLE": ["Energy", "Oil & Gas", "SPDR", "ETF"],
    "AAPL": ["Technology", "Consumer", "Hardware", "Semiconductors"],
    "ENPH": ["Solar Energy", "Renewable Energy", "Technology"],
    "SEDG": ["Solar Energy", "Renewable Energy", "Technology"],
}

def get_entities_for_ticker(ticker: str) -> List[str]:
    """Obtain entities for a specific ticker."""
    return TICKER_TO_ENTITIES.get(ticker, [])
```

### **Opción 2: Dynamic Mapping (via Watchlist Manager)**

```python
# Watchlist Manager aprende relación ticker→entity
def learn_ticker_entities(ticker: str, news_entities: List[str]):
    """Learn which entities are relevant for a ticker based on news."""
    
    # Si una noticia menciona "Oil" y el ticker es USO,
    # aprendemos que USO → ["Oil", "Energy"]
    
    relevant_entities = analyze_news_ticker_correlation(ticker, news_entities)
    update_ticker_mapping(ticker, relevant_entities)
```

---

## **🔍 QUERY: Ticker → News (VÍA ENTITIES)**

```python
def get_news_for_ticker(ticker: str, hours_back: int = 24):
    """Obtain news for a ticker via entity matching."""
    
    # 1. Get ticker's entities
    ticker_entities = get_entities_for_ticker(ticker)
    # ["Crude Oil", "Energy", "Commodities"] para USO
    
    # 2. Find news with those entities
    query = """
        SELECT n.* FROM geo_macro_news n
        JOIN geo_macro_entities e ON n.id = e.news_id
        WHERE e.entity_name IN (?, ?, ?)
        AND n.collected_at > datetime('now', '-' || ? || ' hours')
        ORDER BY n.published_at DESC
        LIMIT 20
    """
    
    return db.execute(query, (*ticker_entities, hours_back))
```

---

## **💡 EJEMPLO COMPLETO**

### **News → Entities (sin tickers)**

```python
# News: "Iran threatens to close Strait of Hormuz, oil prices surge 10%"

entities = extract_entities(news)
# Returns:
[
  {
    "entity_name": "Oil",
    "entity_type": "commodity",
    "impact": "positive",
    "confidence": 1.0,
    "sectors": ["Energy", "Transportation"],
    "regions": ["Middle East", "Global"]
    # NO "tickers" field
  },
  {
    "entity_name": "Strait of Hormuz",
    "entity_type": "region",
    "impact": "negative",
    "confidence": 0.95,
    "sectors": ["Energy", "Shipping"],
    "regions": ["Middle East"]
  }
]
```

### **Ticker → Entities (separado)**

```python
# Ticker mapping (pre-defined o learned)
USO → ["Crude Oil", "Oil", "Energy", "WTI", "Commodities"]
XLE → ["Energy", "Oil & Gas", "SPDR", "ETF"]

# Query news for USO
news_for_uso = get_news_for_ticker("USO")
# Finds news with entities ["Crude Oil", "Oil", "Energy"]
# Returns: ["Iran threatens to close Strait of Hormuz..."]
```

---

## **✅ VENTAJAS DE ESTE ENFOQUE**

### **1. Separación de Concerns**
- News processor → Solo sabe de news/entities
- Ticker analysis → Solo sabe de ticker/entities
- Cada uno evoluciona independientemente

### **2. Flexibilidad**
```python
# Si mañana quiero agregar crypto
BTC → ["Bitcoin", "Cryptocurrency", "Digital Asset"]
News con ["Bitcoin", "Crypto"] → automáticamente relacionadas
# Sin modificar news processing
```

### **3. Consulta Componible**
```python
# News para ticker (via entities)
get_news_for_ticker("USO")

# News para sector (via entities)
get_news_for_sector("Energy")

# News para región (via entities)
get_news_for_region("Middle East")

# News para entity específica
get_news_for_entity("Oil")

# TODAS usan el mismo mecanismo: entities
```

### **4. Entities como "Universal Translator"**

```
         News
          ↓
    [Entities] ← Universal Translator
          ↓
    ┌─────┴─────┐
    │           │
  Ticker      Sector
    │           │
   USO      Energy
```

---

## **🔄 FUTURO: Watchlist Manager**

### **Responsabilidad:**
- Mantener mappings ticker→entity
- Actualizar mappings basados en news
- Cache de relaciones ticker→news

### **Flujo:**
```python
# 1. Usuario crea watchlist con tickers
watchlist = create_watchlist(tickers=["USO", "XLE", "ENPH"])

# 2. Watchlist Manager aprende entities para cada ticker
for ticker in watchlist.tickers:
    entities = discover_ticker_entities(ticker, news_history)
    update_ticker_mapping(ticker, entities)

# 3. Análisis continuo
for ticker in watchlist.tickers:
    ticker_entities = get_ticker_entities(ticker)
    related_news = get_news_for_entities(ticker_entities)
    analyze_news_impact(related_news, ticker)
```

---

**Status**: ✅ Entity extraction modified to NOT extract tickers
**Actualización**: 2026-04-08
