import os
import json
from dotenv import load_dotenv
from google.genai import Client
from agent import analyze_bear_case

load_dotenv()

def test_bear_dna_logic():
    ticker = "USO"
    # Simulamos el contexto que causó el error original
    news_context = """
    - Middle East tensions escalate: Reports of potential conflict in Iran.
    - Global Inflation Surges: Consumer prices rising at fastest pace in decades.
    - Energy Costs Disruption: Supply chain risks in the Strait of Hormuz.
    - Market Sentiment: Fear is high, major stock indices are falling.
    """
    
    print(f"Testing BEAR RESEARCHER with Asset DNA Protocol for {ticker}...")
    print("Context Provided (Simulated 'Bad News'):")
    print(news_context)
    
    analysis = analyze_bear_case(ticker, news_context)
    
    print("\n" + "="*50)
    print(f"VERDICT FOR {ticker}: {analysis.get('overall_sentiment')}")
    print(f"ASSET DNA: {analysis.get('asset_dna')}")
    print(f"BEARISH CATALYSTS IDENTIFIED: {analysis.get('bearish_catalysts_for_dna')}")
    print("\nDEEP ANALYSIS (INTERNAL MONOLOGUE):")
    print(analysis.get('deep_analysis'))
    print("="*50)

if __name__ == "__main__":
    test_bear_dna_logic()
