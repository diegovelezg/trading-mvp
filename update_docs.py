import os

# --- Update README.md ---
with open('README.md', 'r') as f:
    readme = f.read()

readme_injection = """### 3. Gestión del Riesgo Pre-emptiva (ATR Dinámico)
*   **Control Determinista del PnL**: Cálculo preciso de rentabilidades considerando el precio promedio real de entrada (`avg_entry_price`) para activos vivos que hayan promediado ("scale-in").
*   **Stop Loss (1.5x) y Take Profit (3x)**: El sistema evalúa estos umbrales como **PASO 0 absoluto**. Si se tocan, el sistema detiene el análisis cualitativo y ejecuta mecánicamente el cierre de posición. Cero fallbacks, cero negociación.

### 4. Gestión Activa de Posiciones (Trimming & Pyramiding)
*   **Pyramiding (Escalar en Ganadores)**: Si una posición existente tiene ganancias (`PnL > 0`), la señal NLP es de alta convicción (`>= 0.85`) y el activo no está sobrecomprado (`RSI < 65`), el sistema ejecuta un `SCALE_IN` para maximizar el Alpha.
*   **Trimming (Recortes Defensivos)**: Si una posición acumula más de un 5% de ganancia pero muestra agotamiento técnico (`RSI > 75` o MACD negativo), el sistema ejecuta un recorte del 25% (`TRIM`) para asegurar caja y deja correr el resto.

### 5. Sensibilidad y Correlación (Beta/Corr)"""

readme = readme.replace(
    "### 3. Gestión del Riesgo Pre-emptiva (ATR Dinámico)\n*   **Control Determinista del PnL**: Cálculo preciso de rentabilidades considerando el precio promedio real de entrada (`avg_entry_price`) para activos vivos que hayan promediado (\"scale-in\").\n*   **Stop Loss (1.5x) y Take Profit (3x)**: El sistema evalúa estos umbrales como **PASO 0 absoluto**. Si se tocan, el sistema detiene el análisis cualitativo y ejecuta mecánicamente el cierre de posición. Cero fallbacks, cero negociación.\n\n### 4. Sensibilidad y Correlación (Beta/Corr)",
    readme_injection
)

with open('README.md', 'w') as f:
    f.write(readme)

# --- Update docs/DECISION_AGENT_SYSTEM.md ---
with open('docs/DECISION_AGENT_SYSTEM.md', 'r') as f:
    das = f.read()

das_injection = """- **Risk Management Estricto & Pre-Emptivo**: 
  - **PASO 0 (Evaluación Mecánica)**: El Stop Loss (1.5x ATR) y el Take Profit (3.0x ATR) se calculan ANTES de cualquier evaluación cualitativa o modelo NLP. Si el precio actual cruza un umbral, se ejecuta mecánicamente el cierre ("Sell-Off").
  - **Gestión Activa de Ganancias (Trimming)**: Si el activo supera el +5% de PnL pero el RSI entra en sobrecompra (>75) o el momentum se vuelve negativo, el sistema ejecuta un `TRIM` del 25% de la posición para asegurar beneficios.
  - **Escalamiento (Pyramiding)**: Si una posición tiene ganancias y la nueva señal es fuerte (Confianza >= 0.85, RSI < 65), el sistema inyecta más capital (`SCALE_IN`) abandonando la antigua regla rígida de "HELD obligatorio".
  - **Cálculo Exacto de PnL con Scale-Ins**: Toda rentabilidad y límite de riesgo se basa matemáticamente en el **`avg_entry_price`** ponderado del bróker. Si existen compras promediadas, el sistema adapta el centro de masa de la operación automáticamente.
  - **No hay fallbacks harcodeados**: Si el ATR no se puede calcular o está ausente, la operación es **RECHAZADA (IGNORED)**."""

das = das.replace(
    "- **Risk Management Estricto & Pre-Emptivo**: \n  - **PASO 0 (Evaluación Mecánica)**: El Stop Loss (1.5x ATR) y el Take Profit (3.0x ATR) se calculan ANTES de cualquier evaluación cualitativa o modelo NLP. Si el precio actual cruza un umbral, se ejecuta mecánicamente el cierre (\"Sell-Off\").\n  - **Cálculo Exacto de PnL con Scale-Ins**: Toda rentabilidad y límite de riesgo se basa matemáticamente en el **`avg_entry_price`** ponderado del bróker. Si existen compras promediadas, el sistema adapta el centro de masa de la operación automáticamente.\n  - **No hay fallbacks harcodeados**: Si el ATR no se puede calcular o está ausente, la operación es **RECHAZADA (IGNORED)**.",
    das_injection
)

with open('docs/DECISION_AGENT_SYSTEM.md', 'w') as f:
    f.write(das)

# --- Update docs/WORKFLOW_ARCHITECTURE.md ---
with open('docs/WORKFLOW_ARCHITECTURE.md', 'r') as f:
    wa = f.read()

wa_injection = """PASO 6: DECISION ENGINE (RISK MANAGEMENT & ACTIVE SIZING)
├─ PASO 0 (Pre-Emptive): Revisar SL (1.5x) y TP (3.0x) vs current_price.
│   └─ SI SE TOCA UMBRAL: 'Sell-Off' mecánico o Take Profit del 100%, ABORTAR análisis cualitativo.
├─ Process desk recommendations
├─ Active Position Management:
│   ├─ Pyramiding (Scale-In): Aumenta posición en ganadores si Confianza >= 0.85 y RSI < 65.
│   └─ Trimming (Recortes): Venta del 25% si PnL > 5% y agotamiento técnico (RSI > 75).
├─ Risk Guardrails: Stop Loss estrictamente en 1.5x ATR y validación contra MAX_PORTFOLIO_EXPOSURE.
├─ Reject Rule: Si falta ATR, el trade es IGNORED."""

wa = wa.replace(
    "PASO 6: DECISION ENGINE (RISK MANAGEMENT)\n├─ PASO 0 (Pre-Emptive): Revisar SL (1.5x) y TP (3.0x) vs current_price.\n│   └─ SI SE TOCA UMBRAL: 'Sell-Off' mecánico, usando `avg_entry_price` para PnL, y ABORTAR análisis cualitativo.\n├─ Process desk recommendations\n├─ Risk Guardrails: Stop Loss estrictamente en 1.5x ATR.\n├─ Reject Rule: Si falta ATR, el trade es IGNORED.",
    wa_injection
)

with open('docs/WORKFLOW_ARCHITECTURE.md', 'w') as f:
    f.write(wa)

print("Documentation updated successfully.")
