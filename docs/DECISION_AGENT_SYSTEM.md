# 🤖 SISTEMA DE TRADING AUTÓNOMO INSTITUCIONAL - COMPLETO

## 🎯 Visión General

Sistema de trading de grado institucional que abarca desde la recolección de noticias hasta la toma autónoma de decisiones de inversión. Implementa controles de riesgo estrictos, eliminación de sesgos (Echo Chamber) y cálculos cuantitativos robustos.

---

## 🏗️ Arquitectura del Sistema

### **4 PILARES PRINCIPALES**

#### 1️⃣ **PIPELINE DE NOTICIAS (Data Ingestion)**
```bash
python run_daily_geomacro.py
```
- Recolecta noticias de múltiples fuentes (Google News).
- Extrae entidades con IA (Gemini).
- Almacena en BD con timestamps y **Deduplicación por URL Hash MD5**.
- **Gestión Institucional del Ciclo de Vida**: Cron Job (`pg_cron`) de TTL (Time To Live) estricto de 90 días ejecutándose a medianoche, limpiando automáticamente la base de datos de noticias ya absorbidas por los precios ("priced-in").
- **Visión 360 (10-Categorías)**: Búsqueda estructural distribuida en dimensiones temáticas precisas, limitadas a **13 items** por consulta para optimizar el análisis semántico y prevenir dilución del LLM.
- **Frecuencia (Execution Rhythm)**: 2 veces al día (Pre-Market 08:30 AM EST y Power Hour 15:00 PM EST). Se han abandonado los ciclos antiguos de 6 horas para alinearse con la liquidez institucional.

#### 2️⃣ **MESA DE INVERSIONES (Analysis & Quant Engine)**
```bash
python run_investment_desk.py --watchlist-id 3
```
- Analiza TODOS los tickers en la watchlist.
- **NLP Echo Chamber Elimination**: Elimina fallbacks. Los paneles de UI ahora solo muestran evidencia estrictamente polarizada.
- **Sentiment Variance**: El cálculo de sentimiento incorpora la varianza para detectar ilusiones de 'HIGH_VOLATILITY' (donde la media parece neutral pero la dispersión es excesivamente alta).
- **Cálculos Cuantitativos Institucionales**:
  - **Wilder's Smoothing (alpha=1/14)**: Utilizado rigurosamente para el cálculo de RSI y ATR, eliminando el sesgo de medias simples.
  - **Volatilidad Histórica Anualizada Verdadera**: Calculada utilizando `pct_change` y `sqrt(252)` en lugar de desviaciones estándar nominales básicas.
- **Quant Sanity Checks**:
  - **Detección de Anomalías de Beta**: Si Beta es < -1.0 o > 3.0, el puntaje de sensibilidad se invalida y se penaliza fuertemente.
  - **RVOL**: Penalizaciones aplicadas por baja liquidez relativa.
- Genera recomendaciones (BULLISH/BEARISH/CAUTIOUS) basadas en la convergencia de datos.

#### 3️⃣ **AGENTE DE DECISIONES (Decision Engine & Risk Management)**
```bash
# Modo MANUAL (solo sugerencias)
python test_decision_agent.py --watchlist-id 3

# Modo AUTOPILOT (decide y ejecuta automáticamente)
AUTOPILOT_MODE=on python test_decision_agent.py --watchlist-id 3
```
- Analiza recomendaciones de la mesa.
- **Risk Management Estricto & Pre-Emptivo**: 
  - **PASO 0 (Evaluación Mecánica)**: El Stop Loss (1.5x ATR) y el Take Profit (3.0x ATR) se calculan ANTES de cualquier evaluación cualitativa o modelo NLP. Si el precio actual cruza un umbral, se ejecuta mecánicamente el cierre ("Sell-Off").
  - **Cálculo Exacto de PnL con Scale-Ins**: Toda rentabilidad y límite de riesgo se basa matemáticamente en el **`avg_entry_price`** ponderado del bróker. Si existen compras promediadas, el sistema adapta el centro de masa de la operación automáticamente.
  - **No hay fallbacks harcodeados**: Si el ATR no se puede calcular o está ausente, la operación es **RECHAZADA (IGNORED)**.
