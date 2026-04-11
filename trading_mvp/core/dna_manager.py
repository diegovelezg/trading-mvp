"""DNA Manager: The SSOT (Single Source of Truth) for Asset DNA."""

import os
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from google.genai import Client
from trading_mvp.core.db_manager import get_connection

logger = logging.getLogger(__name__)

# Memoria de Experto (Pre-definida para evitar alucinaciones en activos críticos)
EXPERT_DNA = {
    "USO": {
        "asset_type": "Energy Commodity (Oil)",
        "core_drivers": ["OPEC+ Supply", "Global Demand", "Geopolitical Tension", "Inventory Levels"],
        "bullish_catalysts": ["War in Middle East", "Supply Chain Disruption", "Economic Recovery"],
        "bearish_catalysts": ["Global Recession", "Increased Non-OPEC Supply", "Geopolitical De-escalation"],
        "geopolitical_sensitivity": 0.9,
        "interest_rate_sensitivity": 0.3
    },
    "TLT": {
        "asset_type": "Long-Duration Bond ETF (20+ Years)",
        "core_drivers": ["Long-term Interest Rates", "Inflation Expectations", "Fed Policy"],
        "bullish_catalysts": ["Disinflation", "Fed Rate Cuts", "Flight to Quality (Recession)"],
        "bearish_catalysts": ["Sticky Inflation", "Fed Rate Hikes", "Large Fiscal Deficits"],
        "geopolitical_sensitivity": 0.4,
        "interest_rate_sensitivity": 1.0
    },
    "GLD": {
        "asset_type": "Precious Metal (Gold)",
        "core_drivers": ["Real Interest Rates", "US Dollar (DXY)", "Systemic Risk"],
        "bullish_catalysts": ["Geopolitical Chaos", "Dollar Weakness", "Falling Real Yields"],
        "bearish_catalysts": ["Rising Real Rates", "Strong Dollar", "Stability/Peace"],
        "geopolitical_sensitivity": 0.8,
        "interest_rate_sensitivity": 0.7
    },
    "NVDA": {
        "asset_type": "Hyper-Growth Semi/AI",
        "core_drivers": ["AI Infrastructure Spend", "Chip Supply", "Discount Rates"],
        "bullish_catalysts": ["AI Adoption Surge", "Strong Earnings", "Low Interest Rates"],
        "bearish_catalysts": ["Export Bans", "Reduced Tech Capex", "High Interest Rates (PE Compression)"],
        "geopolitical_sensitivity": 0.6,
        "interest_rate_sensitivity": 0.8
    }
}

class DNAManager:
    """Manages asset DNA identification and persistence."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_API_MODEL_02", "gemini-2.0-flash")

    def get_dna(self, ticker: str) -> Dict:
        """Retrieves asset DNA from DB, Expert Memory, or Gemini."""
        ticker = ticker.upper()

        # 1. Check DB first
        db_dna = self._get_from_db(ticker)
        if db_dna:
            logger.info(f"🧬 DNA for {ticker} loaded from DB")
            return db_dna

        # 2. Check Expert Memory
        if ticker in EXPERT_DNA:
            logger.info(f"🧬 DNA for {ticker} loaded from Expert Memory")
            dna = EXPERT_DNA[ticker]
            self._save_to_db(ticker, dna)
            return dna

        # 3. Ask Gemini as fallback
        logger.info(f"🧬 DNA for {ticker} unknown. Generating with AI...")
        dna = self._generate_with_ai(ticker)
        if dna:
            self._save_to_db(ticker, dna)
            return dna

        return {}

    def _get_from_db(self, ticker: str) -> Optional[Dict]:
        """Fetch DNA from Postgres."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT asset_type, core_drivers, bullish_catalysts, bearish_catalysts, geopolitical_sensitivity, interest_rate_sensitivity FROM asset_dna WHERE ticker = %s", (ticker,))
                row = cursor.fetchone()
                if row:
                    return {
                        "asset_type": row[0],
                        "core_drivers": row[1],
                        "bullish_catalysts": row[2],
                        "bearish_catalysts": row[3],
                        "geopolitical_sensitivity": row[4],
                        "interest_rate_sensitivity": row[5]
                    }
        except Exception as e:
            logger.error(f"Error fetching DNA from DB: {e}")
        finally:
            conn.close()
        return None

    def _save_to_db(self, ticker: str, dna: Dict):
        """Save DNA to Postgres."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO asset_dna (ticker, asset_type, core_drivers, bullish_catalysts, bearish_catalysts, geopolitical_sensitivity, interest_rate_sensitivity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker) DO UPDATE SET
                        asset_type = EXCLUDED.asset_type,
                        core_drivers = EXCLUDED.core_drivers,
                        bullish_catalysts = EXCLUDED.bullish_catalysts,
                        bearish_catalysts = EXCLUDED.bearish_catalysts,
                        geopolitical_sensitivity = EXCLUDED.geopolitical_sensitivity,
                        interest_rate_sensitivity = EXCLUDED.interest_rate_sensitivity,
                        last_updated = CURRENT_TIMESTAMP
                """, (
                    ticker, 
                    dna['asset_type'], 
                    dna['core_drivers'], 
                    dna['bullish_catalysts'], 
                    dna['bearish_catalysts'],
                    dna.get('geopolitical_sensitivity', 0.5),
                    dna.get('interest_rate_sensitivity', 0.5)
                ))
        except Exception as e:
            logger.error(f"Error saving DNA to DB: {e}")
        finally:
            conn.close()

    def _generate_with_ai(self, ticker: str) -> Dict:
        """Use Gemini to profile an unknown asset."""
        if not self.api_key:
            return {}

        client = Client(api_key=self.api_key)
        prompt = f"""
        Analyze the asset DNA for {ticker}. 
        Provide a detailed profile in JSON format with these keys:
        - "asset_type": Precise classification (e.g., Small-Cap Biotech, Bond ETF, Defensive Value Stock)
        - "core_drivers": List of 4-5 main factors moving its price
        - "bullish_catalysts": Situations that RAISE its price based on its nature
        - "bearish_catalysts": Situations that LOWER its price based on its nature
        - "geopolitical_sensitivity": Float 0.0 to 1.0
        - "interest_rate_sensitivity": Float 0.0 to 1.0

        IMPORTANT: Distinguish between general 'bad news' and 'asset-specific' catalysts.
        Return ONLY valid JSON.
        """

        try:
            response = client.models.generate_content(model=self.model, contents=prompt)
            clean_text = response.text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Error generating DNA with AI: {e}")
            return {}
