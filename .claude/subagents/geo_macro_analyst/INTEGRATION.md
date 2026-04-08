# GeoMacro Analyst - Guía de Integración

## 🎯 **Propósito**

El GeoMacro Analyst es el agente de **INTELIGENCIA GLOBAL** que monitorea y analiza factores geopolíticos, económicos y macroeconómicos que afectan los mercados financieros. **Todos los demás agentes DEBEN consultar sus insights** para enriquecer sus análisis.

## 📅 **Schedule de Ejecución**

### Automatizado (Cron)
```bash
# Morning Briefing (Pre-Market: 8:00 AM ET)
0 8 * * 1-5 cd /path/to/trading-mvp && .venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --session morning

# Afternoon Update (Post-Market: 2:00 PM ET)
0 14 * * 1-5 cd /path/to/trading-mvp && .venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --session afternoon
```

### Manual
```bash
# Ejecutar sesión ad-hoc
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --session ad-hoc

# Ver resumen de insights
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --summary

# Ver solo eventos críticos
.venv/bin/python .claude/subagents/geo_macro_analyst/agent.py --critical
```

## 🔌 **Integración con Otros Agentes**

### 1. **Explorer Agent**

Cuando descubre oportunidades, el Explorer debe considerar factores macro:

```python
from trading_mvp.core.macro_context import get_macro_context_for_explorer

# En discover_tickers()
def discover_tickers(prompt: str) -> List[str]:
    # ... código existente ...

    # AGREGAR: Obtener contexto macro
    macro_context = get_macro_context_for_explorer(theme=prompt, hours=48)

    # MODIFICAR: Prompt para incluir contexto macro
    gen_prompt = f"""
    You are a financial research scout. Based on the following thematic prompt,
    identify a cluster of at least 5-10 relevant stock ticker symbols (US exchanges).

    Theme: {prompt}

    {macro_context}  # <-- AGREGAR ESTO

    IMPORTANT: Consider the macro context above when selecting tickers.
    Avoid sectors/regions with critical geopolitical risks.
    Prioritize areas positively impacted by recent macro events.

    Provide your response in JSON format with the following keys:
    - tickers: a list of string ticker symbols
    - reasoning: a brief explanation of why these tickers were chosen
    - macro_considerations: how macro context influenced selection
    """
```

### 2. **Hypothesis Generator**

Debe incorporar factores macro en la thesis de inversión:

```python
from trading_mvp.core.macro_context import get_macro_context_for_hypothesis

# En generate_hypothesis()
def generate_hypothesis(tickers: List[str]) -> Dict:
    # ... código existente ...

    # AGREGAR: Obtener contexto macro para los tickers
    macro_context = get_macro_context_for_hypothesis(tickers, hours=72)

    # MODIFICAR: Prompt para incluir contexto macro
    prompt = f"""
    You are an investment research analyst. Analyze the following ticker symbols
    and generate a comprehensive investment hypothesis.

    Tickers: {', '.join(tickers)}

    {macro_context}  # <-- AGREGAR ESTO

    Your analysis should include:
    1. Investment thesis (bullish/bearish/neutral)
    2. Key fundamental drivers (including macro factors)
    3. Major catalysts (both positive and negative)
    4. Macro headwinds or tailwinds from recent events
    5. Sector context and competitive positioning
    6. Timeline expectations
    7. Confidence level

    IMPORTANT: Explicitly address how macro events affect your thesis.
    """
```

### 3. **Bull/Bear Researchers**

Deben contextualizar sus casos con factores macro:

```python
from trading_mvp.core.macro_context import get_macro_context_for_analysis

# En analyze_bull_case()
def analyze_bull_case(ticker: str) -> Dict:
    # AGREGAR: Obtener contexto macro
    context = get_macro_context_for_analysis(ticker=ticker, hours=72)

    # MODIFICAR: Prompt
    prompt = f"""
    You are a bullish investment analyst. Analyze {ticker} and present the
    POSITIVE investment case.

    RELEVANT MACRO CONTEXT:
    {format_macro_context_for_prompt(context)}  # <-- AGREGAR ESTO

    Your analysis should include:
    1. 3-5 key bullish arguments (including macro tailwinds)
    2. Growth catalysts (product, market, AND macro)
    3. Price targets with reasoning
    4. How recent macro events support the bull case

    IMPORTANT: Leverage positive macro developments in your arguments.
    """
```

### 4. **Risk Manager**

Debe evaluar riesgos macro sistémicos:

