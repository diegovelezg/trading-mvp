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

def analyze_bull_case(ticker: str) -> Dict:
    """Analyze bullish case for a ticker using Gemini.

    Args:
        ticker: Ticker symbol to analyze

    Returns:
        Dictionary containing bullish analysis
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model}")

    client = Client(api_key=api_key)

    prompt = f"""
    You are a Senior Bullish Analyst at a top-tier hedge fund. Analyze {ticker} and build a high-conviction POSITIVE investment case.

    Your task is to provide:
    1. EXHAUSTIVE BULLISH ARGUMENTS: 3-5 points with specific evidence and causal links (how X leads to Y).
    2. STRATEGIC CATALYSTS: Detailed events, expected impact magnitude, and specific timelines.
    3. PRICE TARGET SYNTHESIS: Base, Bull, and Blue-Sky scenarios with the underlying valuation logic for each.
    4. COUNTER-RISK ANALYSIS: Identify what could break the bull case and why you believe the upside outweighs it.
    5. DEEP ANALYSIS: A 2-paragraph "Internal Monologue" explaining your conviction.

    Provide your response in JSON format:
    {{
        "arguments": ["..."],
        "catalysts": [
            {{"event": "...", "impact": "...", "timeline": "...", "causal_link": "..."}}
        ],
        "price_targets": {{
            "base": {{"target": 0, "logic": "..."}},
            "bull": {{"target": 0, "logic": "..."}},
            "blue_sky": {{"target": 0, "logic": "..."}}
        }},
        "deep_analysis": "Your institutional-grade ratiocination here...",
        "overall_sentiment": "Strong Buy/Buy/Hold",
        "confidence_score": 0.0-1.0
    }}

    Response MUST be a valid JSON. Think step-by-step.
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
        return {"arguments": [], "catalysts": [], "overall_sentiment": "Hold"}

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
