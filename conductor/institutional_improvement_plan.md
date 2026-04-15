# Plan de Mejora Institucional: Mesa de Inversiones

**Objetivo:** Elevar el sistema de ejecución algorítmica desde una aproximación cautelosa ("retail") hacia un modelo de gestión activa institucional ("alpha generation"), corrigiendo desalineaciones estructurales entre los modelos predictivos y el motor de ejecución (Executioner).

**Archivos Clave Afectados (Estimado inicial):**
*   `trading_mvp/agents/executioner.py` (o similar, donde resida la lógica final de toma de decisión de ejecución).
*   `trading_mvp/agents/macro_analyst.py` o los agentes fundamentales que emiten el "BULLISH".
*   `trading_mvp/analysis/quant_stats.py` o módulo de análisis técnico.
*   `trading_mvp/config/risk_management.py` (Lógica de "Pyramiding" y *Starter Positions*).

---

## Fase 1: Alineación Crítica (Fundamental vs. Price Action)

### Problema:
El motor NLP (Sentimiento) está recomendando acciones `BULLISH` a pesar de que el activo se encuentre en un régimen técnico de mercado a la baja (Ej. $MA con RSI 52, Trend BEARISH).

### Implementación (Filtro de Régimen):
1.  **Creación del Guardarraíl Técnico:**
    *   Modificar la lógica de síntesis (el Orquestador o el Evaluador Final) para que evalúe la tendencia técnica *antes* de aceptar la recomendación del motor NLP.
    *   **Regla Institucional:** Si `trend == "BEARISH"` y el precio está por debajo de su SMA200 (o SMA50), el sistema **NO DEBE** emitir una señal "BULLISH".
    *   En su lugar, el sistema emitirá "WATCHLIST" (vigilar posible giro) o "DEEP VALUE" (para estrategias de reversión a la media), pero no autorizará compras activas en contra del momento primario.
2.  **Verificación:** Ejecutar backtest de señales pasadas con el nuevo filtro; validar que activos como $MA o $SNPS en la ejecución actual hubieran sido marcados correctamente como "NO ENTRY".

---

## Fase 2: Auditoría y Corrección del *Confidence Scoring Bug*

### Problema:
Discrepancia entre el *Average Confidence* crudo emitido por los modelos (Ej. $PWR = 0.87, $BWXT = 0.85) y lo que lee el agente de ejecución, resultando en decisiones justificadas como "Señal de BAJA CONFIANZA (0.68/0.67)".

### Implementación (Rastreo de Flujo de Datos):
1.  **Auditoría del Tensor:** Rastrear cómo se pasa el campo `avg_confidence` desde el `TickerAnalyst` hacia el `Executioner` o `CIO`.
2.  **Identificación del Bug de Ponderación:** Es probable que el orquestador esté sobreescribiendo el `avg_confidence` con la `positive_ratio` (Ej. 0.67 de $BKR se convirtió en 0.67 de confianza en las notas de $BWXT, o similar).
3.  **Corrección:**
    *   Asegurar que el `Confidence Score` final sea una métrica unificada (ej. 70% NLP, 30% Alineación Cuantitativa).
    *   Las notas generadas por el agente de ejecución deben leer del diccionario `data_integrity` y el `avg_confidence` global, no del ratio crudo de sentimiento.
4.  **Verificación:** Lanzar simulaciones unitarias verificando que el *Confidence Score* final mapea exactamente 1:1 con la entrada en base de datos.

---

## Fase 3: Gestión de Posiciones Dinámica (Pyramiding)

### Problema:
Gestión de riesgo binaria: "Si ya tengo posición ($BKR), entonces IGNORED", obligando a intervención manual. Los fondos grandes *añaden* tamaño a los ganadores con momentum.

### Implementación (Scale-In Dinámico):
1.  **Lógica de Tamaños (Tranches):**
    *   Permitir que el estado del portafolio devuelva el tamaño actual de la posición en tramos (ej. `Starter`, `Core`, `Max Size`).
2.  **Condiciones para Pyramiding (Añadir Lotes):**
    *   Si el sistema detecta señal "BULLISH" fuerte (Confianza > 0.80), y...
    *   El activo ya está en el portafolio (`is_in_portfolio == True`), y...
    *   El activo está mostrando "Momentum: POSITIVE" (y un RSI no extremo de sobrecompra).
3.  **Acción (`Action_Taken`):**
    *   En lugar de "IGNORED", emitir "SCALE_IN" o "ADD_ON".
    *   Calcular el tamaño adicional usando la volatilidad y el ATR actual (Volatility-adjusted sizing).
4.  **Verificación:** Comprobar que en simulaciones, si se pasa un activo que ya se posee pero sigue mostrando métricas alcistas fuertes, el sistema propone incrementar la posición un porcentaje en lugar de descartarlo.

---

## Fase 4: Reducción de "Parálisis por Análisis" (Starter Positions)

### Problema:
Falta de agresividad en configuraciones ideales (Ej. $PWR: Macro claro, Trend Bullish, Confianza alta -> Resultado: "Monitoreando para dirección más clara"). Esperar la certeza absoluta evapora el *Alpha*.

### Implementación (Gatillo de Alta Convicción):
1.  **Redefinición de los Umbrales de Entrada:**
    *   Ajustar el agente de ejecución para que, ante una combinación de: `Trend: BULLISH` + `Confidence > 0.85` + `Positive_Ratio > 0.60`, el sistema **ejecute** proactivamente.
2.  **Implementación de "Starter Position" (`Pilot Sizing`):**
    *   Si el sistema aún detecta cierta volatilidad o ruido de mercado a corto plazo, en lugar de no hacer nada (`NONE` o `HELD`), debe entrar con un tamaño fraccionado (ej. 25% del tamaño objetivo).
    *   Acción (`Action_Taken`): "STARTER_POSITION" o "BOUGHT_PARTIAL".
3.  **Verificación:** Refactorizar los *prompts* o lógicas del agente decisor para penalizar la "indecisión inactiva" (esperar) cuando los vientos de cola y los indicadores están alineados a favor.

---

## Plan de Verificación Global (Rollout)

1.  **Despliegue Local (Simulación):** Correr `demo_full_system.py` (o script equivalente de testeo E2E) en un universo de 10 tickers controlados.
2.  **Validación de DB:** Consultar la tabla `investment_decisions` para asegurar que:
    *   Los activos *Bearish* no emiten señal *BULLISH*.
    *   Las notas reflejan el `avg_confidence` correcto.
    *   Los activos en portafolio de alto rendimiento reciben un `SCALE_IN`.
    *   Los *setups* perfectos no se quedan en `NONE`, sino que inician una `STARTER_POSITION`.
3.  **Firma del Head Quant:** Confirmación manual de los nuevos comportamientos (logs crudos).
