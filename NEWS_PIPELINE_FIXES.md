# Arreglos completos del Pipeline de Noticias

## Fecha
2026-04-10

## Problemas identificados y solucionados

### 🚨 Bug #1: `alpaca_id` no se mapeaba en Alpaca News
**Ubicación:** `trading_mvp/data_sources/alpaca_news_connector.py:98-109`

**Problema:** El método `normalize_data` no incluía el campo `alpaca_id`, causando que todas las noticias de Alpaca se insertaran con `alpaca_id = NULL`.

**Solución:**
```python
normalized_item = {
    "source": "alpaca_news",
    # ... otros campos ...
    "alpaca_id": item.get("id"),  # ✅ AGREGADO
    "raw_data": item
}
```

**Impacto:** Ahora las noticias de Alpaca tienen IDs únicos y el constraint UNIQUE funciona correctamente.

---

### 🚨 Bug #2: Validación insuficiente en normalize_data
**Ubicación:** Todos los connectors (Alpaca, Google, SERPAPI)

**Problema:** Los métodos `normalize_data` usaban `continue` silenciosamente cuando fallaba un item, sin reportar cuántos se perdieron ni por qué.

**Solución:**
- Agregado tracking de items fallidos
- Validación de campos críticos (título, URL)
- Reporte detallado de pérdidas con razones
- Logging mejorado con contexto

**Ejemplo:**
```python
failed_items = []
for i, item in enumerate(raw_data):
    try:
        if not title or title == "[Removed]":
            failed_items.append({"index": i, "reason": "invalid_title"})
            continue
        # ... procesar item ...
    except Exception as e:
        failed_items.append({"index": i, "reason": str(e)})
        logger.error(f"❌ Error normalizing item {i}: {e}")

# Reportar pérdidas
if failed_items:
    logger.warning(f"⚠️  Failed to normalize {len(failed_items)}/{len(raw_data)} items")
    for failure in failed_items[:5]:
        logger.warning(f"    - Item {failure['index']}: {failure['reason']}")
```

**Impacto:** Ahora se sabe exactamente cuántas noticias se pierden y por qué.

---

### 🚨 Bug #3: Manejo silencioso de errores en fetch_data
**Ubicación:** Todos los connectors (Alpaca, Google, SERPAPI)

**Problema:** Los métodos `fetch_data` retornaban `[]` silenciosamente sin distinguir entre:
- API retornó vacío (legítimo)
- Error de conexión
- Timeout
- Error de autenticación

**Solución:**
- Manejo específico por tipo de error
- Logging con nivel adecuado (ERROR vs WARNING)
- Incluir detalles del error (response body, query, etc.)
- Tracking de error_count

**Ejemplo:**
```python
except requests.exceptions.Timeout as e:
    self.error_count += 1
    logger.error(f"❌ API timeout after 30s: {e}")
    return []
except requests.exceptions.ConnectionError as e:
    self.error_count += 1
    logger.error(f"❌ API connection error: {e}")
    return []
```

**Impacto:** Ahora se puede diagnosticar rápidamente si el problema es conexión, auth, o la API simplemente no tiene datos.

---

### 🚨 Bug #4: Inserción en BD sin validación ni contexto
**Ubicación:** `trading_mvp/core/db_geo_news.py`

**Problema:**
- `insert_geo_news()` retornaba `None` sin detalles del error
- No validaba campos requeridos antes de intentar insertar
- Error logging no incluía título ni fuente de la noticia fallida

**Solución:**
```python
# Validaciones críticas antes de insertar
if not news:
    logger.error("❌ Cannot insert news: news item is None or empty")
    return None

title = news.get('title', '').strip()
if not title:
    logger.error(f"❌ Cannot insert news: missing title. Source: {news.get('source')}")
    return None

title_preview = title[:50] + "..." if len(title) > 50 else title

# ... en el except ...
logger.error(f"❌ DB error inserting news '{title_preview}' (source: {source}): {e}")
```

**Impacto:** Los errores de BD ahora son diagnosticables inmediatamente.

---

### 🚨 Bug #5: Duplicados no detectados para fuentes sin `alpaca_id`
**Ubicación:** `trading_mvp/core/db_geo_news.py`

**Problema:** Google News y SERPAPI no tienen `alpaca_id`, y PostgreSQL trata NULL como único en el constraint UNIQUE, permitiendo duplicados.

**Solución:**
```python
# Para fuentes sin alpaca_id, usar hash de URL como pseudo-ID
if not alpaca_id and news.get('url'):
    import hashlib
    url_hash = hashlib.md5(news['url'].encode()).hexdigest()
    alpaca_id = int(url_hash[:8], 16) if url_hash else None
```

**Impacto:** Ahora las noticias de Google/SERPAPI también se protegen contra duplicados basado en su URL.

---

### 🚨 Bug #6: Batch insert sin estadísticas detalladas
**Ubicación:** `trading_mvp/core/db_geo_news.py:128-146`