```python
from trading_mvp.core.macro_context import get_macro_context_for_risk

# En assess_risk()
def assess_risk(ticker: str, position_size: float) -> Dict:
    # AGREGAR: Obtener contexto macro completo
    macro_context = get_macro_context_for_risk(ticker, hours=72)

    # CONTAR: Alertas críticas
    critical_count = len(macro_context['critical_alerts'])

    # MODIFICAR: Evaluar riesgo adicional
    base_risk_score = ... # riesgo normal

    # AGREGAR: Ajuste por riesgo macro
    if critical_count > 0:
        risk_adjustment = f"+{critical_count} risk levels due to {critical_count} critical macro alerts"
        # Aumentar stop loss, reducir position size, etc.

    prompt = f"""
    Assess risk for {ticker} with ${position_size} position.

    CRITICAL MACRO RISK FACTORS:
    {format_macro_context_for_prompt(macro_context)}

    Your risk assessment should include:
    1. Overall risk score (considering macro factors)
    2. Position size recommendation
    3. Stop loss levels
    4. Take profit targets
    5. Specific macro risks to monitor

    IMPORTANT: Factor in critical macro events in your risk assessment.
    """
```

## 📊 **Ejemplos de Uso**

### Ejemplo 1: Verificar Alertas Críticas Antes de Trading

```python
from trading_mvp.core.macro_context import check_for_critical_events

# Antes de ejecutar cualquier trade
if check_for_critical_events(hours=24):
    print("⚠️ Hay eventos críticos - considerar reducir tamaño de posición")
    # No ejecutar trades agresivos
else:
    print("✅ Sin eventos críticos - proceder normal")
```

### Ejemplo 2: Análisis Sectorial con Contexto Macro

```python
from trading_mvp.core.macro_context import get_macro_context_for_analysis

# Análisis de sector energético
energy_context = get_macro_context_for_analysis(
    sector="energy",
    hours=48
)

print(f"Insights energéticos: {len(energy_context['insights'])}")
print(f"Alertas críticas: {len(energy_context['critical_alerts'])}")

# Usar en análisis
for insight in energy_context['insights']:
    if insight['event_type'] == 'commodity':
        print(f"Commodity price impact: {insight['title']}")
```

### Ejemplo 3: Monitoreo Geopolítico por Región

```python
from trading_mvp.core.macro_context import get_insights_for_region

# Monitorear conflicto en Medio Oriente
middle_east_insights = get_insights_for_region("Middle East", hours=24)

for insight in middle_east_insights:
    if insight['importance'] in ['critical', 'high']:
        print(f"ALERTA: {insight['title']}")
        # Ajustar estrategia de trading en energía, shipping, etc.
```

## 🎯 **Mejores Prácticas**

1. **SIEMPRE consultar contexto macro** antes de generar recomendaciones
2. **Ajustar thesis** basado en eventos macro recientes
3. **Incrementar conservadurismo** cuando hay alertas críticas
4. **Documentar impacto macro** en todas las recomendaciones
5. **Actualizarse**: Ejecutar GeoMacro 2x al día mínimo

## 📈 **Impacto en Calidad de Señales**

Con GeoMacro Analyst integrado:
- ✅ **Mejor timing**: Evitar entrar antes de eventos negativos
- ✅ **Mayor precisión**: Contexto macro en cada análisis
- ✅ **Riesgo reducido**: Alertas tempranas de crisis sistémicas
- ✅ **Mejores returns**: Aprovechar catalizadores macro
- ✅ **Protección**: Reducir exposición en momentos de riesgo

## 🔄 **Flujo Completo Integrado**

```
1. GeoMacro Analyst (8:00 AM)
   ↓ Genera insights del contexto global

2. Explorer Agent
   ↓ Considera contexto al descubrir oportunidades

3. Hypothesis Generator
   ↓ Incorpora factores macro en thesis

4. Macro Analyst (Sentiment)
   ↓ Analiza noticias con contexto macro

5. Bull/Bear Researchers
   ↓ Contextualizan casos con factores macro

6. Risk Manager
   ↓ Evalúa riesgos macro sistémicos

7. Orchestrator
   ↓ Sintetiza TODO con contexto macro completo

8. Trade Final
   ✓ Recomendación enriquecida con contexto global
```

## 🚀 **Próximos Pasos**

1. ✅ GeoMacro Analyst creado y probado
2. ⏳ Integrar en Explorer Agent
3. ⏳ Integrar en Hypothesis Generator
4. ⏳ Integrar en Bull/Bear Researchers
5. ⏳ Integrar en Risk Manager
6. ⏳ Configurar cron jobs para ejecución automática
7. ⏳ Crear dashboard de monitoreo macro

## 📞 **Soporte**

Para preguntas o problemas con la integración:
- Ver `geo_macro_analyst.md` para documentación completa
- Ver `trading_mvp/core/macro_context.py` para API reference
- Ejecutar con `--summary` para ver insights actuales
