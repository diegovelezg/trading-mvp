# 🤖 SISTEMA DE TRADING AUTÓNOMO - COMPLETO

## 🎯 Visión General

Sistema completo de trading que va desde la recolección de noticias hasta la toma autónoma de decisiones de inversión, con trazabilidad completa en cada paso.

---

## 🏗️ Arquitectura del Sistema

### **4 PILARES PRINCIPALES**

#### 1️⃣ **PIPELINE DE NOTICIAS (Data Ingestion)**
```bash
python run_daily_geomacro.py
```
- Recolecta noticias de 3 fuentes (Alpaca, Google News, SERPAPI)
- Extrae entidades con IA (Gemini)
- Almacena en BD con timestamps
- **Frecuencia**: 6 horas (cron job)

#### 2️⃣ **MESA DE INVERSIONES (Analysis Engine)**
```bash
python run_investment_desk.py --watchlist-id 3
```
- Analiza TODOS los tickers en watchlist
- Genera recomendaciones (BULLISH/BEARISH/CAUTIOUS)
- Compara entre tickers
- **Output**: Ranking + Recomendaciones consolidadas

#### 3️⃣ **AGENTE DE DECISIONES (Decision Engine)**
```bash
# Modo MANUAL (solo sugerencias)
python test_decision_agent.py --watchlist-id 3

# Modo AUTOPILOT (decide automáticamente)
AUTOPILOT_MODE=on python test_decision_agent.py --watchlist-id 3
```
- Analiza recomendaciones de la mesa
- Aplica reglas de decisión
- Calcula tamaño de posición
- Determina stop loss / take profit
- **Registra decisiones automáticamente**

#### 4️⃣ **TRACKING & AUDITORÍA (Audit Trail)**
```bash
python manage_decisions.py history --ticker COP
python manage_decisions.py performance --ticker COP
python manage_decisions.py audit --ticker COP --hours-back 48
```
- Trazabilidad completa de decisiones
- Performance tracking
- Learning loop
- **Full context preservation**

---

## 🔄 Flujo Completo de Datos

```
1. NOTICIAS → Entidades → BD
   ├─ Alpaca News (18 items)
   ├─ Google News (60 items)
   └─ SERPAPI (136 items)

2. ENTIDADES → Ticker Analysis → Recommendations
   ├─ USO: 14 news, 38 entities → CAUTIOUS
   ├─ COP: 7 news, 21 entities → BULLISH ✅
   └─ BNO: 14 news, 38 entities → CAUTIOUS

3. RECOMMENDATIONS → Decision Agent → Action
   ├─ COP (BULLISH, 0.91 conf, 62% pos)
   │  └─ Agente: FOLLOW → BUY $5055 @ $98
   │     ├─ Stop: $93.10 (-5%)
   │     └─ Target: $107.80 (+10%)
   └─ Resto: CAUTIOUS → WATCH

4. ACTION → Database → Performance Tracking
   └─ Decision ID 2: COP BOUGHT @ $98
      └─ Outcome: TBD
```

---

## 🤖 Decision Agent - Detalles

### **Reglas de Decisión**

#### **BULLISH → BUY (FOLLOW)**
```
SI:
  - Confidence >= 0.80
  - Positive Ratio >= 60%
  - Negative Ratio <= 30%

ENTONCES:
  - Action: BOUGHT
  - Position Size: $5000 base × confidence_multiplier
  - Stop Loss: -5%
  - Take Profit: +10%
```

#### **CAUTIOUS → WATCH (FOLLOW)**
```
SI:
  - Recommendation = CAUTIOUS
  - Mixed signals (40-60% pos/neg)

ENTONCES:
  - Action: NONE (monitor)
  - Status: WATCH
```

#### **BULLISH pero débil → IGNORE**
```
SI:
  - Confidence < 0.80
  - Positive Ratio < 60%
  - Negative Ratio > 30%

ENTONCES:
  - Action: NONE
  - Reason: "Criteria not met"
```

### **Position Sizing**
```
Base Size: $5000
Confidence Multiplier: confidence / 0.90

Example COP:
- Confidence: 0.91
- Multiplier: 0.91 / 0.90 = 1.01
- Position Size: $5000 × 1.01 = $5055.56
- Shares: 5055.56 / $98 = 51.5 shares
```

---

## 🎛️ Control ON/OFF

### **Modo MANUAL (Default)**
```bash
python test_decision_agent.py --watchlist-id 3
```
- Agente SUGIERE acciones
- Usuario DEBE decidir manualmente
- No registra en BD automáticamente

### **Modo AUTOPILOT**
```bash
AUTOPILOT_MODE=on python test_decision_agent.py --watchlist-id 3
```
- Agente DECIDE automáticamente
- Registra decisiones en BD
- Calcula position sizing
- Determina stop loss / take profit
- **Sistema 100% autónomo** ✈️

### **Configuración de Parámetros**

```python
# trading_mvp/agents/decision_agent.py

DecisionConfig(
    # Mode
    autopilot_enabled=True,  # Set via AUTOPILOT_MODE=on

    # Risk parameters
    max_position_size=10000.0,      # Max $ per position
    default_stop_loss_pct=0.05,     # 5% stop loss
    default_take_profit_pct=0.10,   # 10% take profit

    # Decision rules
    min_confidence_for_buy=0.80,
    min_positive_ratio_for_bullish=0.60,
    max_negative_ratio_for_bullish=0.30,

    # Position sizing
    base_position_size=5000.0,

    # Safety
    dry_run=True  # False = real money
)
```

