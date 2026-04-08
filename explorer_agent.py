import os
import json
import logging
import argparse
from typing import List, Optional
from dotenv import load_dotenv
from google.genai import Client
from db_manager import insert_exploration
from macro_analyst import ingest_and_analyze

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def discover_tickers(prompt: str) -> List[str]:
    """
    Uses Gemini to discover a list of relevant ticker symbols based on a thematic prompt.
    
    Args:
        prompt: The thematic idea to explore (e.g., "Small caps in gas and nuclear energy").
        
    Returns:
        A list of ticker symbols.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required in environment variables.")
    
    client = Client(api_key=api_key)
    
    gen_prompt = f"""
    You are a financial research scout. Based on the following thematic prompt, 
    identify a cluster of at least 5-10 relevant stock ticker symbols (US exchanges).
    
    Theme: {prompt}
    
    Provide your response in JSON format with the following keys:
    - tickers: a list of string ticker symbols (e.g., ["AAPL", "TSLA"])
    - reasoning: a brief explanation of why these tickers were chosen.
    
    Response MUST be a valid JSON.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=gen_prompt
        )
        
        # Process JSON response
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()
            
        result = json.loads(clean_text)
        tickers = result.get("tickers", [])
        
        # Clean up tickers (remove non-alphanumeric just in case)
        cleaned_tickers = [str(t).strip().upper() for t in tickers if t]
        
        # Save to database
        insert_exploration(prompt, json.dumps({"tickers": cleaned_tickers, "reasoning": result.get("reasoning", "")}))
        
        logger.info(f"Discovered {len(cleaned_tickers)} tickers for theme: {prompt}")
        return cleaned_tickers
        
    except Exception as e:
        logger.error(f"Error discovering tickers: {e}")
        return []

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
    ingest_and_analyze(tickers)

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
