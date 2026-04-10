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

def assess_risk(ticker: str, position_size: float) -> Dict:
    """Assess risk for a ticker and position size using Gemini.

    Args:
        ticker: Ticker symbol
        position_size: Dollar amount of position

    Returns:
        Dictionary containing risk assessment
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model}")

    client = Client(api_key=api_key)

    prompt = f"""
    You are a Senior Risk Manager at a systematic trading firm. Assess the risk for a ${position_size:,.0f} position in {ticker}.

    Your task is to provide:
    1. VOLATILITY SYNTHESIS: Analysis of price action volatility and how it dictates current risk parameters.
    2. TECHNICAL RISK DEFENSE: Justify the Stop Loss and Take Profit levels based on key technical levels, ATR (Average True Range), or standard deviations.
    3. CAPITAL ALLOCATION LOGIC: Explain why the proposed size of ${position_size:,.0f} is optimal or if it should be adjusted based on the "Kelly Criterion" or "Volatility Targeting" concepts.
    4. DRAWDOWN PROJECTION: Worst-case scenario analysis and potential recovery time.
    5. DEEP ANALYSIS: A 2-paragraph "Internal Monologue" explaining your risk conviction and potential hedging strategies.

    Provide your response in JSON format:
    {{
        "volatility": "Low/Medium/High",
        "stop_loss": {{
            "percentage": 0.0,
            "price": 0.0,
            "technical_defense": "..."
        }},
        "take_profit": [
            {{"level": 0.0, "logic": "..."}}
        ],
        "risk_reward_ratio": "...",
        "position_size_recommendation": "...",
        "sizing_logic": "Why this size makes sense...",
        "deep_analysis": "Your institutional-grade risk ratiocination here...",
        "risk_score": "Low/Medium/High",
        "risk_factors": ["..."]
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
