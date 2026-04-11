"""Bear Researcher: Identifies bearish investment case and downside risks."""

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

def analyze_bear_case(ticker: str, news_context: str = "No recent news provided.", dna: Dict = None) -> Dict:
    """Analyze bearish case for a ticker using the provided Asset DNA.

    Args:
        ticker: Ticker symbol to analyze
        news_context: Recent news or market context
        dna: Pre-defined asset DNA from DNAManager

    Returns:
        Dictionary containing bearish analysis
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
    You are a Senior Bearish Analyst. Your task is to build a high-conviction NEGATIVE case for {ticker}.
    
    CRITICAL SOURCE OF TRUTH (Asset DNA):
    ---
    {dna_context}
    ---

    CONTEXTUAL NEWS:
    ---
    {news_context}
    ---

    YOUR MISSION:
    1. ANALYZE if the current news/context matches the 'bearish_catalysts' defined in the Asset DNA.
    2. REASONING: If the news is 'bad for the world' but 'BULLISH' for this specific DNA (e.g., war for oil), you MUST be honest and provide a NEUTRAL/HOLD verdict.
    3. ARGUMENTS: Focus on downside risks that actually apply to this asset type and its core drivers.

    Provide your response in JSON format:
    {{
        "arguments": ["3-5 specific bearish arguments based on DNA and news"],
        "risks": [
            {{"event": "...", "impact": "...", "timeline": "...", "causal_link": "..."}}
        ],
        "price_targets": {{
            "base": {{"target": 0, "logic": "..."}},
            "bear": {{"target": 0, "logic": "..."}},
            "super_bear": {{"target": 0, "logic": "..."}}
        }},
        "red_flags": ["Specific indicators to watch"],
        "deep_analysis": "Institutional-grade monologue explaining why you are bearish (or why you are neutral despite bad news).",
        "overall_sentiment": "Strong Sell/Sell/Hold/Neutral",
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
        logger.info(f"Bear analysis for {ticker}: {analysis.get('overall_sentiment')}")
        return analysis

    except Exception as e:
        logger.error(f"Error analyzing bear case: {e}")
        return {
            "asset_dna": "Unknown",
            "arguments": [], 
            "risks": [], 
            "overall_sentiment": "Hold",
            "deep_analysis": f"Analysis failed: {str(e)}"
        }

def main():
    """Main entry point for Bear Researcher CLI."""
    parser = argparse.ArgumentParser(description="Analyze bearish investment case")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol")

    args = parser.parse_args()
    ticker = args.ticker.upper()

    analysis = analyze_bear_case(ticker)

    print(f"\n{'='*80}")
    print(f"📉 BEARISH ANALYSIS - {ticker}")
    print(f"{'='*80}")
    print(f"Overall Sentiment: {analysis.get('overall_sentiment', 'N/A')}")
    print(f"Confidence: {analysis.get('confidence', 'N/A')}\n")

    print("⚠️ Bearish Arguments:")
    for i, arg in enumerate(analysis.get('arguments', []), 1):
        print(f"  {i}. {arg}")

    print("\n🚨 Risk Factors:")
    for risk in analysis.get('risks', []):
        print(f"  • {risk.get('event', 'N/A')} ({risk.get('impact', 'N/A')}) - {risk.get('timeline', 'N/A')}")

    print("\n💸 Price Targets:")
    targets = analysis.get('price_targets', {})
    for scenario, target_info in targets.items():
        print(f"  {scenario.capitalize()}: ${target_info.get('target', 'N/A')} - {target_info.get('reasoning', 'N/A')}")

    print(f"\n🚩 Red Flags:")
    for flag in analysis.get('red_flags', []):
        print(f"  • {flag}")

    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
