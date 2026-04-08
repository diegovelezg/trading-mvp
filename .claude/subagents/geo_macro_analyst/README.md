# 🌍 GeoMacro Analyst - Sistema de Inteligencia Global

## 🎯 **Qué Hemos Construido**

### **El Agente que Faltaba**

GeoMacro Analyst es el sistema de **INTELIGENCIA GEOPOLÍTICA Y MACROECONÓMICA** que monitorea TODO el contexto global que afecta los mercados financieros:

- 🌐 **Geopolítica**: Conflictos, tensiones, guerras comerciales
- 🏛️ **Política**: Elecciones, cambios de gobierno, regulaciones
- 💰 **Economía Global**: Tasas de interés, inflación, PIB, desempleo
- 🛢️ **Commodities**: Petróleo, gas, oro, litio, materiales críticos
- 📦 **Comercio**: Aranceles, tratados, sanciones, políticas comerciales
- 🚨 **Crisis**: Desastres naturales, pandemias, crisis financieras
- 💻 **Tecnología**: Innovaciones disruptivas, regulaciones tech

## 🏗️ **Arquitectura del Sistema**

```
┌─────────────────────────────────────────────────────────────┐
│                  GEO_MACRO_ANALYST                          │
│              (Ejecución 2x por día)                         │
│                                                              │
│  📅 Morning Briefing (8:00 AM ET)                          │
│  📅 Afternoon Update (2:00 PM ET)                          │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──> 🔍 DATA COLLECTION
                 │    • News APIs (Reuters, Bloomberg, FT)
                 │    • Economic Data (Fed, ECB, etc.)
                 │    • Commodity Prices
                 │    • Geopolitical Risk Services
                 │
                 ├──> 🧠 AI ANALYSIS (Gemini 3.1 Pro)
                 │    • Clasificación de eventos
                 │    • Análisis de impacto cruzado
                 │    • Identificación de catalizadores
                 │    • Mapeo de sectores/regiones/tickers
                 │
                 ├──> 💾 PERSISTENCE
                 │    • Base de datos estructurada
                 │    • Índices para consulta eficiente
                 │    • Histórico de tendencias
                 │
                 └──> 📊 DISTRIBUTION
                      • API para otros agentes
                      • Alertas de eventos críticos
                      • Dashboards de monitoreo
```

## 📊 **Estructura de Insights**

Cada insight contiene:

```json
{
  "event_type": "geopolitical | economic | commodity | crisis | technological | regulatory | market_structure",
  "importance": "critical | high | medium | low",
  "title": "Título conciso del evento",
  "summary": "Resumen de 1-2 oraciones",
  "impact_analysis": "Análisis detallado de impacto en mercados",
  "affected_sectors": ["energy", "technology", "financials"],
  "affected_regions": ["US", "China", "Europe"],
  "affected_tickers": ["XOM", "TSLA", "JPM"],
  "time_horizon": "immediate | short | medium | long",
  "confidence_score": 0.9,
  "tags": ["oil", "geopolitics", "inflation"],
  "sources": ["reuters.com", "bloomberg.com"]
}
```

## 🔌 **Integración con Ecosistema**

### **Todos los Agentes Consumen Insights GeoMacro**

```
GeoMacro Analyst
    ↓
    ├──> Explorer Agent → Considera factores macro al descubrir oportunidades
    ├──> Hypothesis Generator → Incorpora contexto macro en thesis
    ├──> Macro Analyst (Sentiment) → Enriquece análisis de noticias
    ├──> Bull Researcher → Usa catalizadores macro en caso alcista
    ├──> Bear Researcher → Identifica riesgos macro bajistas
    ├──> Risk Manager → Evalúa riesgos sistémicos macro
    └──> Orchestrator → Sintetiza TODO con contexto completo
```

