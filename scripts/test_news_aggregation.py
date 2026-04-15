import math

def get_source_weight(source: str) -> float:
    """Simula la autoridad de diferentes fuentes de noticias."""
    tier_1 = ['reuters', 'bloomberg', 'wsj', 'sec']
    tier_2 = ['cnbc', 'yahoo', 'marketwatch']
    
    source = source.lower()
    if any(t in source for t in tier_1): return 1.0
    if any(t in source for t in tier_2): return 0.6
    return 0.2  # Blogs, rumores, twitter, etc.

def calculate_daily_nlp_shock(news_items: list) -> float:
    """
    Calcula el Shock NLP total combinando Relevancia (ADN), Autoridad de Fuente y Saturación (tanh).
    """
    total_raw_impact = 0.0
    
    print("\n--- Analizando Noticias del Día ---")
    for i, news in enumerate(news_items):
        base_sentiment = news['sentiment_score']
        dna_relevance = news['confidence'] # Qué tanto pega en el ADN
        source_authority = get_source_weight(news['source'])
        
        # Ponderación individual
        impact = base_sentiment * dna_relevance * source_authority
        total_raw_impact += impact
        
        print(f"Noticia {i+1} [{news['source'].upper()}]: Sent={base_sentiment:+.2f} | ADN_Match={dna_relevance:.2f} | Auth={source_authority:.1f} -> Impacto={impact:+.3f}")
    
    # Saturación: Comprime valores extremos entre -1.0 y 1.0
    final_daily_shock = math.tanh(total_raw_impact)
    
    print(f"-> Impacto Crudo Total: {total_raw_impact:+.3f}")
    print(f"-> SHOCK FINAL (Saturado): {final_daily_shock:+.3f}")
    print("-----------------------------------")
    
    return round(final_daily_shock, 3)

def apply_bayesian_decay(initial_shock: float, days_passed: int, half_life_days: float = 3.0) -> float:
    """Aplica decaimiento exponencial a un shock de noticias."""
    if days_passed < 0: return initial_shock
    decay_constant = math.log(2) / half_life_days
    return round(initial_shock * math.exp(-decay_constant * days_passed), 3)

def run_simulation():
    # Simulamos el día de resultados caóticos de TSM
    news_day_0 = [
        # 1. Noticia GRAVE y RELEVANTE de fuente TOP (Rompe la tesis IA)
        {"source": "Reuters", "sentiment_score": -0.90, "confidence": 0.95},
        
        # 2. Rumor bajista de fuente BAJA (Ruido)
        {"source": "Seeking Alpha", "sentiment_score": -0.60, "confidence": 0.80},
        
        # 3. Buena noticia pero IRRELEVANTE al ADN (Premio ambiental)
        {"source": "Bloomberg", "sentiment_score": +0.70, "confidence": 0.15},
        
        # 4. Otra noticia mala de fuente MEDIA (Confirma la primera)
        {"source": "CNBC", "sentiment_score": -0.75, "confidence": 0.85},
    ]
    
    print("="*60)
    print("🧪 TEST: AGREGACIÓN DE NOTICIAS + DECAIMIENTO BAYESIANO")
    print("Activo: TSM | Quant Base Constante: 0.80 (Fuerte Compra)")
    print("="*60)
    
    # 1. Calculamos el Shock del Día 0
    initial_shock = calculate_daily_nlp_shock(news_day_0)
    
    # 2. Simulamos el paso del tiempo
    base_quant = 0.80
    threshold = 0.75
    half_life = 3.0 # El shock se reduce a la mitad cada 3 días
    
    print("\n📅 PROYECCIÓN DE EJECUCIÓN (Los próximos 7 días):")
    for day in range(8):
        current_shock = apply_bayesian_decay(initial_shock, day, half_life)
        final_score = max(0.0, min(1.0, base_quant + current_shock))
        
        action = "🟩 BUY" if final_score >= threshold else "🟨 HOLD"
        
        print(f"Día {day} | Shock Residual: {current_shock:+6.3f} | Score Final: {final_score:.3f} | Decisión: {action}")

if __name__ == "__main__":
    run_simulation()
