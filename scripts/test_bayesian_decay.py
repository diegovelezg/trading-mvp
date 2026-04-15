import math

def apply_bayesian_decay(initial_nlp_shock: float, days_passed: float, half_life_days: float = 3.0) -> float:
    """Aplica decaimiento exponencial a un shock de noticias."""
    if days_passed < 0: return initial_nlp_shock
    decay_constant = math.log(2) / half_life_days
    residual_score = initial_nlp_shock * math.exp(-decay_constant * days_passed)
    return round(residual_score, 3)

def simulate_scenario(ticker, description, base_quant, initial_shock, half_life, threshold=0.75, days=10):
    print(f"\n{'='*60}")
    print(f"🛠️  SIMULACIÓN: {ticker} - {description}")
    print(f"📊 Quant Base (Fijo): {base_quant:.2f} | 💥 Shock Inicial: {initial_shock:+.2f} | ⏱️ Half-life: {half_life} días")
    print(f"🎯 Umbral de Compra: >= {threshold:.2f}")
    print(f"{'='*60}")
    
    for day in range(days + 1):
        # Calcular el shock residual para el día actual
        current_shock = apply_bayesian_decay(initial_shock, day, half_life)
        
        # El score final es la suma del técnico (Quant) + el shock fundamental (NLP)
        final_score = base_quant + current_shock
        
        # Acotamos entre 0 y 1 (o 100%)
        final_score = max(0.0, min(1.0, final_score))
        
        # Decisión
        action = "🟩 BUY (Ejecutar)" if final_score >= threshold else "🟨 HOLD (Esperar)"
        
        # Formato de barras para visualizar
        shock_bar_len = int(abs(current_shock) * 20)
        shock_bar = ("🟥" if current_shock < 0 else "🟩") * shock_bar_len
        
        print(f"Día {day:02d} | Shock NLP: {current_shock:+6.3f} {shock_bar:<20} | Score Final: {final_score:5.3f} | {action}")

if __name__ == '__main__':
    # Escenario 1: TSM (Quant fuerte, Shock negativo duradero)
    # Imaginemos que el precio sube (Quant = 0.85), pero China hace ejercicios militares (Shock = -0.45).
    # Half-life de 4 días (el mercado tarda más en digerir riesgo geopolítico).
    simulate_scenario(
        ticker="TSM", 
        description="Tendencia Alcista bloqueada por Pánico Geopolítico",
        base_quant=0.85, 
        initial_shock=-0.45, 
        half_life=4.0
    )
    
    # Escenario 2: NVDA (Quant neutral, Shock positivo rápido)
    # El precio está lateral (Quant = 0.65), pero anuncian ganancias récord (Shock = +0.35).
    # Half-life de 2 días (la euforia de ganancias se desvanece rápido si el precio no acompaña).
    simulate_scenario(
        ticker="NVDA", 
        description="Mercado Lateral impulsado por Euforia de Ganancias",
        base_quant=0.60, 
        initial_shock=0.35, 
        half_life=2.0
    )
