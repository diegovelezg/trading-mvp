# 🏛️ Investment Desk v2 - Workflow Architecture

## 🎯 **Principios de Diseño**

### 1. **Fail-Fast** 🛑
- **Si cualquier paso falla críticamente, SE DETIENE la ejecución**
- **NO se opera con datos incompletos o inválidos**
- **Errores explícitos con stack traces completos**

### 2. **Logging Estructurado** 📊
- **Cada paso queda registrado con timestamps**
- **Inputs y outputs documentados**
- **Retención de 72 horas de logs**
- **Logs en JSON + archivo rotatorio**

### 3. **Paso 0: Noticias Frescas** 📰
- **PRIMER paso obligatorio: extraer noticias**
- **Validación de frescura (max 24h)**
- **Si no hay noticias recientes → NO operar**

---

## 🔄 **Flujo Completo (7 Pasos)**

```
PASO 0: NEWS EXTRACTION (CRÍTICO)
├─ Extraer noticias de Supabase
├─ Validar cantidad mínima (10+)
├─ Validar frescura (≤ 24h)
├─ Validar calidad de datos
└─ FAIL FAST si no pasa validaciones

PASO 1: LOAD PORTFOLIO
├─ Obtener posiciones desde Alpaca
├─ Obtener cuenta (buying power)
└─ FAIL FAST si falla conexión

PASO 2: LOAD WATCHLIST
├─ Obtener watchlist desde Dashboard
└─ FAIL FAST si no hay tickers

PASO 3: COMBINE TICKERS
├─ Portfolio ∪ Watchlist
└─ FAIL FAST si lista vacía

PASO 4: TICKER ANALYSIS
├─ Para cada ticker:
│   ├─ Entity mapping
│   ├─ News matching
│   ├─ Sentiment analysis
│   └─ Recommendation (BULLISH/BEARISH/CAUTIOUS)
└─ CONTINUE even if some fail (partial results OK)

PASO 5: AGGREGATION
├─ Agrupar por recommendation
├─ Calcular aggregate metrics
└─ FAIL FAST si falla agregación

PASO 6: DECISION ENGINE
├─ DecisionAgent.process_desk_recommendations()
├─ Filtros técnicos (RSI, trend)
├─ Position sizing (risk guardrails)
├─ Ejecutar ordenes si AUTOPILOT
└─ CONTINUE even if fails (operaciones manuales posibles)

PASO 7: PERSISTENCE
├─ Guardar en DB (investment_desk_runs)
├─ Guardar ticker_analyses
├─ Guardar decisions
└─ CONTINUE even if fails (ya tenemos resultados)
```

---

## 📂 **Sistema de Archivos**

```
logs/workflow_executions/
├── workflow.log (rotating, 1 file per hour)
├── execution_20250411_143022.json (log completo)
├── execution_20250411_150103.json
└── ... (72 horas máx)

Cada execution log contiene:
{
  "execution_id": "20250411_143022",
  "start_time": "2025-04-11T14:30:22",
  "end_time": "2025-04-11T14:35:47",
  "total_duration_seconds": 325.3,
  "total_steps": 7,
  "completed_steps": 6,
  "failed_steps": 1,
  "steps": [
    {
      "step_id": "news_extraction_001",
      "step_type": "news_extraction",
      "status": "completed",
      "start_time": "2025-04-11T14:30:22",
      "end_time": "2025-04-11T14:30:45",
      "duration_seconds": 23.2,
      "input_data": {...},
      "output_data": {...}
    },
    ...
  ]
}
```

---

## 🚨 **Errores Críticos vs Continuables**

### **CRÍTICOS (Fail-Fast)**
- ❌ **Paso 0 falla**: No hay noticias → ABORTAR
- ❌ **Paso 1 falla**: No se puede cargar portfolio → ABORTAR
- ❌ **Paso 2 falla**: No hay watchlist → ABORTAR
- ❌ **Paso 3 falla**: No hay tickers → ABORTAR
- ❌ **Paso 5 falla**: Agregación falla → ABORTAR

### **CONTINUABLES (Warning)**
- ⚠️ **Paso 4**: Algunos tickers fallan análisis → Continuar con exitosos
- ⚠️ **Paso 6**: Decision engine falla → Continuar (operaciones manuales)
- ⚠️ **Paso 7**: Persistencia falla → Continuar (ya tenemos resultados)

---

## 🔧 **Uso**

### **Ejecutar versión v2 (Fail-Fast)**
```bash
python ejecutar_mesa_inversiones.py
# O directamente:
python scripts/run_investment_desk_v2.py --hours-back 48
```

### **Ver logs de ejecución**
```bash
# Log actual
tail -f logs/workflow_executions/workflow.log

# Logs históricos
ls logs/workflow_executions/execution_*.json

# Ver ejecución específica
cat logs/workflow_executions/execution_20250411_143022.json | jq
```

### **Limpiar logs antiguos**
```python
from trading_mvp.core.workflow_orchestrator import WorkflowLogger
logger = WorkflowLogger(retention_hours=72)
logger.cleanup_old_logs()
```

---

## 📊 **Métricas de Ejecución**

Cada ejecución registra:
- **Tiempo total**: Suma de todos los pasos
- **Paso más lento**: Identificar cuellos de botella
- **Tasa de éxito**: completed_steps / total_steps
- **Ticker success rate**: analyzed_tickers / total_tickers

---

## 🛡️ **Garantías**

✅ **No silent failures**: Todo error se loggea explícitamente
✅ **No operación sin datos**: Paso 0 garantiza noticias frescas
✅ **Auditoría completa**: Cada paso queda registrado
✅ **Reproducibilidad**: Mismos inputs → mismo output
✅ **Post-mortem analysis**: Logs completos por 72 horas

---

## 🔄 **Migración desde v1**

| v1 | v2 |
|---|---|
| Noticias on-demand | **Paso 0 obligatorio** |
| Silent failures | **Fail-fast explícito** |
| Logging básico | **Logging estructurado JSON** |
| Sin audit trail | **72 horas de logs** |
| Operación sin validación | **Validación antes de operar** |

---

## 📝 **Ejemplo de Log Completo**

```json
{
  "execution_id": "20250411_143022",
  "start_time": "2025-04-11T14:30:22.123456",
  "end_time": "2025-04-11T14:35:47.654321",
  "total_duration_seconds": 325.53,
  "total_steps": 7,
  "completed_steps": 7,
  "failed_steps": 0,
  "steps": [
    {
      "step_id": "news_extraction_001",
      "step_type": "news_extraction",
      "status": "completed",
      "start_time": "2025-04-11T14:30:22.123456",
      "end_time": "2025-04-11T14:30:45.234567",
      "duration_seconds": 23.11,
      "input_data": {
        "hours_back": 48,
        "min_news_count": 10,
        "max_age_hours": 24
      },
      "output_data": {
        "success": true,
        "stats": {
          "total_news": 1523,
          "unique_news": 1498,
          "duplicates": 25,
          "source_count": 42
        }
      }
    },
    ...
  ]
}
```

---

## 🎯 **Checklist Antes de Operar**

- [ ] Paso 0 completado (news extraction OK)
- [ ] Portfolio cargado (buying power > 0)
- [ ] Watchlist válida (tickers > 0)
- [ ] Al menos 1 ticker analizado exitosamente
- [ ] Decision engine ejecutado (manual o auto)
- [ ] Logs guardados correctamente

**Solo cuando TODOS los checkpoints pasan → se puede operar.** 🚀
