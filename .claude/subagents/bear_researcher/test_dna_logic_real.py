import os
import json
from dotenv import load_dotenv
from google.genai import Client
from agent import analyze_bear_case

load_dotenv()

def test_bear_dna_logic_real_data():
    ticker = "USO"
    # Datos reales extraídos de la base de datos Supabase
    news_context = """
    - Title: Trump Says Iran's Doing 'Poor Job' Over Strait Of Hormuz: Oil Spikes, Dow Futures Slip
    - Summary: U.S. stock futures dipped while oil prices surged above $98 as Donald Trump warned Iran over disruptions in the Strait of Hormuz.
    - Context: Geopolitical tension in the Middle East, specifically threats to the Strait of Hormuz (a major oil artery).
    """
    
    print(f"--- TESTING BEAR RESEARCHER WITH REAL DATA FOR {ticker} ---")
    print("Market Context (The 'Conflict'):")
    print(news_context)
    
    analysis = analyze_bear_case(ticker, news_context)
    
    print("\n" + "="*70)
    print(f"VERDICT FOR {ticker}: {analysis.get('overall_sentiment')}")
    print(f"ASSET DNA: {analysis.get('asset_dna')}")
    print(f"BEARISH CATALYSTS FOR THIS DNA: {analysis.get('bearish_catalysts_for_dna')}")
    print("\nDEEP ANALYSIS (THE REASONING):")
    print(analysis.get('deep_analysis'))
    print("\nARGUMENTS (WHY IT SHOULD BE NEUTRAL/BULLISH):")
    for arg in analysis.get('arguments', []):
        print(f"  • {arg}")
    print("="*70)

if __name__ == "__main__":
    test_bear_dna_logic_real_data()
