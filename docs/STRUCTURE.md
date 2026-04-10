# 🏗️ Estructura del Proyecto - Trading MVP (Quant-Mental Edition)

## 🎯 Filosofía de Diseño: "Quant-Mental"

**Síntesis de análisis Cualitativo (LLM News) y Cuantitativo (Python Metrics) bajo un mando estratégico centralizado (CIO).**

```
trading_mvp/          = Código compartido (LIBRERÍA)
.claude/subagents/    = Subagentes especializados (ROLES)
```

## 📁 Estructura Completa

```
trading_mvp/                         # 📦 CÓDIGO COMPARTIDO
├── core/                            # Utilidades base y Guardrails
│   ├── db_manager.py               # Base de datos SQLite
│   ├── db_watchlist.py             # Gestión de listas de seguimiento
│   └── portfolio_logic.py          # 🛡️ Guardrails Deterministas (Python)
│
├── analysis/                        # Motores Analíticos
│   ├── gemini_sentiment.py         # Análisis de sentimiento
│   └── quant_stats.py              # 📊 Métricas Cuantitativas (SMA, RSI, Beta, ATR)
│
├── news/                            # Fuentes de datos
│   └── alpaca_news.py              # Integración Alpaca News
│
├── execution/                       # Ejecución de órdenes
│   └── alpaca_orders.py            # Órdenes Alpaca Paper Trading
│
└── reporting/                       # Reportes y Visualización
    ├── trade_cards.py              # Trade Cards
    └── performance.py              # Reportes de performance

.claude/subagents/                  # 🤖 SUBAGENTES ESPECIALIZADOS
├── explorer/                        # 🔍 Scout: Descubre empresas
├── macro_analyst/                   # 📊 Analyst: Noticias y sentimiento
├── bull_researcher/                 # 📈 Bull: Argumentos a favor
├── bear_researcher/                 # 📉 Bear: Argumentos en contra
├── risk_manager/                    # ⚡ Risk: Gestión de riesgos (ATR-based)
├── cio/                             # 🧠 CIO: DECISIÓN ESTRATÉGICA (GLM-5.1)
├── executioner/                      # 💼 Execute: Ejecuta órdenes
└── orchestrator/                    # 🎯 Orchestrator: Coordina el flujo (Ops)
```

## 🔄 Flujo de Trabajo Quant-Mental

```
ORCHESTRATOR (Project Manager)
    │
    ├─> 1. EXPLORER (Scout)
    │      └─> Descubre candidatos por temática (Batch)
    │
    ├─> 2. DATA ENGINES (Parallel)
    │      ├─> MACRO ANALYST: Sentimiento de noticias
    │      └─> QUANT STATS: RSI, SMA 50/200, Beta, ATR
    │
    ├─> 3. THE DESK (Dialectics)
    │      ├─> BULL/BEAR RESEARCHERS: Argumentos técnicos y narrativos
    │      └─> RISK MANAGER: Perfil de riesgo basado en volatilidad (ATR)
    │
    ├─> 4. CIO (The Strategic Brain - GLM-5.1)
    │      └─> Síntesis: Contrasta Sentimiento vs Realidad Técnica (RSI/Trend)
    │          Priorización: Elige el mejor activo del batch
    │          Sizing: Define inversión óptima basada en convicción
    │
    ├─> 5. PORTFOLIO GUARDRAILS (Compliance)
    │      └─> Valida límites de exposición y cash
    │          Ajusta tamaño si rompe reglas
    │
    └─> 6. EXECUTIONER & REPORTING
           └─> Ejecuta en Alpaca y genera Trade Card con racional del CIO
```

## 🚀 Cómo Usar

### Flujo Completo con CIO
```bash
# Orchestrator coordina todo, el CIO (GLM-5.1) decide
python .claude/subagents/orchestrator/agent.py "AI infrastructure" --capital 5000

# Con ejecución real y validación de guardrails
python .claude/subagents/orchestrator/agent.py "energy transition" --capital 10000 --execute
```

## 📊 Estado de Implementación

### ✅ EVOLUCIÓN QUANT-MENTAL COMPLETADA:
- ✅ **CIO Agent**: Cerebro estratégico integrado con Z.AI (GLM-5.1).
- ✅ **Quant Engine**: Proveedor de métricas SMA, RSI, Beta y ATR integrado.
- ✅ **Portfolio Guardrails**: Lógica determinista de Python para seguridad de capital.
- ✅ **Batch Orchestration**: El sistema analiza múltiples candidatos antes de decidir.
- ✅ **Alpaca Sync**: Integración real con balance de cuenta y posiciones actuales.
