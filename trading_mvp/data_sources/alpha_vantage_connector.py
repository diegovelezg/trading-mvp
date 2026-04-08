"""Alpha Vantage connector for commodity prices."""

import os
import logging
from typing import List, Dict
from datetime import datetime, timedelta
import requests

from trading_mvp.data_sources.base_connector import BaseDataConnector

logger = logging.getLogger(__name__)

class AlphaVantageConnector(BaseDataConnector):
    """Connector for Alpha Vantage API (commodities, FX, etc.)."""

    def __init__(self):
        """Initialize Alpha Vantage connector."""
        super().__init__("Alpha Vantage")

        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")  # Get free key at https://www.alphavantage.co/support/#api-key
        self.base_url = "https://www.alphavantage.co/query"

        if not self.api_key:
            logger.warning("⚠️  ALPHA_VANTAGE_API_KEY not found in environment variables")

        logger.info("✅ Alpha Vantage connector initialized")

    def fetch_data(self, function: str, symbol: str, **kwargs) -> Dict:
        """Fetch data from Alpha Vantage.

        Args:
            function: API function (e.g., 'COMMODITY_EXCHANGE_RATE')
            symbol: Symbol to fetch
            **kwargs: Additional parameters

        Returns:
            API response data
        """
        try:
            if not self.api_key:
                logger.warning("⚠️  No Alpha Vantage API key available")
                return {}

            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key,
                **kwargs
            }

            logger.info(f"📊 Fetching {function} for {symbol}...")

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            self.last_fetch = datetime.now()
            self.fetch_count += 1

            # Check for API error messages
            if "Error Message" in data or "Note" in data:
                logger.warning(f"⚠️  Alpha Vantage API limit reached or error: {data}")
                return {}

            return data

        except requests.exceptions.RequestException as e:
            self.error_count += 1
            logger.error(f"❌ Error fetching Alpha Vantage data: {e}")
            return {}

    def normalize_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Normalize Alpha Vantage data to standard format.

        Args:
            raw_data: Raw data from Alpha Vantage

        Returns:
            Normalized data items
        """
        return raw_data

    def get_commodity_price(self, symbol: str) -> Dict:
        """Get current commodity price.

        Args:
            symbol: Commodity symbol (e.g., 'WTI', 'BRENT', 'GOLD')

        Returns:
            Price data
        """
        try:
            data = self.fetch_data("COMMODITY_EXCHANGE_RATE", symbol=symbol)

            if data and "data" in data:
                price_data = data["data"][0]  # Most recent

                price_info = {
                    "symbol": symbol,
                    "price": float(price_data.get("value", 0)),
                    "date": price_data.get("date"),
                    "unit": price_data.get("unit", "USD")
                }

                logger.info(f"🛢️  {symbol}: ${price_info['price']}")

                return price_info

        except Exception as e:
            logger.error(f"❌ Error getting commodity price for {symbol}: {e}")

        return {}

    def get_key_commodities(self) -> Dict[str, Dict]:
        """Get prices for key commodities.

        Returns:
            Dictionary of commodity name to price data
        """
        commodities = {
            "wti_crude_oil": "WTI",
            "brent_crude_oil": "BRENT",
            "natural_gas": "NG",
            "gold": "GOLD",
            "silver": "SILVER",
            "copper": "COPPER"
        }

        commodity_prices = {}

        for name, symbol in commodities.items():
            try:
                price_data = self.get_commodity_price(symbol)
                if price_data:
                    commodity_prices[name] = price_data
            except Exception as e:
                logger.warning(f"⚠️  Could not fetch {name}: {e}")

        return commodity_prices

    def get_oil_prices(self) -> Dict:
        """Get current oil prices (WTI and Brent).

        Returns:
            Oil price data with trends
        """
        try:
            wti = self.get_commodity_price("WTI")
            brent = self.get_commodity_price("BRENT")

            oil_data = {
                "wti": wti,
                "brent": brent,
                "spread": None,
                "trend": None
            }

            if wti and brent:
                oil_data["spread"] = brent["price"] - wti["price"]

                # Simple trend analysis (would need historical data for real trend)
                if wti["price"] > 80:
                    oil_data["trend"] = "high"
                elif wti["price"] > 60:
                    oil_data["trend"] = "elevated"
                else:
                    oil_data["trend"] = "normal"

                logger.info(f"🛢️  WTI: ${wti['price']}, BRENT: ${brent['price']}, Spread: ${oil_data['spread']:.2f}")

            return oil_data

        except Exception as e:
            logger.error(f"❌ Error getting oil prices: {e}")
            return {}

    def format_for_insights(self) -> str:
        """Format commodity prices for inclusion in insights.

        Returns:
            Formatted string with commodity prices
        """
        commodities = self.get_key_commodities()

        output = ["## COMMODITY PRICES ##\n"]

        for name, data in commodities.items():
            if data and "price" in data:
                formatted_name = name.replace("_", " ").title()
                output.append(f"{formatted_name}: ${data['price']}")

        return "\n".join(output)
