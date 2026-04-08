"""FRED (Federal Reserve Economic Data) connector."""

import os
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import requests

from trading_mvp.data_sources.base_connector import BaseDataConnector

logger = logging.getLogger(__name__)

class FREDConnector(BaseDataConnector):
    """Connector for Federal Reserve Economic Data (FRED)."""

    def __init__(self):
        """Initialize FRED connector."""
        super().__init__("FRED Economic Data")

        # FRED API key (free at https://fred.stlouisfed.org/docs/api/api_key.html)
        self.api_key = os.getenv("FRED_API_KEY", "")  # Optional for now

        self.base_url = "https://api.stlouisfed.org/fred"

        logger.info("✅ FRED connector initialized")

    def fetch_data(self, series_id: str) -> Dict:
        """Fetch data for a specific series.

        Args:
            series_id: FRED series ID (e.g., 'UNRATE' for unemployment rate)

        Returns:
            Series data
        """
        try:
            url = f"{self.base_url}/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": 1,  # Get only latest observation
                "sort_order": "desc"
            }

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.last_fetch = datetime.now()
                self.fetch_count += 1
                return data
            else:
                logger.warning(f"⚠️  FRED API error: {response.status_code}")
                return {}

        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error fetching FRED data: {e}")
            return {}

    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize FRED data to standard format.

        Args:
            raw_data: Raw data from FRED

        Returns:
            Normalized data items
        """
        # FRED data is already structured, so minimal normalization needed
        return raw_data

    def get_key_economic_indicators(self) -> Dict[str, Dict]:
        """Get key economic indicators from FRED.

        Returns:
            Dictionary of indicator name to latest value
        """
        key_indicators = {
            "unemployment_rate": "UNRATE",
            "interest_rate": "FEDFUNDS",
            "cpi_inflation": "CPIAUCSL",
            "gdp_growth": "A191RP1Q225SBEA",  # Real GDP
            "consumer_confidence": "UMCSENT",
            "housing_starts": "HOUST",
            "industrial_production": "IPMAN"
        }

        indicators_data = {}

        for name, series_id in key_indicators.items():
            try:
                data = self.fetch_data(series_id)

                if data and "observations" in data:
                    observations = data["observations"]
                    if observations and len(observations) > 0:
                        latest = observations[0]
                        indicators_data[name] = {
                            "value": latest.get("value"),
                            "date": latest.get("date"),
                            "series_id": series_id
                        }
                        logger.info(f"📊 {name}: {latest.get('value')} (as of {latest.get('date')})")

            except Exception as e:
                logger.warning(f"⚠️  Could not fetch {name}: {e}")

        return indicators_data

    def get_interest_rate_outlook(self) -> Dict:
        """Get current interest rate and recent changes.

        Returns:
            Interest rate data with outlook
        """
        try:
            # Get federal funds rate
            data = self.fetch_data("FEDFUNDS")

            if data and "observations" in data:
                observations = data["observations"]
                if len(observations) >= 2:
                    latest = observations[0]
                    previous = observations[1]

                    current_rate = float(latest.get("value", 0))
                    previous_rate = float(previous.get("value", 0))
                    change = current_rate - previous_rate

                    outlook = {
                        "current_rate": current_rate,
                        "previous_rate": previous_rate,
                        "change": change,
                        "date": latest.get("date"),
                        "trend": "rising" if change > 0 else "falling" if change < 0 else "stable"
                    }

                    logger.info(f"📈 Interest Rate: {current_rate}% (change: {change:+.2f}%)")

                    return outlook

        except Exception as e:
            logger.error(f"❌ Error getting interest rate outlook: {e}")

        return {}

    def get_inflation_data(self) -> Dict:
        """Get inflation data (CPI).

        Returns:
            Inflation data with trend
        """
        try:
            # Get CPI data
            data = self.fetch_data("CPIAUCSL")

            if data and "observations" in data:
                observations = data["observations"]
                if len(observations) >= 2:
                    latest = observations[0]
                    previous = observations[1]

                    # Calculate year-over-year change
                    current_cpi = float(latest.get("value", 0))
                    previous_cpi = float(previous.get("value", 0))
                    yoy_change = ((current_cpi - previous_cpi) / previous_cpi) * 100

                    inflation = {
                        "current_cpi": current_cpi,
                        "yoy_change_percent": yoy_change,
                        "date": latest.get("date"),
                        "trend": "rising" if yoy_change > 3 else "stable" if yoy_change > 1 else "falling"
                    }

                    logger.info(f"📊 Inflation (YoY): {yoy_change:.2f}%")

                    return inflation

        except Exception as e:
            logger.error(f"❌ Error getting inflation data: {e}")

        return {}

    def format_for_insights(self) -> str:
        """Format economic indicators for inclusion in insights.

        Returns:
            Formatted string with key indicators
        """
        indicators = self.get_key_economic_indicators()
        interest_outlook = self.get_interest_rate_outlook()
        inflation_data = self.get_inflation_data()

        output = ["## ECONOMIC INDICATORS (FRED) ##\n"]

        if interest_outlook:
            output.append(f"Interest Rates: {interest_outlook['current_rate']}% ({interest_outlook['trend']})")

        if inflation_data:
            output.append(f"Inflation: {inflation_data['yoy_change_percent']:.2f}% YoY ({inflation_data['trend']})")

        for name, data in indicators.items():
            if data and "value" in data:
                formatted_name = name.replace("_", " ").title()
                output.append(f"{formatted_name}: {data['value']} (as of {data['date']})")

        return "\n".join(output)
