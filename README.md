# Plataforma de Inteligencia Ciudadana (PIC) / Trading MVP: Mesa de Inversiones Autónoma de Grado Institucional

**Sistema de trading autónomo con 7 roles especializados, motor cuantitativo de alta precisión y control humano determinista.**

## 🎯 Introducción y Visión del Proyecto

Este proyecto nació como un MVP de trading, pero ha evolucionado hacia una **Arquitectura de Grado Institucional**. Es una mesa de inversión impulsada por IA que emula un entorno de un *Hedge Fund* Tier 1 (como Citadel o Millennium). El sistema gestiona una cartera completa bajo principios de **"Portfolio-First Analysis"**, integrando la narrativa macroeconómica global, el análisis de sentimiento de noticias polarizadas y un **Rigor Cuantitativo Híbrido** basado en datos históricos reales.

El objetivo principal es lograr que un enjambre de agentes LLM (Flash 2.0/Claude) opere de manera determinista, eliminando las "alucinaciones" a través de *Sanity Checks* rigurosos y una gestión del riesgo dinámica basada en la Volatilidad Histórica (ATR).

---

## ⏱️ Ritmo de Ejecución Institucional (El "Sweet Spot")

Para maximizar el Alpha (retorno) sin generar ruido estadístico ni sobre-operar (churning), el sistema está diseñado para ejecutarse **exactamente 2 veces al día**, alineado con la microestructura del mercado americano. 

Se desaconseja ejecutar el sistema cada 4 o 6 horas, ya que el Motor Quant (que pesa el 60% de la decisión) se basa en velas diarias y la volatilidad a ese marco temporal. Una ejecución excesiva haría que el NLP reaccione histéricamente al ruido intradía.

### 🌅 1. La Ingesta Pre-Market (08:30 AM EST | 12:30 UTC | **07:30 AM America/Lima** 🇵🇪)
*   **Propósito:** Digerir el flujo de noticias de la sesión asiática, la apertura europea y los reportes de ganancias nocturnos.
*   **Lógica Quant:** Utiliza el cierre consolidado de la vela diaria del día anterior. Los indicadores (RSI, MACD, Beta) están inmaculados y sin ruido intradía.
*   **Acción del Agente:** Detectar oportunidades de "Gap up/down" (saltos de precio) provocados por noticias nocturnas y tomar posiciones justo en la apertura (09:30 AM).

### 🌇 2. La Consolidación del Cierre (15:00 PM EST | 19:00 UTC | **14:00 PM America/Lima** 🇵🇪 - Power Hour)
*   **Propósito:** Capturar el verdadero sentimiento institucional ("Smart Money"), que suele operar en la última hora del día.
*   **Lógica Quant:** La vela diaria actual está al 90% de su formación. El sistema sabe con alta probabilidad si el activo cerrará respetando su estructura técnica (ej. sobre la SMA 200) y si el volumen (RVOL) es legítimo.
*   **Acción del Agente:** Liquidar posiciones que perdieron su estructura técnica o comprar activos que confirmaron una ruptura técnica real respaldada por el flujo de noticias del día.

### ⚙️ Implementación en Coolify CI/CD

**🚀 Dos modos de despliegue disponibles:**

**Modo 1: Coolify CI/CD (Recomendado - Deploy Continuo)**
```bash
# Ver documentación completa
cat coolify/CI-CD.md

# Características:
# - Deploy automático desde GitHub
# - Soporte Nixpacks (build auto) o Dockerfile
# - Cron jobs nativos de Coolify
# - Health checks y restart automático
# - Rollback con 1 click
```

**Modo 2: VPS con Cron Jobs (Tradicional)**
```bash
cd coolify
chmod +x setup_crons.sh
./setup_crons.sh
```

Cron Jobs:
```bash
# Pre-Market (07:30 AM Lima | 12:30 UTC)
30 12 * * 1-5 cd /path/to/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones

# Power Hour (14:00 PM Lima | 19:00 UTC)
0 19 * * 1-5 cd /path/to/trading-mvp && AUTOPILOT_MODE=on .venv/bin/python ejecutar_mesa_inversiones
```

### 📊 Tabla Resumen de Horarios

| Ejecución | EST | UTC | **America/Lima** 🇵🇪 | Propósito |
|-----------|-----|-----|---------------------|-----------|
| **Pre-Market** | 08:30 AM | 12:30 | **07:30 AM** | Gaps + Apertura |
| **Power Hour** | 15:00 PM (3:00 PM) | 19:00 | **14:00 PM (2:00 PM)** | Cierre + Smart Money |

**🌎 Nota sobre Zonas Horarias:**
- **America/Lima**: UTC-5 (sin horario de verano)
- **EST (EE.UU.)**: UTC-5 (invierno) / UTC-4 (verano)
- Lima es siempre 1 hora atrás de Nueva York (en verano) o misma hora (en invierno)

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

*   **Visión 360 Institucional:** Pipeline de noticias categorizadas en 10 dimensiones estructurales (Macro, Geopolítica, Tech, Energía, Crypto, etc.), limitadas a 13 noticias por categoría para un muestreo profundo sin dilución de contexto del LLM.
*   **Deduplicación & Retención:** Ingesta centralizada en Supabase con resolución nativa de duplicados y un Job (pg_cron) de TTL estricto a 90 días, garantizando que el modelo analice solo información viva y relevante (no "priced-in").
*   **Sentimiento de Entidades y Varianza:** Ratio de impacto positivo/negativo y control estricto de volatilidad mediática (filtrando falsas señales "neutrales" en noticias extremadamente polarizadas).

---

## 📈 Quantitative Intelligence Engine (60/40 Weighted Model)

El sistema ya no es solo intuitivo; integra un motor estadístico que domina el **60% de la decisión final**, asegurando que ninguna narrativa de noticias ignore la realidad del precio:

### 1. Filtros de Estructura y Momentum
*   **Alineación de SMAs**: El sistema requiere confirmación de tendencia primaria y secundaria. 
*   **MACD & RSI Confirmation**: Se buscan zonas de aceleración de tendencia sin entrar en niveles de agotamiento (RSI > 75).

### 2. Convicción y Volumen Relativo (RVOL)
*   **Institutional Confirmation**: El sistema ignora noticias si el volumen relativo es bajo (< 0.8), identificando movimientos de minoristas o ruido. Solo actúa ante convicción real (> 1.2 RVOL).

### 3. Gestión del Riesgo Pre-emptiva (ATR Dinámico)
*   **Control Determinista del PnL**: Cálculo preciso de rentabilidades considerando el precio promedio real de entrada (`avg_entry_price`) para activos vivos que hayan promediado ("scale-in").
*   **Stop Loss (1.5x) y Take Profit (3x)**: El sistema evalúa estos umbrales como **PASO 0 absoluto**. Si se tocan, el sistema detiene el análisis cualitativo y ejecuta mecánicamente el cierre de posición. Cero fallbacks, cero negociación.

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