- Calcula tamaño de posición dinámicamente.
- **Registra decisiones automáticamente**.

#### 4️⃣ **TRACKING & AUDITORÍA (Audit Trail)**
```bash
python manage_decisions.py history --ticker COP
```
- Trazabilidad completa e inmutable de decisiones.
- Performance tracking y learning loop.

---

## 🔄 Flujo Completo de Datos

```
1. NOTICIAS → Entidades → BD (08:30 AM / 15:00 PM EST)
   ├─ Filtrado estricto de Echo Chambers
   └─ Cálculo de Sentiment Variance (control de HIGH_VOLATILITY)

2. ENTIDADES + DATA CUANTITATIVA → Ticker Analysis
   ├─ ATR & RSI (Wilder's Smoothing)
   ├─ Beta Validation (-1.0 a 3.0)
   └─ COP: Convergencia alcista confirmada → BULLISH ✅

3. RECOMMENDATIONS → Decision Agent → Action
   ├─ COP (BULLISH)
   │  └─ Agente: FOLLOW → BUY $5055
   │     ├─ Stop: Dinámico estricto a 1.5x ATR
   │     └─ Target: Take profit calculado
   └─ Falla ATR: Operación IGNORED (sin fallbacks)
```

---

## 🤖 Decision Agent - Detalles

### **Reglas de Decisión y Gestión de Riesgo**

#### **BULLISH → BUY (FOLLOW)**
```
SI:
  - Confidence >= 0.80
  - Sentimiento Polarizado Confirmado (Sin Echo Chamber)
  - Sanity Checks OK (Beta entre -1.0 y 3.0, Liquidez RVOL OK)
  - ATR válido y calculado

ENTONCES:
  - Action: BOUGHT
  - Position Size: Base × confidence_multiplier
  - Stop Loss: Estrictamente 1.5x ATR
```

#### **RECHAZOS (IGNORED)**
```
SI:
  - ATR es nulo o inválido.
  - Beta < -1.0 o > 3.0 (Anomalía).
  - Volatilidad extrema sin dirección (HIGH_VOLATILITY por Sentiment Variance).

ENTONCES:
  - Action: NONE (IGNORED)
  - Reason: "Missing ATR / Risk Constraint Failed"
```

### **Configuración de Parámetros**

```python
# trading_mvp/agents/decision_agent.py

DecisionConfig(
    autopilot_enabled=True,
    max_position_size=10000.0,
    # El stop loss usa 1.5x ATR dinámicamente, sin fallback estático
    require_valid_atr=True,
    min_confidence_for_buy=0.80,
    base_position_size=5000.0,
    dry_run=True
)
```

---

## 🚀 Producción y Ejecución

### **Setup de Cron Jobs (Rhythm Institucional)**
```bash
# Pre-Market: 08:30 AM EST
30 8 * * 1-5 cd /path/to/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python test_decision_agent.py --watchlist-id 3

# Power Hour: 15:00 PM EST
0 15 * * 1-5 cd /path/to/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python test_decision_agent.py --watchlist-id 3
```

### **Monitoreo**
```bash
python manage_decisions.py audit --ticker COP --hours-back 48
```

---

## ✅ El Sistema está LISTO (Grado Institucional)

**Capacidades implementadas:**
1. ✅ **Pipeline sincronizado al mercado (08:30 / 15:00 EST)**
2. ✅ **Eliminación de Echo Chambers NLP y Sentiment Variance**
3. ✅ **Cálculos Cuantitativos Reales** (Wilder's Smoothing, True Annualized Volatility)
4. ✅ **Sanity Checks de Riesgo** (Beta Anomaly, RVOL Penalty)
5. ✅ **Stop Loss Dinámico Estricto** (1.5x ATR, sin fallbacks)
