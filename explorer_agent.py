import os
import json
import logging
from typing import List, Optional
from dotenv import load_dotenv
from google.genai import Client

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
        
        logger.info(f"Discovered {len(cleaned_tickers)} tickers for theme: {prompt}")
        return cleaned_tickers
        
    except Exception as e:
        logger.error(f"Error discovering tickers: {e}")
        return []

if __name__ == "__main__":
    # Quick test
    test_prompt = "Small caps in gas and nuclear energy"
    discovered = discover_tickers(test_prompt)
    print(f"Discovered tickers: {discovered}")
