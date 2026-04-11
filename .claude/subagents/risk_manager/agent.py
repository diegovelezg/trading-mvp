"""Risk Manager: Assesses risks and determines position sizing."""

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

def assess_risk(ticker: str, position_size: float, dna: Dict = None) -> Dict:
    """Assess risk for a ticker and position size using provided Asset DNA.

    Args:
        ticker: Ticker symbol
        position_size: Dollar amount of position
        dna: Pre-defined asset DNA from DNAManager

    Returns:
        Dictionary containing risk assessment
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model}")

    client = Client(api_key=api_key)

    # Use provided DNA or fallback
    dna_context = json.dumps(dna, indent=2) if dna else "Unknown asset DNA."

    prompt = f"""
    You are a Senior Risk Manager. Your goal is to define the risk parameters for a ${position_size:,.0f} position in {ticker}.

    SOURCE OF TRUTH (Asset DNA):
    ---
    {dna_context}
    ---

    YOUR MANDATE:
    1. DNA-BASED VOLATILITY: Use the 'geopolitical_sensitivity' and 'interest_rate_sensitivity' to define the risk profile.
    2. SMART STOP LOSS: If an asset has HIGH geopolitical sensitivity (e.g., Oil), allow for more 'volatility breathing room' in the Stop Loss to avoid being stopped out by noise.
    3. SIZING ADJUSTMENT: Suggest adjusting the ${position_size:,.0f} based on the DNA risk. Lower the size for high-sensitivity/high-beta assets.
    4. HEDGING: Suggest specific assets to hedge this position based on its DNA drivers (e.g., if sensitive to rates, hedge with Treasuries).

    Provide your response in JSON format:
    {{
        "risk_score": "Low/Medium/High",
        "volatility_profile": "Analysis of volatility based on DNA sensitivities",
        "stop_loss": {{
            "percentage": 0.0,
            "rationale": "Why this SL fits the asset DNA"
        }},
        "position_size_recommendation": "USD amount adjusted for DNA risk",
        "hedging_strategy": "Specific assets or actions to mitigate DNA risks",
        "deep_analysis": "Internal monologue on DNA-aware risk management.",
        "risk_factors": ["List of DNA-specific risks"]
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

        assessment = json.loads(clean_text)
        logger.info(f"Risk assessment for {ticker}: {assessment.get('risk_score')}")
        return assessment

    except Exception as e:
        logger.error(f"Error assessing risk: {e}")
        return {
            "risk_score": "Medium",
            "stop_loss": {"percentage": 0.05, "price": 0},
            "risk_reward_ratio": "1:2"
        }

def main():
    """Main entry point for Risk Manager CLI."""
    parser = argparse.ArgumentParser(description="Assess investment risk")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker symbol")
    parser.add_argument("--position-size", type=float, required=True, help="Position size in dollars")

    args = parser.parse_args()
    ticker = args.ticker.upper()
    position_size = args.position_size

    assessment = assess_risk(ticker, position_size)

    print(f"\n{'='*80}")
    print(f"⚡ RISK ASSESSMENT - {ticker} (${position_size:,.0f} position)")
    print(f"{'='*80}")
    print(f"Overall Risk Score: {assessment.get('risk_score', 'N/A')}")
    print(f"Volatility: {assessment.get('volatility', 'N/A')}")
    print(f"Market Correlation: {assessment.get('correlation_with_market', 'N/A')}\n")

    print(f"🛡️ Stop Loss:")
    stop = assessment.get('stop_loss', {})
    print(f"  {stop.get('percentage', 0)*100:.1f}% (${stop.get('price', 0):.2f})")
    print(f"  Reasoning: {stop.get('reasoning', 'N/A')}")

    print(f"\n🎯 Take Profit Levels:")
    for tp in assessment.get('take_profit', []):
        print(f"  {tp.get('target', 'N/A')}: ${tp.get('level', 0):.2f} - {tp.get('reasoning', 'N/A')}")

    print(f"\n📊 Risk/Reward: {assessment.get('risk_reward_ratio', 'N/A')}")

    print(f"\n💼 Position Size:")
    print(f"  Recommendation: {assessment.get('position_size_recommendation', 'N/A')}")
    print(f"  Reasoning: {assessment.get('position_size_reasoning', 'N/A')}")

    print(f"\n⚠️ Risk Factors:")
    for factor in assessment.get('risk_factors', []):
        print(f"  • {factor}")

    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
