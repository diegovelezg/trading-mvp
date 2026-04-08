# Trading MVP: Multi-Agent Investment Desk

**Mesa de Inversión completa con 7 roles especializados coordinados**

## 🎯 Visión

Sistema multi-agente que emula una mesa de inversión institucional, donde agentes especializados (Explorer, Analysts, Researchers, Risk Manager, Executioner) colaboran para analizar y ejecutar decisiones de inversión.

## 🏗️ Arquitectura

```
trading_mvp/                     # 📦 Código compartido
├── core/                      # Base de datos, configuración
├── analysis/                  # Análisis de sentimiento
├── news/                      # Fuentes de noticias (Alpaca)
├── execution/                 # Ejecución de órdenes
└── reporting/                 # Reportes y Trade Cards

.claude/subagents/             # 🤖 Subagentes especializados
├── explorer/                  # 🔍 Descubre empresas por temática
├── macro_analyst/             # 📊 Analiza noticias y sentimiento
├── hypothesis_generator/      # 🧠 Genera hipótesis de inversión
├── bull_researcher/           # 📈 Argumentos a favor
├── bear_researcher/           # 📉 Argumentos en contra
├── risk_manager/              # ⚡ Gestión de riesgos
├── executioner/               # 💼 Ejecuta órdenes
└── orchestrator/              # 🎯 Coordina todo el flujo
```

## 🚀 Inicio Rápido

### Instalación
```bash
# Clonar y configurar
git clone https://github.com/diegovelezg/trading-mvp
cd trading-mvp

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Instalar
pip install -e ".[dev]"

# Configurar API keys
cp .env.example .env
# Editar .env con tus credenciales de Alpaca y Gemini

# Inicializar base de datos
python -m trading_mvp.core.db_manager
```

### Uso de Subagentes

```bash
# 1. Explorer: Descubrir empresas por temática
python .claude/subagents/explorer/agent.py "small caps in energy sector"

# 2. Hypothesis Generator: Analizar fundamentales
python .claude/subagents/hypothesis_generator/agent.py --tickers "AAPL,TSLA,MSFT"

# 3. Macro Analyst: Analizar noticias y sentimiento
python .claude/subagents/macro_analyst/agent.py --symbols "AAPL,TSLA"

# 4. Bull Researcher: Análisis alcista
python .claude/subagents/bull_researcher/agent.py --ticker "AAPL"

# 5. Bear Researcher: Análisis bajista
python .claude/subagents/bear_researcher/agent.py --ticker "AAPL"

# 6. Risk Manager: Evaluar riesgo
python .claude/subagents/risk_manager/agent.py --ticker "AAPL" --position-size 1000

# 7. Executioner: Ejecutar órdenes
python .claude/subagents/executioner/agent.py --symbol "AAPL" --action "BUY" --qty 10
python .claude/subagents/executioner/agent.py --positions  # Ver posiciones

# 8. Orchestrator: ¡FLUJO COMPLETO! (Recomendado)
python .claude/subagents/orchestrator/agent.py "AI infrastructure" --capital 5000
```

### Ver Exploraciones Registradas

```bash
# Ver historial de exploraciones con criterios
python scripts/query_explorations.py --limit 5
```

## 📊 Flujo de Trabajo Completo

1. **Discovery** → Explorer descubre empresas por temática
2. **Hypothesis** → Hypothesis Generator crea hipótesis de inversión
3. **Analysis** → Macro Analyst analiza noticias y sentimiento
4. **Dialectical** → Bull + Bear Researchers debaten pros y contras
5. **Risk** → Risk Manager evalúa riesgos y tamaño de posición
6. **Execution** → Executioner ejecuta órdenes en Alpaca Paper Trading
7. **Reporting** → Se generan Trade Cards y reportes automáticos

## 🔧 Scripts de Utilidad

```bash
# Inicializar base de datos
python -m trading_mvp.core.db_manager

# Ver exploraciones recientes
python scripts/query_explorations.py

# Migrar esquema de BD (cuando hay cambios)
python scripts/migrate_db.py
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest -v

# Con cobertura
pytest --cov=trading_mvp --cov-report=html
```

## 📖 Documentación

- [STRUCTURE.md](STRUCTURE.md) - Estructura detallada del proyecto
- [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) - Estado de implementación
- [docs/conductor/](docs/conductor/) - Documentación técnica completa

## 🎯 Características

✅ **7 roles especializados** + Orchestrator
✅ **Autocontenido**: Cada subagente tiene su config + código
✅ **Registro de criterios**: Explorer guarda criterios de búsqueda
✅ **Trade Cards**: Reportes automáticos con análisis completo
✅ **Alpaca Paper Trading**: Integración con broker real
✅ **Base de datos SQLite**: Auditoría completa de decisiones

## 📊 Estado del Proyecto

- **Versión**: 0.2.0
- **Estado**: Alpha (Funcional pero en desarrollo)
- **Tests**: En progreso
- **Documentación**: Completa

## 🚧 Próximos Pasos

1. Completar suite de tests
2. Orquestación nativa Claude Code (sin scripts manuales)
3. Más fuentes de datos (GDELT, SEC filings)
4. Optimizar prompts de Gemini para mejor análisis

---

**Nota**: Este es un MVP para investigación educativa. No es apto para trading real sin gestión de riesgos apropiada.

**Licencia**: MIT - Ver archivo [LICENSE](LICENSE)