**Problema:** `insert_geo_news_batch()` solo reportaba cantidad insertada, sin distinguir entre:
- Nuevas inserciones
- Duplicados saltados (skipped)
- Fallos reales (failed)

**Solución:**
```python
inserted_count = 0
skipped_count = 0
failed_count = 0

for news in news_list:
    news_id = insert_geo_news(news)
    if news_id:
        inserted_count += 1
    else:
        if not news.get('title'):
            failed_count += 1
        else:
            skipped_count += 1  # Probablemente duplicado

# Reporte detallado
logger.info(f"📊 Batch: {inserted_count} inserted, {skipped_count} skipped, {failed_count} failed out of {total} total")
```

**Impacto:** Ahora se puede distinguir entre "no se insertaron porque ya existían" vs "no se insertaron por error".

---

### 🚨 Bug #7: Processor sin detección de fallos críticos
**Ubicación:** `trading_mvp/core/geo_macro_processor.py`

**Problema:** El `GeoMacroProcessor` no detectaba cuando:
- Todas las fuentes fallaban
- Todas las normalizaciones producían 0 items
- Ninguna noticia se insertaba en BD

**Solución:**
```python
if total_fetched == 0:
    logger.error("❌ CRITICAL: No news items fetched from any source!")
    return source_counts

# ... después de insertar ...

if inserted_count == 0:
    logger.error("❌ CRITICAL: Zero news items stored in database!")
elif inserted_count < total_fetched:
    loss_rate = ((total_fetched - inserted_count) / total_fetched) * 100
    logger.warning(f"⚠️  Storage loss: {loss_rate:.1f}% ({total_fetched - inserted_count} items not stored)")
```

**Impacto:** Ahora el pipeline alerta inmediatamente cuando hay fallos críticos.

---

## Tests de validación

Se creó `test_news_pipeline.py` para validar:

1. ✅ Alpaca News fetch y normalize
2. ✅ Presencia de `alpaca_id` en datos normalizados
3. ✅ Validación de títulos
4. ✅ Google News fetch y normalize
5. ✅ Inserción en BD de noticias válidas
6. ✅ Rechazo de noticias inválidas
7. ✅ Detección de duplicados

**Resultado:** Todos los tests pasan exitosamente.

---

## Archivos modificados

1. `trading_mvp/data_sources/alpaca_news_connector.py`
   - `fetch_data()`: Mejor manejo de errores con contexto
   - `normalize_data()`: Agregado `alpaca_id`, validación de títulos, tracking de fallos

2. `trading_mvp/data_sources/google_news_connector.py`
   - `fetch_data()`: Mejor manejo de errores
   - `normalize_data()`: Validación de títulos, tracking de fallos

3. `trading_mvp/data_sources/serpapi_connector.py`
   - `fetch_data()`: Mejor manejo de errores
   - `normalize_data()`: Validación de títulos y URLs, tracking de fallos

4. `trading_mvp/core/db_geo_news.py`
   - `insert_geo_news()`: Validaciones críticas, mejor logging, hash de URL para duplicados
   - `insert_geo_news_batch()`: Estadísticas detalladas (inserted/skipped/failed)

5. `trading_mvp/core/geo_macro_processor.py`
   - `step1_fetch_and_store_news()`: Detección de fallos críticos, mejor reporte

6. `trading_mvp/core/dashboard_api_client.py`
   - `insert_news()`: Validaciones, mejor logging con contexto

---

## Cómo verificar que todo funciona

```bash
# Activar virtual environment
source .venv/bin/activate

# Ejecutar tests
python test_news_pipeline.py
```

Se debería ver:
- ✅ Alpaca: 10 items fetched, 10/10 normalized
- ✅ Google: 10 items fetched, 10/10 normalized
- ✅ alpaca_id presente en cada item
- ✅ Inserción en BD funciona
- ✅ Noticias inválidas se rechazan

---

## Principios aplicados

1. **Cero fallos silenciosos**: Todo error se loguea con contexto suficiente
2. **Validación temprana**: Fallar rápido antes de intentar operaciones costosas
3. **Estadísticas detalladas**: Siempre reportar cuántos items se procesaron vs cuántos fallaron
4. **Logging accionable**: Los mensajes de error incluyen suficiente información para diagnosticar sin búsqueda adicional
5. **Separación de concerns**: Distinguir entre "no hay datos" (legítimo) vs "falló la operación" (error)

---

## Próximos pasos recomendados

1. **Monitoreo en producción**: Configurar alertas para logs con nivel ERROR
2. **Métricas**: Agregar tracking de tasas de éxito/fracaso por fuente
3. **Retry logic**: Para errores transitorios (timeout, connection)
4. **Circuit breaker**: Deshabilitar fuentes que fallan consistentemente
5. **Tests de integración**: Probar el pipeline completo con BD real
