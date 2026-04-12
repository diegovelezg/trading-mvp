"""Entity extraction from news using Gemini AI."""

import os
import json
import logging
import re
from typing import List, Dict, Optional
from google.genai import Client
from dotenv import load_dotenv

# FORZAR SSOT
load_dotenv(override=True)
logger = logging.getLogger(__name__)

class EntityExtractor:
    """Extract investment entities from news using Gemini AI."""

    def __init__(self):
        """Initialize entity extractor."""
        # Recargar para asegurar que tenemos la última clave
        load_dotenv(override=True)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.model = os.getenv("GEMINI_API_MODEL_01", "gemini-3.1-flash-lite-preview")
        self.client = Client(api_key=api_key)

        logger.info(f"✅ EntityExtractor initialized with model: {self.model} (API Key ends in: ...{api_key[-4:]})")

    def extract_json_from_response(self, text: str) -> str:
        """Extract JSON from Gemini response."""
        clean_text = text.strip()

        # Try regex for JSON object
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, clean_text, re.DOTALL)

        if matches:
            return max(matches, key=len)

        # Remove code blocks
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:]

        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]

        return clean_text.strip()

    def extract_entities(self, news: Dict) -> List[Dict]:
        """Extract entities from a single news item (WITHOUT tickers).

        Args:
            news: Normalized news item

        Returns:
            List of extracted entities (themes, commodities, sectors, regions, events, policies)
        """
        prompt = f"""
Extract the key investment entities from this news item:

Title: {news.get('title', '')}
Summary: {news.get('summary', '')}

Identify:
1. ENTITIES (themes/commodities/regions/events/policies/sectors/indicators affected)
2. ENTITY_TYPE (theme/commodity/region/event/policy/sector/indicator)
3. IMPACT (positive/negative/neutral) on investments
4. CONFIDENCE (0.0-1.0) in this assessment
5. SECTORS (specific sectors affected)
6. REGIONS (countries/regions affected)

DO NOT include specific ticker symbols. Focus on macro-level entities only.

Respond in strict JSON:
{{
  "entities": [
    {{
      "entity_name": "Oil",
      "entity_type": "commodity",
      "impact": "positive",
      "confidence": 0.9,
      "sectors": ["Energy", "Transportation"],
      "regions": ["Middle East"]
    }}
  ]
}}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            response_text = response.text.strip()
            json_str = self.extract_json_from_response(response_text)
            result = json.loads(json_str)

            entities = result.get("entities", [])
            logger.info(f"✅ Extracted {len(entities)} entities from news")
            return entities

        except Exception as e:
            logger.warning(f"⚠️  Could not extract entities: {e}")
            return []

    def extract_entities_batch(self, news_list: List[Dict]) -> Dict[int, List[Dict]]:
        """Extract entities from multiple news items.

        Args:
            news_list: List of normalized news items

        Returns:
            Dictionary mapping news_id to list of entities
        """
        all_entities = {}

        for news in news_list:
            news_id = news.get('id') or news.get('alpaca_id')
            entities = self.extract_entities(news)
            all_entities[news_id] = entities

        logger.info(f"✅ Extracted entities from {len(news_list)} news items")
        return all_entities

    def get_entity_type_distribution(self, entities: List[Dict]) -> Dict[str, int]:
        """Get distribution of entity types.

        Args:
            entities: List of entities

        Returns:
            Dictionary with counts per entity type
        """
        distribution = {}
        for entity in entities:
            entity_type = entity.get('entity_type', 'unknown')
            distribution[entity_type] = distribution.get(entity_type, 0) + 1

        return distribution

    def get_top_entities(self, entities: List[Dict], top_n: int = 10) -> List[tuple]:
        """Get most frequently mentioned entities.

        Args:
            entities: List of entities
            top_n: Number of top entities to return

        Returns:
            List of (entity_name, count) tuples
        """
        entity_counts = {}
        for entity in entities:
            name = entity.get('entity_name', 'unknown')
            entity_counts[name] = entity_counts.get(name, 0) + 1

        return sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]


def extract_entities_from_news(news: Dict) -> List[Dict]:
    """Convenience function to extract entities from a news item.

    Args:
        news: Normalized news item

    Returns:
        List of extracted entities
    """
    extractor = EntityExtractor()
    return extractor.extract_entities(news)


def extract_entities_batch(news_list: List[Dict]) -> Dict[int, List[Dict]]:
    """Convenience function to extract entities from multiple news items.

    Args:
        news_list: List of normalized news items

    Returns:
        Dictionary mapping news_id to list of entities
    """
    extractor = EntityExtractor()
    return extractor.extract_entities_batch(news_list)
