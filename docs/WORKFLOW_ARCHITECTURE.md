# 🏛️ Investment Desk v2 - Workflow Architecture Institucional

## 🎯 **Principios de Diseño**

### 1. **Fail-Fast & No Fallbacks** 🛑
- **Si cualquier paso falla críticamente, SE DETIENE la ejecución.**
- **NO se opera con datos incompletos o inválidos.**
- **Stop Loss Dinámico**: Ausencia de ATR resulta en rechazo inmediato de la operación (IGNORED). No existen fallbacks hardcodeados.

### 2. **Logging Estructurado** 📊
- Registros con timestamps detallados (JSON + rotatorio, retención 72h).
- Inputs y outputs documentados con stack traces completos.

### 3. **Rhythm Institucional (Execution Rhythm)** ⏱️
- **Sincronización de Mercado**: 2 ejecuciones al día.
  - **Pre-Market**: 08:30 AM EST.
  - **Power Hour**: 15:00 PM EST.
- (Se abandonan los cron jobs antiguos de 6 horas continuas).

---

## 🔄 **Flujo Completo Institucional (7 Pasos)**

```
PASO 0: NEWS EXTRACTION (CRÍTICO)
├─ Extraer noticias de Supabase (alineado al horario 08:30/15:00 EST)
├─ Estrategia Visión 360: 10 categorías (13 items máximo cada una).
├─ Deduplicación en BD vía Hash MD5 de URL (ON CONFLICT DO NOTHING).
├─ Limpieza Automática (TTL 90 días): Job pg_cron descartando news 'priced-in'.
├─ Validar cantidad mínima (10+) y frescura (≤ 24h)
└─ FAIL FAST si no pasa validaciones

PASO 1: LOAD PORTFOLIO
├─ Obtener posiciones desde Alpaca y account buying power
└─ FAIL FAST si falla conexión

PASO 2: LOAD WATCHLIST
├─ Obtener watchlist desde Dashboard
└─ FAIL FAST si no hay tickers

PASO 3: COMBINE TICKERS
├─ Portfolio ∪ Watchlist
└─ FAIL FAST si lista vacía

PASO 4: TICKER ANALYSIS (QUANT & NLP ENGINE)
├─ Para cada ticker:
│   ├─ NLP Echo Chamber Elimination: Evidencia estrictamente polarizada sin fallbacks.
│   ├─ Sentiment Variance: Filtrar ilusiones 'HIGH_VOLATILITY'.
│   ├─ Quant Math: Wilder's Smoothing (alpha=1/14) para RSI y ATR.
│   ├─ Volatility: True Annualized Historical Volatility (pct_change * sqrt(252)).
│   └─ Sanity Checks: Beta anomaly (< -1.0 o > 3.0 invalida), RVOL penalizaciones.
└─ CONTINUE (resultados parciales permitidos)

PASO 5: AGGREGATION
├─ Agrupar por recomendación institucional
└─ FAIL FAST si falla agregación

PASO 6: DECISION ENGINE (RISK MANAGEMENT & ACTIVE SIZING)
├─ PASO 0 (Pre-Emptive): Revisar SL (1.5x) y TP (3.0x) vs current_price.
│   └─ SI SE TOCA UMBRAL: 'Sell-Off' mecánico o Take Profit del 100%, ABORTAR análisis cualitativo.
├─ Process desk recommendations
├─ Active Position Management:
│   ├─ Pyramiding (Scale-In): Aumenta posición en ganadores si Confianza >= 0.85 y RSI < 65.
│   └─ Trimming (Recortes): Venta del 25% si PnL > 5% y agotamiento técnico (RSI > 75).
├─ Risk Guardrails: Stop Loss estrictamente en 1.5x ATR y validación contra MAX_PORTFOLIO_EXPOSURE.
├─ Reject Rule: Si falta ATR, el trade es IGNORED.
└─ CONTINUE (operaciones manuales o autopilotadas)

PASO 7: PERSISTENCE
├─ Guardar en DB (investment_desk_runs, análisis y decisiones)
└─ CONTINUE (preservación de auditoría inmutable)
```

---

## 🚨 **Controles de Riesgo Institucional**

### **Quant Sanity Checks (Paso 4)**
- **Wilder's Smoothing**: Impuesto para evitar señales falsas en RSI y ATR.
- **Beta Anomaly Detection**: Un Beta extremo (< -1.0 o > 3.0) señala datos corruptos o anomalías estructurales; la sensibilidad es penalizada/invalidada.
- **Volatilidad Verdadera**: Basada en 252 días (anualizada) sobre cambios porcentuales, descartando desviación estándar nominal básica.

### **Strict Risk Management (Paso 6)**
- **Dynamic Stop Loss Pre-Emptivo**: Evaluado como PASO 0 de riesgo mecánico, anclado irrevocablemente a **1.5x ATR**.
- **Cálculo Matemático PnL**: Basado rigurosamente en el `avg_entry_price` (precio promedio de las compras escalonadas/scale-ins).
- **Regla Anti-Fallback**: Históricamente se usaban porcentajes estáticos si fallaba el cálculo cuantitativo. Ahora, **sin ATR válido, no hay trade (IGNORED)**.

---

## 🔧 **Uso y Operación**

### **Ejecutar versión Institucional (Fail-Fast)**
```bash
python scripts/run_investment_desk.py --hours-back 48
```

### **Monitorización de Ejecuciones**
```bash
tail -f logs/workflow_executions/workflow.log
cat logs/workflow_executions/execution_20260411_143022.json | jq
```

---

## 🔄 **Evolución: De MVP a Institucional**

| MVP Antiguo | Grado Institucional Actual |
|---|---|
| Ejecución cada 6 horas | **2 veces al día (08:30 AM / 15:00 PM EST)** |
| Sentiment promedio simple | **Sentiment Variance + Echo Chamber Elimination** |
| RSI/ATR con medias simples | **Wilder's Smoothing (alpha=1/14)** |
| Stop Loss estático / Fallbacks | **1.5x ATR Estricto (Sin ATR = IGNORED trade)** |
| Volatilidad Nominal (StdDev) | **True Annualized Volatility (pct_change * sqrt(252))** |
| Beta sin límites | **Detección de Anomalías de Beta (-1.0 a 3.0)** |

---

## 🎯 **Checklist de Ejecución**

- [ ] Horario correcto (08:30 AM o 15:00 PM EST).
- [ ] Validación Quant superada (ATR calculado, Beta válido).
- [ ] Sentimiento verificado sin Echo Chamber.
- [ ] Risk Management aplicado (Stop Loss a 1.5x ATR).
- [ ] Ejecución y Logs guardados.

**Solo cuando TODOS los checkpoints y parámetros institucionales pasan → se toma la posición.** 🚀
