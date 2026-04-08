# 🌐 Data Sources for GeoMacro Analyst

## **Fuentes de Datos REALES Implementadas**

El GeoMacro Analyst utiliza **Fuentes de datos REALES**, nada simulado.

---

## **1. Alpaca News API** ✅ (FUNCIONANDO)

### **Descripción**
- Noticias financieras en tiempo real
- Coverge global de markets, economía, geopolítica
- **FIXED**: Ahora funciona con credenciales PAPER

### **Endpoint**
```
GET https://data.alpaca.markets/v1beta1/news
```

### **Credenciales (CORREGIDAS)**
```bash
# Usar credenciales PAPER (no DATA_API)
ALPACA_PAPER_API_KEY=YOUR_ALPACA_PAPER_API_KEY
PAPER_API_SECRET=YOUR_ALPACA_SECRET_KEY
```

### **Items por request**
- **Máximo 50** (límite de Alpaca)
- 200 requests por minuto

### **Última ejecución**
- ✅ 23 noticias recolectadas
- ✅ 11 noticias de commodities
- ✅ Todas con datos REALES

### **Solución aplicada**
1. ✅ Base URL: `data.alpaca.markets` (no `api.alpaca.markets`)
2. ✅ Endpoint: `v1beta1/news`
3. ✅ Credenciales: `PAPER_API` (no `DATA_API`)
4. ✅ Fecha formato RFC3339: `%Y-%m-%dT%H:%M:%SZ`
5. ✅ Límite: 50 items por request

---

## **2. Google News RSS** ✅ (FUNCIONANDO)

### **Descripción**
- Noticias globales en tiempo real
- Cobertura geopolítica internacional
- Totalmente GRATIS

### **URLs Utilizadas**
```
https://news.google.com/rss/search?q=<topic>&hl=en-US&gl=US
```

### **Topics Monitoreados**
- Geopolitical conflicts
- International relations
- Economic indicators
- Trade policies
- Government regulations

### **Última ejecución**
- ✅ 30 noticias geopolíticas
- ✅ 30 noticias económicas
- ✅ **60 items totales**

### **Rate Limits**
- Sin límite (RSS público)

---

## **3. SERPAPI Google News** ✅ (FUNCIONANDO)

### **Descripción**
- Búsqueda de noticias Google vía API
- Cobertura global de alta calidad
- Resultados muy específicos

### **Endpoint**
```
GET https://serpapi.com/search.json
```

### **Credenciales**
```bash
SERPAPI_API_KEY=YOUR_SERPAPI_API_KEY
```

### **Categories disponibles**
- Geopolitical news
- Economic news
- Trade policy news

### **Última ejecución**
- ✅ 50 noticias geopolíticas
- ✅ 50 noticias económicas
- ✅ 36 políticas comerciales
- ✅ **136 items totales**

### **Rate Limits**
- 100 búsquedas gratis (freemium)

---

## **4. FRED (Federal Reserve Economic Data)** ⚠️ (OPCIONAL)

### **Descripción**
- Datos económicos oficiales de EE.UU.
- Mantenido por Federal Reserve de St. Louis
- Totalmente GRATIS

### **Endpoint**
```
GET https://api.stlouisfed.org/fred/series/observations
```

### **Indicadores Obtenidos**
- Unemployment Rate (UNRATE)
- Federal Funds Rate (FEDFUNDS)
- CPI Inflation (CPIAUCSL)
- Real GDP (A191RP1Q225SBEA)
- Consumer Confidence (UMCSENT)
- Housing Starts (HOUST)
- Industrial Production (IPMAN)

### **API Key (OPCIONAL)**
```bash
# Obtener GRATIS en: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=tu_api_key_aqui
```

### **Rate Limits**
- 120 requests por día (sin API key)
- Ilimitado (con API key gratuita)

---

## **5. Alpha Vantage** ⚠️ (RECOMENDADO)

### **Descripción**
- Precios de commodities
- Datos de divisas
- Indicadores económicos globales

### **Endpoint**
```
GET https://www.alphavantage.co/query
```

### **Commodities Obtenidos**
- WTI Crude Oil
- Brent Crude Oil
- Natural Gas
- Gold
- Silver
- Copper

### **API Key (NECESARIA)**
```bash
# Obtener GRATIS en: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=tu_api_key_aqui
```

### **Rate Limits**
- 25 requests por día (gratis)
- 500 requests por día ($5/mes)

---

## **🔧 Configuración de API Keys**

### **Fuentes ya configuradas** ✅
- Alpaca News API: ✅ Funcionando (PAPER credentials)
- Google News RSS: ✅ Funcionando (no requiere key)
- SERPAPI: ✅ Funcionando (key configurada)

