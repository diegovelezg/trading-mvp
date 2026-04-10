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

## 📈 Quantitative Intelligence Engine

El sistema no opera solo por intuición narrativa. Integra un motor estadístico que valida cada tesis de inversión mediante **sensores técnicos en tiempo real**:

### 1. Filtros de Momentum y Tendencia
*   **SMA 50 vs SMA 200 (Golden/Death Cross)**: El sistema identifica la tendencia primaria. Si el precio está bajo la media de 200 días, la confianza del análisis alcista se penaliza automáticamente un 20%.
*   **Momentum de Corto Plazo**: Cruce de SMA 50 para detectar aceleración del precio.

### 2. Osciladores de Fuerza Relativa (RSI)
*   **Anti-Euphoria Filter**: Si el RSI(14) es **> 75**, el `DecisionAgent` bloquea cualquier orden de compra, independientemente de lo buenas que sean las noticias (evita el FOMO y compras en techos).
*   **Oversold Detection**: Identifica activos castigados con RSI **< 30** como oportunidades de alta probabilidad.

### 3. Volatilidad y Gestión de Riesgo (ATR)
*   **Stop Loss Dinámico (2x ATR)**: Olvida los porcentajes fijos. El sistema calcula la volatilidad diaria (Average True Range). El Stop Loss se coloca a 2 ATRs del precio de entrada, adaptándose al "ruido" específico de cada activo.
*   **Take Profit Inteligente**: Ratio de Riesgo/Beneficio de **1:2** calculado sobre la volatilidad real.

### 4. Correlación de Mercado (Beta)
*   **Beta vs SPY**: Mide la sensibilidad del activo respecto al mercado general. Si el mercado es bajista, el sistema reduce el tamaño de posición en activos de alta Beta (> 1.2).

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
