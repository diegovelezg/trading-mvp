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

def analyze_sentiment(text: str) -> Dict:
    """
    Analyzes the sentiment of a text using Gemini 2.0 Flash.
    
    Args:
        text: The news content to analyze.
        
    Returns:
        A dictionary with 'sentiment' (float -1 to 1) and 'summary' (str).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required in environment variables.")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    logger.info(f"Using model: {model}")

    client = Client(api_key=api_key)
    
    prompt = f"""
    Analyze the sentiment of the following financial news content.
    Provide your response STRICTLY in JSON format with these exact keys:
    - "sentiment": a float between -1 (extremely negative) and 1 (extremely positive)
    - "summary": a brief summary of the news

    IMPORTANT: Return ONLY the JSON object, no additional text, no markdown formatting.

    News Content:
    {text}

    Example format:
    {{"sentiment": 0.5, "summary": "Brief description here"}}
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
