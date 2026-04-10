"""Hypothesis Generator: Creates investment hypotheses based on fundamental analysis."""

import os
import sys
import json
import logging
import argparse
from typing import List, Dict
from dotenv import load_dotenv
from google.genai import Client

# Add parent directory to path to import trading_mvp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.core.dashboard_api_client import insert_exploration

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def generate_hypothesis(tickers: List[str]) -> Dict:
    """
    Generate investment hypothesis for given tickers using Gemini.

    Args:
        tickers: List of ticker symbols to analyze

    Returns:
        Dictionary containing investment hypothesis
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model}")

    client = Client(api_key=api_key)

    prompt = f"""
    You are an investment research analyst. Analyze the following ticker symbols and generate a comprehensive investment hypothesis.

    Tickers: {', '.join(tickers)}

    Your analysis should include:
    1. Investment thesis (bullish/bearish/neutral)
    2. Key fundamental drivers
    3. Major catalysts (both positive and negative)
    4. Sector context and competitive positioning
    5. Timeline expectations (short-term/medium-term/long-term)
    6. Confidence level (High/Medium/Low)

    Provide your response in JSON format:
    {{
        "thesis": "bullish/bearish/neutral",
        "drivers": ["driver 1", "driver 2", ...],
        "catalysts": {{
            "positive": ["catalyst 1", ...],
            "negative": ["catalyst 1", ...]
        }},
        "sector_context": "brief sector analysis",
        "positioning": "competitive positioning",
        "timeline": "short-term/medium-term/long-term",
        "confidence": "High/Medium/Low",
        "reasoning": "detailed explanation"
    }}

    Response MUST be valid JSON.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        # Process JSON response
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()

        hypothesis = json.loads(clean_text)

        logger.info(f"Generated hypothesis for {len(tickers)} tickers: {hypothesis.get('thesis')}")
        return hypothesis

    except Exception as e:
        logger.error(f"Error generating hypothesis: {e}")
        return {
            "thesis": "neutral",
            "drivers": [],
            "catalysts": {"positive": [], "negative": []},
            "sector_context": "Analysis failed",
            "positioning": "N/A",
            "timeline": "N/A",
            "confidence": "Low",
            "reasoning": f"Error: {str(e)}"
        }

def main():
    """Main entry point for Hypothesis Generator CLI."""
    parser = argparse.ArgumentParser(description="Generate investment hypotheses for tickers")
    parser.add_argument("--tickers", type=str, required=True, help="Comma-separated list of tickers")

    args = parser.parse_args()
    tickers = [t.strip().upper() for t in args.tickers.split(",")]

    hypothesis = generate_hypothesis(tickers)

    print(f"\n{'='*80}")
    print(f"INVESTMENT HYPOTHESIS FOR {', '.join(tickers)}")
    print(f"{'='*80}")
    print(f"Thesis: {hypothesis.get('thesis', 'N/A').upper()}")
    print(f"Confidence: {hypothesis.get('confidence', 'N/A')}")
    print(f"Timeline: {hypothesis.get('timeline', 'N/A')}")
    print(f"\nKey Drivers:")
    for driver in hypothesis.get('drivers', []):
        print(f"  • {driver}")
    print(f"\nPositive Catalysts:")
    for catalyst in hypothesis.get('catalysts', {}).get('positive', []):
        print(f"  + {catalyst}")
    print(f"\nNegative Catalysts:")
    for catalyst in hypothesis.get('catalysts', {}).get('negative', []):
        print(f"  - {catalyst}")
    print(f"\nReasoning: {hypothesis.get('reasoning', 'N/A')}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
