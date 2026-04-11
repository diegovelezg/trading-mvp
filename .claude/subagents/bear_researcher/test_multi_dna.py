import os
import json
from dotenv import load_dotenv
from google.genai import Client
import sys

# Añadir el path para importar el agente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from agent import analyze_bear_case

load_dotenv()

def run_dna_test(ticker, news_context):
    print(f"\n{'='*80}")
    print(f"🔍 TESTING ASSET DNA: {ticker}")
    print(f"{'='*80}")
    print(f"Context: {news_context.strip()}")
    
    try:
        analysis = analyze_bear_case(ticker, news_context)
        
        print(f"\n🧬 ASSET DNA: {analysis.get('asset_dna')}")
        print(f"📉 VERDICT: {analysis.get('overall_sentiment')}")
        print(f"🎯 CONFIDENCE: {analysis.get('confidence_score')}")
        
        print("\n🧠 LOGICAL REASONING (The 'Why'):")
        print(analysis.get('deep_analysis'))
        
        print("\n⚠️ REAL BEARISH FACTORS FOR THIS DNA:")
        for factor in analysis.get('bearish_catalysts_for_dna', []):
            print(f"  • {factor}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    # Test 1: NVDA (Tech Growth) con contexto de Recesión
    run_dna_test("NVDA", "Global recession fears rise as consumer spending drops. Tech valuations are under pressure due to high interest rates.")
    
    # Test 2: TLT (Bonds) con contexto de Inflación
    run_dna_test("TLT", "CPI data comes in hotter than expected. The Fed signals 'Higher for Longer' interest rate policy to combat persistent inflation.")
    
    # Test 3: GLD (Gold) con contexto de Guerra (El test de fuego)
    run_dna_test("GLD", "Geopolitical tensions explode in Eastern Europe and Middle East. Massive 'Risk-Off' sentiment in global equity markets.")
