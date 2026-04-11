import os
import json
import logging
import re
from typing import Dict
from dotenv import load_dotenv
from google.genai import Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def extract_json_from_response(text: str) -> str:
    """
    Robustly extracts JSON from Gemini response, handling various formats.

    Args:
        text: Raw response text from Gemini

    Returns:
        Cleaned JSON string
    """
    # Remove leading/trailing whitespace
    clean_text = text.strip()

    # Try to find JSON object with regex - look for content between { and }
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, clean_text, re.DOTALL)

    if matches:
        # Return the largest match (most likely to be complete JSON)
        return max(matches, key=len)

    # Fallback: remove code blocks
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]

    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]

    return clean_text.strip()

def analyze_sentiment(text: str, ticker: str = "Unknown", dna: Dict = None) -> Dict:
    """
    Analyzes the sentiment of a text using Gemini 2.0 Flash with Asset DNA context.
    
    Args:
        text: The news content to analyze.
        ticker: Ticker symbol for context.
        dna: Asset DNA dictionary from DNAManager.
        
    Returns:
        A dictionary with 'sentiment' (float -1 to 1) and 'summary' (str).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required in environment variables.")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model} for {ticker} sentiment")

    client = Client(api_key=api_key)
    
    # Asset DNA context for the prompt
    dna_context = ""
    if dna:
        dna_context = f"""
        ASSET DNA FOR {ticker}:
        - Type: {dna.get('asset_type')}
        - Bullish Catalysts: {dna.get('bullish_catalysts')}
        - Bearish Catalysts: {dna.get('bearish_catalysts')}
        """

    prompt = f"""
    You are an expert Financial Sentiment Analyst. Analyze the following news for the ticker: {ticker}.
    
    {dna_context}

    YOUR MISSION:
    Determine if this news is Bullish, Bearish, or Neutral SPECIFICALLY for {ticker} based on its DNA.
    Example: Geopolitical conflict is BULLISH for Oil but BEARISH for Growth Tech.
    
    Provide your response STRICTLY in JSON format with these exact keys:
    - "sentiment": a float between -1 (extremely bearish for this asset) and 1 (extremely bullish for this asset)
    - "summary": a brief summary of the news and its specific impact on the asset
    - "reasoning": 1 sentence explaining why this sentiment was chosen based on the asset's nature

    IMPORTANT: Return ONLY the JSON object.

    News Content:
    {text}
    """
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        # Debug: log raw response
        logger.debug(f"Raw Gemini response: {response.text[:200]}...")

        # Use robust JSON extraction
        json_text = extract_json_from_response(response.text)

        # Parse JSON with more detailed error handling
        try:
            result = json.loads(json_text)
        except json.JSONDecodeError as je:
            logger.error(f"JSON decode error: {je}")
            logger.error(f"Cleaned text that failed: {json_text[:500]}")
            raise

        # Validate expected keys
        if "sentiment" not in result or "summary" not in result:
            logger.warning(f"Missing expected keys in JSON: {result.keys()}")
            raise ValueError("JSON response missing required keys")

        return {
            "sentiment": float(result["sentiment"]),
            "summary": str(result["summary"])
        }

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        logger.error(f"Response text was: {response.text[:300] if 'response' in locals() else 'No response'}")
        return {
            "sentiment": 0.0,
            "summary": f"Error: {e}"
        }
