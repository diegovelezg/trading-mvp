import os
import json
import logging
from typing import Dict
from dotenv import load_dotenv
from google.genai import Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

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
    
    client = Client(api_key=api_key)
    
    prompt = f"""
    Analyze the sentiment of the following financial news content.
    Provide your response in JSON format with the following keys:
    - sentiment: a float between -1 (extremely negative) and 1 (extremely positive)
    - summary: a brief summary of the news
    
    News Content:
    {text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        # Process JSON response
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()
            
        result = json.loads(clean_text)
        return {
            "sentiment": float(result.get("sentiment", 0)),
            "summary": str(result.get("summary", "No summary provided."))
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {
            "sentiment": 0.0,
            "summary": f"Error: {e}"
        }
