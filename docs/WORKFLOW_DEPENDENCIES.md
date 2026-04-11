# 🔗 Workflow Dependencies - Arquitectura Correcta

## Problema Identificado

El workflow actual tiene **dependencias implícitas** que no están validadas:

```
PASO 0: News Extraction
   ↓ (depende de)
PASO 0.5: Entity Extraction ❌ NO ESTÁ EN EL WORKFLOW
   ↓ (depende de)
PASO 4: Ticker Analysis
```

---

## Workflow CORRECTO con Dependencias

### **FASE 1: INGESTA DE DATOS (PREREQUISITOS)**

```python
# PASO 0: News Extraction & Validation
├─ Recolecta noticias de fuentes
├─ Valida frescura (≤ 24h)
├─ Valida cantidad mínima (≥ 10)
└─ FAIL si no pasa → NO continúa

# PASO 0.5: Entity Extraction (NUEVO - CRÍTICO)
├─ Procesa TODAS las noticias recolectadas
├─ Extrae entidades usando Gemini API
├─ Valida cobertura mínima (≥ 50% de noticias con entidades)
├─ Valida cantidad mínima de entidades (≥ 100)
└─ FAIL si no pasa → NO continúa a PASO 4
```

### **FASE 2: CARGA DE CONTEXTO**

```python
# PASO 1: Load Portfolio
├─ Obtiene posiciones desde Alpaca
└─ FAIL si falla → NO continúa

# PASO 2: Load Watchlist
├─ Obtiene watchlist desde Dashboard
├─ Valida que no esté vacía (o permite vacía)
└─ FAIL si falla → NO continúa

# PASO 3: Combine Tickers
├─ Portfolio ∪ Watchlist
├─ Valida lista no vacía (≥ 1 ticker)
└─ FAIL si vacía → NO continúa
```

### **FASE 3: ANÁLISIS (REQUIERE PASO 0.5 COMPLETO)**

```python
# PASO 4: Ticker Analysis
├─ Para cada ticker:
│   ├─ Entity mapping
│   ├─ News matching (requiere entidades extraídas)
│   ├─ Sentiment analysis (requiere entidades)
│   └─ Recommendation
├─ Valida que al menos 1 ticker tenga análisis exitoso
└─ FAIL si todos fallan → NO continúa
```

---

## Dependencias por Paso

| Paso | Dependencias | Validación | Fail si |
|------|--------------|------------|---------|
| 0    | Ninguna      | News ≥ 10, frescura OK | ✅ |
| 0.5  | **PASO 0**   | Entidades en ≥ 50% noticias | ✅ |
| 1    | Ninguna      | Conexión Alpaca OK | ✅ |
| 2    | Ninguna      | Dashboard API OK | ✅ |
| 3    | **PASO 1, 2** | Lista no vacía | ✅ |
| 4    | **PASO 0.5, 3** | ≥ 1 ticker analizado | ✅ |
| 5    | **PASO 4**    | Agregación exitosa | ✅ |
| 6    | **PASO 5**    | Decision engine OK | ⚠️ (continuable) |
| 7    | **PASO 6**    | Persistencia OK | ⚠️ (continuable) |

---

## Implementación con Checkpoints

```python
def run_workflow_with_dependencies():
    """Workflow con validación de dependencias."""

    # ============================================================
    # FASE 1: INGESTA DE DATOS (CRÍTICA)
    # ============================================================

    # PASO 0: News Extraction
    step0_result = execute_step(
        name="PASO 0: News Extraction",
        function=extract_and_validate_news,
        fail_fast=True
    )

    # CHECKPOINT: ¿Tenemos noticias?
    assert step0_result['success'], "No hay noticias"
    assert step0_result['stats']['total_news'] >= 10, "Insuficientes noticias"

    # ============================================================
    # PASO 0.5: ENTITY EXTRACTION (NUEVO)
    # ============================================================

    step0_5_result = execute_step(
        name="PASO 0.5: Entity Extraction",
        function=extract_all_entities,
        input_data={
            'hours_back': 48,
            'min_coverage_pct': 0.5,  # 50% mínimo
            'min_total_entities': 100
        },
        fail_fast=True  # CRÍTICO
    )

    # CHECKPOINT: ¿Tenemos entidades suficientes?
    assert step0_5_result['success'], "Entity extraction falló"
    assert step0_5_result['coverage'] >= 0.5, "Cobertura entidades < 50%"
    assert step0_5_result['total_entities'] >= 100, "Entidades insuficientes"

    # ============================================================
    # FASE 2: CARGA DE CONTEXTO
    # ============================================================

    # PASO 1-3: Portfolio, Watchlist, Combine
    ...
    # CHECKPOINT: ¿Tenemos tickers para analizar?
    assert len(all_tickers) > 0, "No hay tickers"

    # ============================================================
    # FASE 3: ANÁLISIS
    # ============================================================

    # PASO 4: Ticker Analysis (AHORA PUEDE FUNCIONAR)
    step4_result = execute_step(
        name="PASO 4: Ticker Analysis",
        function=analyze_all_tickers,
        fail_fast=True
    )

    # CHECKPOINT: ¿Al menos 1 ticker analizó?
    analyzed = [t for t in step4_result if t['success']]
    assert len(analyzed) >= 1, "Ningún ticker analizó correctamente"
```

---

## Tipos de Fallos

### **FAIL-FAST (Críticos - Detienen ejecución):**
- ❌ Paso 0: No hay noticias frescas
- ❌ **Paso 0.5: Entidades insuficientes** ← NUEVO
- ❌ Paso 1: No se puede conectar a Alpaca
- ❌ Paso 2: No hay watchlists disponibles
- ❌ Paso 3: No hay tickers para analizar
- ❌ Paso 4: Ningún ticker pudo analizarse
- ❌ Paso 5: Agregación falla

### **CONTINUABLE (Warnings - No detienen):**
- ⚠️ Paso 6: Decision engine falla (operaciones manuales posibles)
- ⚠️ Paso 7: Persistencia falla (ya tenemos resultados)

---

## Métricas de Salud por Paso

Cada paso debe reportar:

```python
{
    "step_id": "entity_extraction_001",
    "status": "completed",
    "input_data": {...},
    "output_data": {
        "total_news": 211,
        "processed_news": 211,  # ← CRÍTICO: TODAS
        "entities_extracted": 1500,
        "coverage_pct": 0.85,  # ← CRÍTICO: ≥ 50%
        "health_status": "healthy"  # healthy | degraded | failed
    },
    "validation_checks": {
        "min_news_passed": true,
        "min_coverage_passed": true,
        "min_entities_passed": true,
        "all_checks_passed": true  # ← CRÍTICO
    }
}
```

---

## Prioridad de Arreglo

1. **URGENTE**: Agregar PASO 0.5 al workflow
2. **URGENTE**: Validar cobertura de entidades antes de Paso 4
3. **IMPORTANTE**: Implementar checkpoints entre pasos
4. **DESEABLE**: Health status por paso