## 📈 **Ejemplo Real: Output del Sistema**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║              🌍 GEOMACRO INTELLIGENCE BRIEFING                             ║
║              2026-04-08 12:57:29                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 OVERVIEW (Last 24 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Insights: 8

By Importance:
  • CRITICAL: 3
  • HIGH: 3
  • MEDIUM: 2

By Event Type:
  • crisis: 2
  • geopolitical: 2
  • commodity: 1
  • regulatory: 1
  • economic: 1
  • technological: 1

🚨 CRITICAL INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 European Natural Gas Crisis Deepens Amid Supply Disruptions
   Type: crisis | Horizon: immediate
   Impact: Creates massive upward pressure on TTF gas futures. European industrial
   output, particularly in chemicals and heavy manufacturing, will face steep cost
   escalations. US LNG exporters stand to gain heavily...

📍 Middle East Tensions Disrupt Global Oil Supply
   Type: geopolitical | Horizon: immediate
   Impact: Immediate upside for crude oil futures and major energy conglomerates.
   Rising energy costs will pressure global transportation sectors...

📍 Renewed US-China Semiconductor Trade Tensions
   Type: geopolitical | Horizon: short
   Impact: Major headwind for global semiconductor companies reliant on Chinese
   end-markets. Anticipate increased volatility in major tech stocks...
```

## 🛠️ **Componentes Creados**

### **1. Core del Sistema**
- ✅ `.claude/subagents/geo_macro_analyst/agent.py` - Agente principal
- ✅ `trading_mvp/core/db_geo_macro.py` - Schema y operaciones DB
- ✅ `trading_mvp/core/macro_context.py` - API para otros agentes

### **2. Documentación**
- ✅ `geo_macro_analyst.md` - Especificación completa
- ✅ `INTEGRATION.md` - Guía de integración para otros agentes
- ✅ `README.md` - Este archivo

### **3. Configuración**
- ✅ `GEMINI_API_MODEL_04=gemini-3.1-pro-preview` - Modelo potente para análisis complejo
- ✅ Schema de base de datos con índices optimizados
- ✅ Funciones de consulta eficiente (ticker, sector, región)

## 🚀 **Cómo Usar**

### **Ejecución Manual**
```bash
# Sesion matutina (pre-market)
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --session morning

# Sesion vespertina (post-market)
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --session afternoon

# Ver resumen actual
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --summary

# Ver solo críticos
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --critical
```

### **Desde Otros Agentes**
```python
from trading_mvp.core.macro_context import get_macro_context_for_analysis

# Obtener contexto general
context = get_macro_context_for_analysis(hours=48)

# Para ticker específico
nvda_context = get_macro_context_for_analysis(ticker='NVDA', hours=72)

# Para sector
energy_context = get_macro_context_for_analysis(sector='energy', hours=48)

# Formateado para incluir en prompts
formatted = format_macro_context_for_prompt(context)
```

## 📊 **Beneficios Inmediatos**

### **Para el Sistema de Trading**
1. **Contexto Global**: Ya no operamos "en el vacío"
2. **Timing Mejorado**: Evitar entrar antes de eventos negativos
3. **Riesgo Reducido**: Alertas tempranas de crisis sistémicas
4. **Mejores Returns**: Aprovechar catalizadores macro
5. **Decisiones Informadas**: Todas las señales con contexto completo

### **Para los Agentes**
1. **Explorer**: Evita sectores con riesgo geopolítico
2. **Hypothesis**: Thesis enriquecidas con factores macro
3. **Bull/Bear**: Argumentos contextualizados con realidad global
4. **Risk Manager**: Evalúa riesgos sistémicos, no solo idiosincráticos
5. **Orchestrator**: Síntesis completa de micro + macro

## 🎯 **Próximos Pasos**

1. **Automatizar**: Configurar cron jobs para ejecución 2x/día
2. **Integrar**: Modificar todos los agentes para usar contexto macro
3. **Mejorar**: Agregar más fuentes de datos (APIs reales)
4. **Visualizar**: Crear dashboard de monitoreo macro
5. **Expandir**: Agregar más tipos de eventos y análisis

## 💡 **Impacto Estratégico**

**ANTES**: Sistema "micro" → Solo noticias de precios, sin contexto

**DESPUÉS**: Sistema "micro + macro" → Contexto global completo

Esto transforma el sistema de un simple analizador de noticias a una **plataforma de inteligencia de inversiones completa**.

---

**Status**: ✅ COMPLETADO Y PROBADO
**Modelo**: Gemini 3.1 Pro Preview
**Ejecución**: Manual (automatización pendiente)
**Integración**: Pendiente en otros agentes
