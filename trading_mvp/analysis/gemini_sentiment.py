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
    """Robustly extracts JSON from Gemini response, handling various formats."""
    # Remove markdown code blocks if present
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Remove control characters that often break JSON parsing
    text = "".join(ch for n, ch in enumerate(text) if unicodedata.category(ch)[0] != 'C' or ch in '\n\r\t')
    
    clean_text = text.strip()

    # Find the first { and last }
    start = clean_text.find('{')
    end = clean_text.rfind('}')
    
    if start != -1 and end != -1:
        return clean_text[start:end+1]
    
    return clean_text

import unicodedata

def analyze_sentiment(text: str, ticker: str = "Unknown", dna: Dict = None) -> Dict:
    """
    Analyzes the sentiment of a text using Gemini 2.0 Flash with Asset DNA context.
    Returns a normalized dictionary with both float and label sentiment.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required in environment variables.")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    client = Client(api_key=api_key)
    
    prompt = f"""
    Analyze sentiment for {ticker}.
    
    Provide response STRICTLY in JSON:
    - "sentiment": float between -1.0 and 1.0
    - "summary": short impact summary
    - "explanation": 1 sentence reasoning
    
    Text: {text}
    """
    
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        json_text = extract_json_from_response(response.text)
        
        # Aggressive cleaning for illegal commas or characters
        json_text = re.sub(r',\s*\}', '}', json_text) # Remove trailing commas
        json_text = re.sub(r',\s*\]', ']', json_text)
        
        result = json.loads(json_text)
        
        score = float(result.get("sentiment", 0))
        
        # Map score to label
        if score >= 0.25: label = "bullish"
        elif score <= -0.25: label = "bearish"
        else: label = "neutral"

        return {
            "sentiment": label,
            "sentiment_score": score,
            "confidence": 0.8, # Default confidence for Flash
            "explanation": result.get("explanation", result.get("summary", "No details")),
            "summary": result.get("summary", "No summary")
        }

    except Exception as e:
        logger.error(f"Sentiment Analysis Error for {ticker}: {e}")
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "confidence": 0.5,
            "explanation": f"Analysis failed: {str(e)}",
            "summary": "N/A"
        }
