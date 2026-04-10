import os
import sys
import json
import logging
import argparse
from typing import List, Optional
from dotenv import load_dotenv
from google.genai import Client

# Add parent directory to path to import trading_mvp modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.core.dashboard_api_client import insert_exploration

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def discover_tickers(prompt: str) -> List[dict]:
    """
    Uses Gemini to discover a list of relevant tickers with basic info in Spanish.

    Args:
        prompt: The thematic idea to explore.

    Returns:
        A list of dictionaries with ticker details.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required.")

    model = os.getenv("GEMINI_API_MODEL_01", "gemini-2.0-flash")
    client = Client(api_key=api_key)

    gen_prompt = f"""
    You are a financial research scout. Based on the theme: "{prompt}",
    identify 5-10 relevant stock tickers (US exchanges).

    For EACH ticker, you MUST provide:
    1. Ticker symbol
    2. Company Name
    3. Industry Sector
    4. A 1-sentence description in SPANISH (description_es).

    Provide your response in JSON format:
    {{
        "results": [
            {{
                "ticker": "TICKER",
                "name": "Company Name",
                "sector": "Sector",
                "description_es": "Breve descripción en castellano sobre su actividad."
            }}
        ],
        "reasoning": "Brief overall explanation in Spanish"
    }}
    """

    try:
        response = client.models.generate_content(model=model, contents=gen_prompt)
        clean_text = response.text.strip()
        if clean_text.startswith("```json"): clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"): clean_text = clean_text[3:-3].strip()

        data = json.loads(clean_text)
        results = data.get("results", [])
        
        # Save to database
        tickers_only = [r['ticker'].upper() for r in results]
        criteria = extract_search_criteria(prompt)
        insert_exploration(
            prompt=prompt,
            criteria=criteria,
            tickers=tickers_only,
            reasoning=data.get("reasoning", "")
        )

        logger.info(f"Discovered {len(results)} tickers with metadata.")
        return results

    except Exception as e:
        logger.error(f"Error in explorer: {e}")
        return []

def extract_search_criteria(prompt: str) -> str:
    """
    Extract and structure the search criteria from the prompt.

    Args:
        prompt: The user's thematic prompt

    Returns:
        Structured criteria description
    """
    # Use Gemini to structure the criteria
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback to simple extraction
        return f"Thematic search for: {prompt}"

    model = os.getenv("GEMINI_API_MODEL_01", "gemini-2.0-flash")
    client = Client(api_key=api_key)

    criteria_prompt = f"""
    Extract and structure the investment criteria from this thematic prompt:

    "{prompt}"

    Provide a structured criteria description including:
    - Market cap range (if specified)
    - Sector focus
    - Geographic focus
    - Technology/theme focus
    - Time horizon (if any)
    - Any specific constraints

    Return as a concise criteria description (2-3 sentences).
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=criteria_prompt
        )
        return response.text.strip()
    except:
        return f"Thematic search for: {prompt}"

def handover_to_analyst(tickers: List[str]) -> None:
    """
    Triggers the Macro Analyst to ingest and analyze news for the given tickers.

    Args:
        tickers: A list of ticker symbols to analyze.
    """
    if not tickers:
        logger.warning("No tickers provided for handover.")
        return

    logger.info(f"Handing over {len(tickers)} tickers to Macro Analyst...")
    # Import directly from the macro_analyst module
    import subprocess
    macro_analyst_path = os.path.join(os.path.dirname(__file__), "..", "macro_analyst", "agent.py")
    symbols_str = ",".join(tickers)
    subprocess.run([sys.executable, macro_analyst_path, "--symbols", symbols_str])

def main() -> None:
    """Main entry point for the Explorer Agent CLI."""
    parser = argparse.ArgumentParser(description="Discover stock tickers based on a thematic prompt.")
    parser.add_argument("prompt", type=str, help="The thematic prompt to explore.")
    parser.add_argument("--analyze", action="store_true", help="Automatically trigger Macro Analyst for discovered tickers.")

    args = parser.parse_args()

    discovered = discover_tickers(args.prompt)
    if discovered:
        print(f"\nDiscovered Tickers for '{args.prompt}':")
        for ticker in discovered:
            print(f"- {ticker}")

        if args.analyze:
            handover_to_analyst(discovered)
    else:
        print(f"\nNo tickers discovered for '{args.prompt}'.")

if __name__ == "__main__":
    main()
