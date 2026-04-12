# Plan de Mejora: Grado Institucional (Mesa de Inversiones Autónoma)

## Objetivo
Elevar la arquitectura de la mesa de inversiones autónoma a un estándar de grado institucional (Tier 1 Hedge Fund) abordando fallos críticos descubiertos durante la auditoría: el "Echo Chamber" en la asignación de noticias, la ilusión matemática del sentimiento promedio, la falta de validadores de cordura (sanity checks) para datos cuantitativos anómalos y la gestión de riesgo estática (hardcodeada).

## Archivos Clave & Contexto
- `scripts/analyze_ticker.py`: Orquestador principal del análisis por ticker (NLP, Extracción, UI Payload).
- `trading_mvp/agents/decision_agent.py`: Motor de decisiones 60/40 y ejecución de órdenes.
- `trading_mvp/analysis/gemini_sentiment.py`: Análisis de sentimiento de Gemini (Prompting y Parsing).

## Pasos de Implementación

### Fase 1: Reestructuración NLP y Eliminación del "Echo Chamber"
1. **Modificar `analyze_ticker.py` (Sección 5 - Build UI Objects)**:
   - Eliminar el fallback que asigna noticias neutrales a `bear_items` o `bull_items` cuando estos están vacíos (`if not bear_items... bear_items = neutral[:2]`).
   - Si no hay evidencia alcista o bajista pura, el caso correspondiente (`bull_case` o `bear_case`) debe quedar vacío o con un mensaje explícito de "No se encontraron factores de riesgo/catalizadores en las noticias recientes". Esto forzará un debate adversarial real entre los agentes lógicos.

### Fase 2: Corrección de la "Ilusión Matemática" del Sentimiento
1. **Modificar `analyze_ticker.py` (Sección 4 - Aggregate Patterns)**:
   - Implementar el cálculo de la **Dispersión del Sentimiento** (Varianza o Desviación Estándar de los `sentiment_score`).
   - Si la media del sentimiento es cercana a 0.0 pero la dispersión es alta (ej. noticias de +0.8 y -0.8 simultáneamente), clasificar el sentimiento general de la narrativa como `HIGH_VOLATILITY` o `MIXED_EXTREMES` en lugar de `NEUTRAL`.
   - Ajustar el `recommendation` y `rationale` (Sección 6) para reflejar la incertidumbre cuando hay dispersión extrema.

### Fase 3: Filtros Quant de Grado Institucional (Sanity Checks)
1. **Modificar `decision_agent.py` (`_calculate_quant_score` y lógicas de validación)**:
   - Añadir validadores de cordura para `Beta`. Si `beta_spy` es `< -1.0` o `> 3.0`, registrar una alerta crítica (`logger.warning`) y penalizar el `sens_score` o invalidar la señal técnica, ya que indica una descorrelación anómala o datos corruptos.
   - Reforzar la penalización si faltan datos críticos como `Corr SPY` o si el `RVOL` indica una liquidez anormalmente baja que contradice el volumen de noticias.

### Fase 4: Gestión de Riesgos Dinámica Estricta
1. **Modificar `analyze_ticker.py` (Payload de Salida)**:
   - Eliminar el hardcodeo del `stop_loss: {"percentage": 0.05}` en la clave `risk_analysis` del JSON de salida. El payload debe reflejar el múltiplo de ATR calculado dinámicamente o dejar que el `decision_agent` sea la única fuente de verdad para el stop.
2. **Modificar `decision_agent.py` (`_handle_bullish`)**:
   - Refinar la lógica del Stop Loss. Actualmente usa `1.5 * ATR` pero tiene un fallback hardcodeado del 7% (`0.07`). Cambiar este comportamiento para que, si el ATR no está disponible, la decisión de inversión reduzca significativamente el `position_size` o se clasifique como `IGNORED` por falta de datos de riesgo fiables, en lugar de asumir un riesgo estático ciego.

## Verificación y Pruebas
1. **Test de NLP**: Ejecutar `python scripts/analyze_ticker.py USO` y verificar que las secciones de Toro y Oso no compartan las mismas noticias neutrales y que reporten un sentimiento de alta dispersión si hay noticias polarizadas.
2. **Test Quant**: Simular un payload quant con un Beta anómalo (ej. -1.91) y verificar que `decision_agent.py` capture la anomalía y penalice el trade.
3. **Test de Riesgo**: Ejecutar un análisis donde el ATR falle o no esté disponible y confirmar que el sistema reacciona de forma defensiva (reduciendo tamaño de posición o abortando) en lugar de aplicar un stop del 7%.
