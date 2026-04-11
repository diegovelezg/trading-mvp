"""Bull Researcher: Identifies bullish investment case and upside potential."""

import os
import sys
import json
import logging
import argparse
from typing import Dict
from dotenv import load_dotenv
from google.genai import Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def analyze_bull_case(ticker: str, news_context: str = "No recent news provided.", dna: Dict = None) -> Dict:
    """Analyze bullish case for a ticker using the provided Asset DNA.

    Args:
        ticker: Ticker symbol to analyze
        news_context: Recent news or market context
        dna: Pre-defined asset DNA from DNAManager

    Returns:
        Dictionary containing bullish analysis
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model}")

    client = Client(api_key=api_key)

    # Use provided DNA or fallback to generic
    dna_context = json.dumps(dna, indent=2) if dna else "Unknown asset DNA."

    prompt = f"""
    You are a Senior Bullish Analyst. Your task is to build a high-conviction POSITIVE case for {ticker}.
    
    CRITICAL SOURCE OF TRUTH (Asset DNA):
    ---
    {dna_context}
    ---

    CONTEXTUAL NEWS:
    ---
    {news_context}
    ---

    YOUR MISSION:
    1. ANALYZE if the current news/context matches the 'bullish_catalysts' defined in the Asset DNA.
    2. REASONING: If the news is 'good for the world' but 'BEARISH' for this specific DNA (e.g., peace for gold), you MUST be honest and provide a NEUTRAL/HOLD verdict.
    3. CATALYSTS: Focus on upside drivers that actually apply to this asset type and its core drivers.

    Provide your response in JSON format:
    {{
        "arguments": ["3-5 specific bullish arguments based on DNA and news"],
        "catalysts": [
            {{"event": "...", "impact": "...", "timeline": "...", "causal_link": "..."}}
        ],
        "price_targets": {{
            "base": {{"target": 0, "logic": "..."}},
            "bull": {{"target": 0, "logic": "..."}},
            "blue_sky": {{"target": 0, "logic": "..."}}
        }},
        "deep_analysis": "Institutional-grade monologue explaining why you are bullish (or why you are neutral despite good news).",
        "overall_sentiment": "Strong Buy/Buy/Hold/Neutral",
        "confidence_score": 0.0-1.0
    }}

    Response MUST be a valid JSON.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        analysis = json.loads(clean_text)
        logger.info(f"Bull analysis for {ticker}: {analysis.get('overall_sentiment')}")
        return analysis

    except Exception as e:
        logger.error(f"Error analyzing bull case: {e}")
        return {
            "asset_dna": "Unknown",
            "arguments": [], 
            "catalysts": [], 
            "overall_sentiment": "Hold",
            "deep_analysis": f"Analysis failed: {str(e)}"
        }

def main():
    """Main entry point for Bull Researcher CLI."""
    parser = argparse.ArgumentParser(description="Analyze bullish investment case")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol")

    args = parser.parse_args()
    ticker = args.ticker.upper()

    analysis = analyze_bull_case(ticker)

    print(f"\n{'='*80}")
    print(f"📈 BULLISH ANALYSIS - {ticker}")
    print(f"{'='*80}")
    print(f"Overall Sentiment: {analysis.get('overall_sentiment', 'N/A')}")
    print(f"Confidence: {analysis.get('confidence', 'N/A')}\n")

    print("🎯 Bullish Arguments:")
    for i, arg in enumerate(analysis.get('arguments', []), 1):
        print(f"  {i}. {arg}")

    print("\n🚀 Catalysts:")
    for catalyst in analysis.get('catalysts', []):
        print(f"  • {catalyst.get('event', 'N/A')} ({catalyst.get('impact', 'N/A')}) - {catalyst.get('timeline', 'N/A')}")

    print("\n💰 Price Targets:")
    targets = analysis.get('price_targets', {})
    for scenario, target_info in targets.items():
        print(f"  {scenario.capitalize()}: ${target_info.get('target', 'N/A')} - {target_info.get('reasoning', 'N/A')}")

    print(f"\n⚠️ Risks to Bull Case:")
    for risk in analysis.get('risks', []):
        print(f"  • {risk}")

    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