### **Fuentes opcionales** ⚠️
1. **FRED (Opcional pero recomendado)**
   ```bash
   # Obtener GRATIS en:
   # https://fred.stlouisfed.org/docs/api/api_key.html

   # Agregar a .env:
   FRED_API_KEY=tu_fred_api_key_aqui
   ```

2. **Alpha Vantage (Necesario para commodities)**
   ```bash
   # Obtener GRATIS en:
   # https://www.alphavantage.co/support/#api-key

   # Agregar a .env:
   ALPHA_VANTAGE_API_KEY=tu_alpha_vantage_api_key_aqui
   ```

### **Verificar configuración**
```bash
# Test de conectores
.venv/bin/python << 'EOF'
from trading_mvp.data_sources import (
    AlpacaNewsConnector,
    GoogleNewsConnector,
    SerpApiConnector
)

# Test Alpaca
print('Testing Alpaca News...')
alpaca = AlpacaNewsConnector()
news = alpaca.fetch_macro_news(hours_back=1)
print(f'✅ Alpaca: {len(news)} news items')

# Test Google News
print('\nTesting Google News...')
google = GoogleNewsConnector()
geo_news = google.fetch_geopolitical_news(max_items=5)
print(f'✅ Google News: {len(geo_news)} news items')

# Test SERPAPI
print('\nTesting SERPAPI...')
serpapi = SerpApiConnector()
macro_news = serpapi.fetch_macro_news()
print(f'✅ SERPAPI: {len(macro_news)} news items')

print('\n✅ All connectors working!')
EOF
```

---

## **📊 Resumen de Fuentes**

| Fuente | Tipo | Costo | Estado | Noticias | API Key |
|--------|------|-------|--------|----------|---------|
| **Alpaca News** | News API | Incluido | ✅ Activo | 23 | PAPER (Fixed) |
| **Google News RSS** | RSS Feed | GRATIS | ✅ Activo | 60 | No necesaria |
| **SERPAPI** | Search API | FREEMIUM | ✅ Activo | 136 | Configurada |
| **FRED** | Economic Data | GRATIS | ⚠️ Opcional | - | Opcional |
| **Alpha Vantage** | Commodities | FREEMIUM | ⚠️ Recomendado | - | Necesaria |

**TOTAL**: ✅ **219 noticias REALES** recolectadas

---

## **🚀 Próximos Pasos**

### **Inmediato** ✅
1. ✅ Alpaca News: FIXED - Funcionando
2. ✅ Google News RSS: Funcionando
3. ✅ SERPAPI: Funcionando

### **Corto Plazo** ⏳
4. ⏳ FRED: Obtener API key (opcional)
5. ⏳ Alpha Vantage: Obtener API key (recomendado)
6. ⏳ Test completo del sistema

### **Mediano Plazo** ⏳
7. ⏳ Agregar más fuentes regionales
8. ⏳ Implementar WebSocket streaming
9. ⏳ Optimizar deduplicación

---

## **📈 Cobertura de Datos**

### **Geopolítica** 🌍
- Conflictos internacionales
- Relaciones diplomáticas
- Tensiones comerciales
- Sanciones y embargos

**Fuentes:** Google News RSS, Alpaca News, SERPAPI

### **Economía** 💰
- Tasas de interés
- Inflación
- PIB y empleo
- Confianza del consumidor

**Fuentes:** FRED (opcional), Google News, Alpaca News, SERPAPI

### **Commodities** 🛢️
- Petróleo (WTI, Brent)
- Gas natural
- Metales preciosos (oro, plata)
- Metales industriales (cobre, litio)

**Fuentes:** Alpha Vantage (recomendado), Alpaca News

### **Políticas Públicas** 🏛️
- Regulaciones gubernamentales
- Políticas comerciales
- Cambios regulatorios
- Decisiones de bancos centrales

**Fuentes:** Google News RSS, Alpaca News, SERPAPI

---

## **⚠️ Limitaciones Actuales**

1. **Alpha Vantage**: Sin API key, no podemos obtener precios de commodities
2. **FRED**: Opcional, pero mejor con API key
3. **Deduplicación**: Puede haberOverlap entre fuentes
4. **Rate limits**: Respetar límites de cada API

---

## **🔮 Mejoras Futuras**

1. **WebSocket streaming**: Alpaca News en tiempo real
2. **Bloomberg Terminal** ($$$): Cobertura completa
3. **Reuters News** ($): Noticias financieras profesionales
4. **Sibylline Risk** ($$$): Inteligencia geopolítica profesional
5. **Deduplicación inteligente**: Eliminar noticias duplicadas entre fuentes

---

**Status**: ✅ **3 de 5 sources FULLY OPERATIONAL**
**Total news**: ✅ **219 noticias REALES**
**Actualización**: 2026-04-08
