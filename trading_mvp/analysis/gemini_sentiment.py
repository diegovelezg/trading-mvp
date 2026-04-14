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
    Analyzes the sentiment of a text using Gemini 2.0 Flash with Institutional Asset DNA context.
    Returns a normalized dictionary with impact mapping to core drivers.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required in environment variables.")

    model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")
    client = Client(api_key=api_key)
    
    # Construct Institutional Context from DNA
    dna_context = ""
    if dna:
        dna_context = f"""
        ASSET CONTEXT (DNA):
        - Type: {dna.get('asset_type', 'N/A')}
        - Core Drivers: {', '.join(dna.get('core_drivers', [])) if isinstance(dna.get('core_drivers'), list) else dna.get('core_drivers', 'N/A')}
        - Bullish Catalysts: {', '.join(dna.get('bullish_catalysts', [])) if isinstance(dna.get('bullish_catalysts'), list) else dna.get('bullish_catalysts', 'N/A')}
        - Bearish Catalysts: {', '.join(dna.get('bearish_catalysts', [])) if isinstance(dna.get('bearish_catalysts'), list) else dna.get('bearish_catalysts', 'N/A')}
        """

    prompt = f"""
    You are a Senior Institutional Analyst specializing in {ticker}.
    {dna_context}
    
    TASK: Analyze the following text and determine its impact on {ticker} based on its specific DNA.
    
    TEXT TO ANALYZE:
    {text}
    
    REQUIRED RESPONSE FORMAT (JSON ONLY):
    {{
        "sentiment": float (-1.0 to 1.0),
        "impact_label": "bullish" | "bearish" | "neutral",
        "dna_alignment": "Which specific core driver or catalyst from the DNA is being triggered?",
        "summary": "Short impact summary in Spanish",
        "explanation": "1 sentence technical reasoning in Spanish",
        "confidence": float (0.0 to 1.0)
    }}
    
    Rules:
    1. If the text triggers a 'Bullish Catalyst' from the DNA, sentiment must be > 0.4.
    2. If the text triggers a 'Bearish Catalyst' from the DNA, sentiment must be < -0.4.
    3. Be objective. If the news is irrelevant to the core drivers, stay neutral.
    4. Respond ONLY with the JSON object.
    """
    
    try:
        response = client.models.generate_content(model=model, contents=prompt)
        json_text = extract_json_from_response(response.text)
        
        # Aggressive cleaning
        json_text = re.sub(r',\s*\}', '}', json_text)
        json_text = re.sub(r',\s*\]', ']', json_text)
        
        result = json.loads(json_text)
        
        score = float(result.get("sentiment", 0))
        label = result.get("impact_label", "neutral")
        
        # Ensure label matches score if inconsistent
        if score >= 0.25: label = "bullish"
        elif score <= -0.25: label = "bearish"
        else: label = "neutral"

        return {
            "sentiment": label,
            "sentiment_score": score,
            "confidence": float(result.get("confidence", 0.8)),
            "explanation": result.get("explanation", "No details"),
            "summary": result.get("summary", "No summary"),
            "dna_alignment": result.get("dna_alignment", "N/A")
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
