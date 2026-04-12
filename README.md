# Trading MVP: Institutional-Grade Multi-Agent Investment Desk

**Sistema de trading autónomo con 7 roles especializados, motor cuantitativo de alta precisión y control humano determinista.**

## 🎯 Visión

Mesa de inversión impulsada por IA que emula un entorno institucional. El sistema gestiona una cartera completa bajo principios de **"Portfolio-First Analysis"**, integrando narrativa macro, sentimiento de noticias y un **Rigor Cuantitativo Híbrido**.

---

## 🏗️ Arquitectura "By the Book" (Claude Code Pattern)

El proyecto sigue el estándar de diseño de Claude Code para workflows multi-agente, asegurando determinismo y escalabilidad:

1.  **Capa de Intención (`.md`)**: Cada agente tiene una "Constitución" en Markdown que define su rol, mandatos y flujo de trabajo.
2.  **Capa de Ejecución (`.py`)**: Implementación determinista via CLI que garantiza entradas y salidas estructuradas (Structured I/O).
3.  **Patrón Handover**: Desacoplamiento total entre agentes; la comunicación se realiza mediante eventos y disparadores de shell.

### Estructura de Módulos
```
trading_mvp/                     # 📦 Core Infrastructure
├── core/                      # Portofolio Logic & DB (Supabase/SQLite)
├── analysis/                  # Quant Engine & Sentiment Analysis
├── news/                      # News Aggregators (Alpaca, GDELT)
├── execution/                 # Alpaca Trading API Integration
└── reporting/                 # Automated Trade Cards & Audit Trails
```

---

## 🏛️ Arquitectura de la Mesa de Inversiones (v2.0)

El sistema opera bajo un **Modelo de Decisión Ponderado 60/40**, donde la disciplina matemática de los datos cuantitativos guía la estrategia, y la capacidad contextual de la IA (LLM) valida la tesis.

### 1. Motor Quant: El Núcleo del 60%
El algoritmo procesa **11 indicadores clave** divididos en 5 dimensiones críticas para filtrar el ruido y detectar valor real:

*   **I. Estructura (Tendencia):** SMA 200 (Dirección LP), SMA 50 (Salud MP), y Distancia al Precio % (Sobre-extensión).
*   **II. Impulso (Momentum):** RSI 14 (Agotamiento) y MACD (Convergencia/Divergencia de ciclos).
*   **III. Convicción (Liquidez):** RVOL (Participación Institucional) e Indicador OBV (On-Balance Volume).
*   **IV. Volatilidad (Riesgo):** ATR 14 (Rango Real) y Desviación Estándar 20d (Pánico/Euforia).
*   **V. Sensibilidad (Contexto):** Beta vs SPY (Exposición al Mercado) y Correlación Rodante (Alineación Sistémica).

### 2. Motor LLM: El Cerebro Contextual del 40%
La IA procesa el lenguaje natural de noticias y reportes para aportar el "por qué" detrás de los números:

*   **Análisis GeoMacro:** Impacto de conflictos (ej. Irán-EE.UU.), tasas de la FED y datos de inflación (CPI).
*   **Sentimiento de Entidades:** Ratio de impacto positivo/negativo de actores clave en el mercado.
*   **Análisis Dialéctico:** Contraste de tesis alcistas y bajistas basadas en la narrativa macro.

---

## 📈 Quantitative Intelligence Engine (60/40 Weighted Model)

El sistema ya no es solo intuitivo; integra un motor estadístico que domina el **60% de la decisión final**, asegurando que ninguna narrativa de noticias ignore la realidad del precio:

### 1. Filtros de Estructura y Momentum
*   **Alineación de SMAs**: El sistema requiere confirmación de tendencia primaria y secundaria. 
*   **MACD & RSI Confirmation**: Se buscan zonas de aceleración de tendencia sin entrar en niveles de agotamiento (RSI > 75).

### 2. Convicción y Volumen Relativo (RVOL)
*   **Institutional Confirmation**: El sistema ignora noticias si el volumen relativo es bajo (< 0.8), identificando movimientos de minoristas o ruido. Solo actúa ante convicción real (> 1.2 RVOL).

### 3. Volatilidad Adaptativa (ATR)
*   **Stop Loss Dinámico (2x ATR)**: El sistema calcula la volatilidad diaria (Average True Range). El Stop Loss se coloca a 2 ATRs del precio de entrada, adaptándose al "ruido" específico de cada activo.

### 4. Sensibilidad y Correlación (Beta/Corr)
*   **Market-Neutral Bias**: El sistema mide la correlación rodante de 20 días con el SPY. Se priorizan activos con "vida propia" o baja correlación para generar Alpha real.


---

## 🛡️ Human-in-the-Loop Guardrails (Control Humano)

Configura estos límites innegociables en tu `.env` para gobernar a la IA:

*   **`MIN_CONFIDENCE_SCORE`**: Umbral de certeza mínima (ej. 0.80).
*   **`MAX_POSITION_SIZE_PCT`**: Máximo capital por activo (ej. 10% de la cuenta).
*   **`MAX_PORTFOLIO_EXPOSURE_PCT`**: Límite de inversión total (ej. 85%).
*   **`MIN_CASH_RESERVE_PCT`**: Efectivo intocable para emergencias.
*   **`DAILY_DRAWDOWN_LIMIT_PCT`**: **Panic Button** que apaga el sistema ante pérdidas rápidas.

---

## 📊 Flujo de Trabajo Integral (The Desk Loop)

El sistema opera en un ciclo dialéctico y determinista de 7 pasos:

1.  **Sync Context**: Lectura de cartera real de Alpaca.
2.  **Evaluate Health**: Análisis de posiciones actuales. Si un activo se vuelve **BEARISH**, se liquida automáticamente (**Sell-Off logic**).
3.  **Discovery**: Explorer identifica nuevas empresas basadas en la temática activa.
4.  **Quant Snapshot**: Ingesta de datos históricos y cálculo de RSI, ATR y SMAs.
5.  **Dialectical Research**: Bull y Bear Researchers debaten la tesis contrastando noticias con la evidencia Quant.
6.  **Deterministic Decision**: El `DecisionAgent` cruza la IA con los Guardrails Humanos y Sensores Técnicos.
7.  **Autonomous Execution**: Si `AUTOPILOT_MODE=on`, ejecución de órdenes y generación de **Trade Cards**.

---

## 🛠️ Comandos de Ejecución

```bash
# Ejecutar la Mesa de Inversiones Integral (Flujo Completo)
export PYTHONPATH=$PYTHONPATH:.
./venv/bin/python3 scripts/run_investment_desk.py --watchlist-id 2 --hours-back 168

# Uso Individual de Agentes (Patrón CLI)
python .claude/subagents/bull_researcher/agent.py --ticker "AAPL"
python .claude/subagents/risk_manager/agent.py --ticker "AAPL" --position-size 1000
```

---

**Nota**: Este es un proyecto de investigación y desarrollo. No constituye asesoramiento financiero. El uso de autopilot en cuentas reales conlleva riesgos significativos.

**Versión**: 0.3.5 (Quant-Native Edition)
**Licencia**: MIT