---

## 📊 Ejemplo Real: COP

### **Input: Mesa de Inversiones**
```
Ticker: COP
Recommendation: BULLISH
Confidence: 0.91
Positive Ratio: 62.0%
Negative Ratio: 29.0%
News: 7 items
Entities: 21 found
Top Risks: Crude Oil (negative)
Top Opportunities: Ceasefire (positive)
```

### **Procesamiento: Decision Agent**
```
🤔 Analyzing COP: BULLISH
   Confidence: 0.91 | Positive: 62.0% | Negative: 29.0%

✅ DECISION: FOLLOWED - BUY COP
   Size: $5055.56 @ $98.00
   Stop: $93.10 | Target: $107.80

✅ Recorded decision 2 for COP: FOLLOWED
```

### **Output: Base de Datos**
```
investment_decisions:
  id: 2
  ticker: COP
  recommendation: BULLISH
  desk_action: BUY
  decision: FOLLOWED
  action_taken: BOUGHT
  position_size: 5055.56
  entry_price: $98.00
  status: PENDING
  decision_timestamp: 2026-04-08 19:12:35
```

---

## 📈 Tracking Completo

### **Historial de Decisiones**
```bash
$ python manage_decisions.py history --ticker COP

🚀 COP - BULLISH
   Decision: ✅ FOLLOWED | Action: BOUGHT
   Status: ⏳ PENDING
   Entry: $98.00
   Size: $5055.56
   Date: 2026-04-08 19:12:35
```

### **Audit Trail Completo**
```bash
$ python manage_decisions.py audit --ticker COP --hours-back 48

📅 Analysis: 2026-04-08T14:12:35
   Desk Sentiment: CAUTIOUSLY BEARISH
   Ticker Recommendation: BULLISH
   Confidence: 0.91
   News Analyzed: 7
   Entities Found: 21

   ⚠️ Top Risks:
      • Crude Oil (negative)
      • Crude oil (negative)

   🚀 Top Opportunities:
      • Ceasefire (positive)
      • Real Estate (positive)

   📝 Decision ID: 2
   Decision: FOLLOWED
   Action: BOUGHT
   Entry Price: $98.00
   Position Size: $5055.56
   Stop: $93.10
   Target: $107.80
   Status: PENDING
```

---

## 🔥 Capabilidades del Sistema

### **Full Automation**
- ✅ Recolecta noticias automáticamente (6h)
- ✅ Analiza tickers automáticamente
- ✅ Genera recomendaciones automáticamente
- ✅ **Toma decisiones automáticamente** (AUTOPILOT)
- ✅ Registra todo en BD automáticamente
- ✅ Calcula position sizing automáticamente
- ✅ Determina stop loss / TP automáticamente

### **Trazabilidad Completa**
- ✅ Cada análisis tiene timestamp
- ✅ Cada decisión tiene rationale
- ✅ Cada decisión linka a análisis original
- ✅ Cada decisión linka a news/entidades específicas
- ✅ Performance tracking automático
- ✅ Learning loop (ratings, lessons learned)

### **Flexibilidad**
- ✅ ON/OFF switch (AUTOPILOT_MODE)
- ✅ Configuración de reglas
- ✅ Risk parameters ajustables
- ✅ Position sizing personalizable
- ✅ Diversificación configurable

---

## 🚀 Producción

### **Setup de Cron Jobs**
```bash
# Cada 6 horas: recolectar noticias + analizar + decidir
0 */6 * * * cd /path/to/trading-mvp && \
  AUTOPILOT_MODE=on \
  .venv/bin/python test_decision_agent.py --watchlist-id 3
```

### **Monitoreo**
```bash
# Ver decisiones recientes
python manage_decisions.py history

# Ver performance
python manage_decisions.py performance

# Ver pending positions
python manage_decisions.py list-pending
```

---

## ⚠️ Safety Features

### **Dry Run Mode**
```python
dry_run=True  # No ejecuta trades reales (testing)
```

### **Risk Limits**
```python
max_position_size=10000.0
max_portfolio_risk=0.02  # 2% max risk
default_stop_loss_pct=0.05  # Auto stop at -5%
```

### **Decision Logging**
- TODAS las decisiones se registran
- Full context preservado
- Audit trail inmutable
- Performance tracking automático

---

## ✅ El Sistema está LISTO

**Capacidades implementadas:**

1. ✅ **Pipeline de noticias automático** (3 fuentes)
2. ✅ **Extracción de entidades con IA**
3. ✅ **Mesa de inversiones completa**
4. ✅ **Agente de decisiones autónomo**
5. ✅ **ON/OFF switch** (AUTOPILOT_MODE)
6. ✅ **Trazabilidad completa** (4 tablas BD)
7. ✅ **Performance tracking**
8. ✅ **Risk management**
9. ✅ **Position sizing automático**
10. ✅ **Audit trail inmutable**

**🚀 Sistema puede operar 100% autónomamente en modo AUTOPILOT**

Para activar modo autónomo:
```bash
export AUTOPILOT_MODE=on
python test_decision_agent.py --watchlist-id 3
```
