"""GeoMacro Analyst: Global Geopolitical & Macro Intelligence Agent."""

import os
import sys
import json
import logging
import argparse
from typing import List, Dict
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from dotenv import load_dotenv
from google.genai import Client
from trading_mvp.core.db_geo_macro import (
    create_geo_macro_tables,
    insert_geo_macro_insight,
    get_insight_summary,
    get_critical_insights,
    get_recent_insights
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Event type classification
EVENT_TYPES = [
    "geopolitical",
    "economic",
    "commodity",
    "crisis",
    "technological",
    "regulatory",
    "market_structure"
]

# Importance levels
IMPORTANCE_LEVELS = ["critical", "high", "medium", "low"]

# Time horizons
TIME_HORIZONS = ["immediate", "short", "medium", "long"]

class GeoMacroAnalyst:
    """Global Geopolitical & Macro Intelligence Analyst."""

    def __init__(self):
        """Initialize GeoMacro Analyst."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        self.model = os.getenv("GEMINI_API_MODEL_04", "gemini-3.1-pro-preview")
        logger.info(f"🌍 GeoMacro Analyst initialized with model: {self.model}")

        self.client = Client(api_key=api_key)

        # Initialize database
        create_geo_macro_tables()

    def collect_global_intelligence(self, session_type: str = "ad-hoc") -> List[Dict]:
        """Collect global intelligence from multiple sources.

        Args:
            session_type: Type of session (morning, afternoon, ad-hoc)

        Returns:
            List of collected intelligence items
        """
        logger.info(f"🔍 Collecting global intelligence - Session: {session_type}")

        # Simulated data collection (in production, integrate real APIs)
        intelligence_sources = self._fetch_from_sources()

        logger.info(f"📊 Collected {len(intelligence_sources)} raw intelligence items")

        return intelligence_sources

    def _fetch_from_sources(self) -> List[Dict]:
        """Fetch intelligence from REAL data sources.

        Integrates:
        - Alpaca News API (real-time)
        - Google News RSS (global news)
        - FRED (economic indicators)
        - Alpha Vantage (commodity prices)
        """
        all_intelligence = []

        # 1. Fetch from Alpaca News API (Macro & Geopolitical)
        try:
            from trading_mvp.data_sources.alpaca_news_connector import AlpacaNewsConnector

            alpaca = AlpacaNewsConnector()

            # Get macro news from Alpaca
            macro_news = alpaca.fetch_macro_news(hours_back=24)
            all_intelligence.extend([{
                "source": "alpaca_news",
                "content_type": "macro_news",
                "data": item
            } for item in macro_news])

            # Get commodity news from Alpaca
            commodity_news = alpaca.fetch_commodity_news(hours_back=24)
            all_intelligence.extend([{
                "source": "alpaca_news",
                "content_type": "commodity_news",
                "data": item
            } for item in commodity_news])

        except Exception as e:
            logger.error(f"❌ Error fetching from Alpaca: {e}")

        # 2. Fetch from Google News RSS (Geopolitical)
        try:
            from trading_mvp.data_sources.google_news_connector import GoogleNewsConnector

            google_news = GoogleNewsConnector()

            # Get geopolitical news
            geo_news = google_news.fetch_geopolitical_news(max_items=30)
            all_intelligence.extend([{
                "source": "google_news",
                "content_type": "geopolitical_news",
                "data": item
            } for item in geo_news])

            # Get economic news
            econ_news = google_news.fetch_economic_news(max_items=20)
            all_intelligence.extend([{
                "source": "google_news",
                "content_type": "economic_news",
                "data": item
            } for item in econ_news])

            # Get trade policy news
            trade_news = google_news.fetch_trade_policy_news(max_items=20)
            all_intelligence.extend([{
                "source": "google_news",
                "content_type": "trade_news",
                "data": item
            } for item in trade_news])

            # Get regulatory news
            reg_news = google_news.fetch_regulatory_news(max_items=20)
            all_intelligence.extend([{
                "source": "google_news",
                "content_type": "regulatory_news",
                "data": item
            } for item in reg_news])

        except Exception as e:
            logger.error(f"❌ Error fetching from Google News: {e}")

        # 3. Fetch Economic Indicators from FRED
        try:
            from trading_mvp.data_sources.fred_connector import FREDConnector

            fred = FREDConnector()

            # Get key economic indicators
            indicators = fred.get_key_economic_indicators()
            all_intelligence.append({
                "source": "fred",
                "content_type": "economic_indicators",
                "data": indicators
            })

            # Get interest rate outlook
            interest_outlook = fred.get_interest_rate_outlook()
            all_intelligence.append({
                "source": "fred",
                "content_type": "interest_rate_outlook",
                "data": interest_outlook
            })

            # Get inflation data
            inflation = fred.get_inflation_data()
            all_intelligence.append({
                "source": "fred",
                "content_type": "inflation_data",
                "data": inflation
            })

        except Exception as e:
            logger.error(f"❌ Error fetching from FRED: {e}")

        # 4. Fetch Commodity Prices from Alpha Vantage
        try:
            from trading_mvp.data_sources.alpha_vantage_connector import AlphaVantageConnector

            alpha_vantage = AlphaVantageConnector()

            # Get oil prices
            oil_prices = alpha_vantage.get_oil_prices()
            all_intelligence.append({
                "source": "alpha_vantage",
                "content_type": "commodity_prices",
                "data": oil_prices
            })

            # Get key commodities
            commodities = alpha_vantage.get_key_commodities()
            all_intelligence.append({
                "source": "alpha_vantage",
                "content_type": "commodity_prices_detail",
                "data": commodities
            })

        except Exception as e:
            logger.error(f"❌ Error fetching from Alpha Vantage: {e}")

        logger.info(f"📊 Total intelligence items collected: {len(all_intelligence)}")

        return all_intelligence

    def analyze_and_generate_insights(self, raw_intelligence: List[Dict], session_type: str = "ad-hoc") -> List[Dict]:
        """Analyze raw intelligence and generate structured insights.

        Args:
            raw_intelligence: List of raw intelligence items
            session_type: Type of session

        Returns:
            List of structured insights
        """
        logger.info("🧠 Analyzing REAL intelligence and generating insights...")

        # Use Gemini for advanced analysis with REAL data
        insights = self._generate_insights_with_gemini(raw_intelligence, session_type)

        logger.info(f"✅ Generated {len(insights)} structured insights from REAL data")

        return insights

    def _generate_insights_with_gemini(self, raw_intelligence: List[Dict], session_type: str) -> List[Dict]:
        """Generate insights using Gemini AI from REAL data sources.

        Args:
            raw_intelligence: List of raw intelligence items from various sources
            session_type: Type of session

        Returns:
            List of structured insights
        """
        # Format intelligence for prompt
        formatted_intel = self._format_intelligence_for_prompt(raw_intelligence)

        prompt = f"""
        You are an elite geopolitical and macroeconomic intelligence analyst. Your task is to analyze the following REAL-TIME global intelligence from multiple sources and extract actionable investment insights.

        REAL-TIME INTELLIGENCE:
        {formatted_intel}

        TASK: Analyze this intelligence and identify 5-10 most significant events/developments. Generate structured insights for each.

        For each insight, provide:
        1. **event_type**: One of {EVENT_TYPES}
        2. **importance**: One of {IMPORTANCE_LEVELS}
        3. **title**: Brief but descriptive title
        4. **summary**: 1-2 sentence summary based on the ACTUAL data
        5. **impact_analysis**: Detailed analysis of potential market impact
        6. **affected_sectors**: List of affected sectors (max 5)
        7. **affected_regions**: List of affected regions/countries (max 5)
        8. **affected_tickers**: Specific tickers likely affected (max 10)
        9. **time_horizon**: One of {TIME_HORIZONS}
        10. **confidence_score**: Float 0-1 indicating confidence in analysis
        11. **tags**: List of relevant tags for search

        CRITICAL REQUIREMENTS:
        - Base insights ONLY on the provided intelligence data
        - DO NOT invent or imagine events
        - If insufficient data for high-confidence insights, reduce importance or omit
        - Cross-reference multiple sources when available
        - Explicitly mention data sources in impact analysis

        OUTPUT FORMAT: Valid JSON array of insights.

        Example:
        [
          {{
            "event_type": "geopolitical",
            "importance": "critical",
            "title": "China announces new EV subsidies",
            "summary": "China's government unveils $10B in subsidies for domestic EV manufacturers (Source: Alpaca News)",
            "impact_analysis": "Major boost for Chinese EV makers, pressure on global competitors. Based on real-time data from Alpaca News API. Impact: +20% for Chinese EV stocks, -5% for foreign competitors.",
            "affected_sectors": ["electric_vehicles", "automotive", "technology"],
            "affected_regions": ["China", "US", "Europe"],
            "affected_tickers": ["BYD", "NIO", "XPEV", "TSLA"],
            "time_horizon": "immediate",
            "confidence_score": 0.9,
            "tags": ["EV", "subsidies", "China", "automotive"]
          }}
        ]

        IMPORTANT: Return ONLY valid JSON array, no additional text.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            # Parse JSON response
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3].strip()

            insights = json.loads(clean_text)

            # Add session type and sources to each insight
            for insight in insights:
                insight['session_type'] = session_type
                insight['data_sources'] = list(set([item['source'] for item in raw_intelligence]))

            return insights

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []

    def _format_intelligence_for_prompt(self, raw_intelligence: List[Dict]) -> str:
        """Format raw intelligence for prompt inclusion.

        Args:
            raw_intelligence: List of intelligence items

        Returns:
            Formatted string
        """
        sections = []

        # Group by content type
        by_type = {}
        for item in raw_intelligence:
            content_type = item.get('content_type', 'unknown')
            if content_type not in by_type:
                by_type[content_type] = []
            by_type[content_type].append(item)

        # Format each section
        for content_type, items in by_type.items():
            sections.append(f"\n## {content_type.upper().replace('_', ' ')} ##")

            for item in items[:20]:  # Limit to 20 items per type
                source = item.get('source', 'unknown')
                data = item.get('data', {})

                if content_type in ['macro_news', 'geopolitical_news', 'economic_news', 'trade_news', 'regulatory_news']:
                    # News items
                    title = data.get('title', data.get('headline', ''))
                    summary = data.get('summary', '')
                    sections.append(f"[{source}] {title}: {summary[:200]}...")

                elif content_type == 'economic_indicators':
                    # Economic indicators
                    for name, values in data.items():
                        if isinstance(values, dict) and 'value' in values:
                            sections.append(f"{name}: {values['value']} (as of {values.get('date', 'N/A')})")

                elif content_type in ['interest_rate_outlook', 'inflation_data']:
                    # Economic outlook
                    for key, value in data.items():
                        sections.append(f"{key}: {value}")

                elif content_type == 'commodity_prices':
                    # Commodity prices
                    if 'wti' in data and 'brent' in data:
                        sections.append(f"WTI: ${data['wti'].get('price', 'N/A')}, BRENT: ${data['brent'].get('price', 'N/A')}")

        return "\n".join(sections)

    def save_insights(self, insights: List[Dict]) -> List[int]:
        """Save insights to database.

        Args:
            insights: List of insight dictionaries

        Returns:
            List of insight IDs
        """
        logger.info(f"💾 Saving {len(insights)} insights to database...")

        insight_ids = []
        for insight in insights:
            try:
                insight_id = insert_geo_macro_insight(insight)
                insight_ids.append(insight_id)
                logger.info(f"  ✅ Saved insight #{insight_id}: {insight['title'][:50]}...")
            except Exception as e:
                logger.error(f"  ❌ Error saving insight: {e}")

        return insight_ids

    def generate_executive_summary(self, hours: int = 24) -> str:
        """Generate executive summary of recent insights.

        Args:
            hours: Hours to look back

        Returns:
            Formatted executive summary
        """
        summary_data = get_insight_summary(hours=hours)

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              🌍 GEOMACRO INTELLIGENCE BRIEFING                             ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 OVERVIEW (Last {hours} hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Insights: {summary_data['total_insights']}

By Importance:
"""

        for imp, count in summary_data['by_importance'].items():
            report += f"  • {imp.upper()}: {count}\n"

        report += "\nBy Event Type:\n"
        for event_type, count in summary_data['by_event_type'].items():
            report += f"  • {event_type}: {count}\n"

        # Critical insights
        if summary_data['critical_insights']:
            report += "\n🚨 CRITICAL INSIGHTS\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for insight in summary_data['critical_insights']:
                report += f"\n📍 {insight['title']}\n"
                report += f"   Type: {insight['event_type']} | Horizon: {insight['time_horizon']}\n"
                report += f"   Impact: {insight['impact_analysis'][:200]}...\n"

        # High importance insights
        if summary_data['high_insights']:
            report += "\n⚠️  HIGH IMPORTANCE\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            for insight in summary_data['high_insights']:
                report += f"\n📍 {insight['title']}\n"
                report += f"   {insight['summary']}\n"

        report += "\n" + "═"*80 + "\n"

        return report

    def run_daily_session(self, session_type: str = "morning") -> Dict:
        """Run a complete daily analysis session.

        Args:
            session_type: Type of session (morning, afternoon)

        Returns:
            Session results dictionary
        """
        logger.info(f"🚀 Starting GeoMacro {session_type} session...")

        # Step 1: Collect intelligence
        raw_intelligence = self.collect_global_intelligence(session_type)

        # Step 2: Analyze and generate insights
        insights = self.analyze_and_generate_insights(raw_intelligence, session_type)

        # Step 3: Save to database
        insight_ids = self.save_insights(insights)

        # Step 4: Generate executive summary
        summary = self.generate_executive_summary()

        results = {
            "session_type": session_type,
            "timestamp": datetime.now().isoformat(),
            "insights_generated": len(insights),
            "insights_saved": len(insight_ids),
            "insight_ids": insight_ids,
            "summary": summary
        }

        logger.info(f"✅ Session complete: {len(insights)} insights generated and saved")

        return results

def main():
    """Main entry point for GeoMacro Analyst CLI."""
    parser = argparse.ArgumentParser(
        description="GeoMacro Analyst - Global Geopolitical & Macro Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run morning briefing session
  python agent.py --session morning

  # Run afternoon update session
  python agent.py --session afternoon

  # Run ad-hoc analysis
  python agent.py --session ad-hoc

  # Show recent insights summary
  python agent.py --summary

  # Show only critical insights
  python agent.py --critical
        """
    )

    parser.add_argument("--session", type=str, choices=["morning", "afternoon", "ad-hoc"],
                       default="ad-hoc", help="Type of session to run")
    parser.add_argument("--summary", action="store_true", help="Show recent insights summary")
    parser.add_argument("--critical", action="store_true", help="Show only critical insights")

    args = parser.parse_args()

    analyst = GeoMacroAnalyst()

    if args.summary:
        # Show summary
        summary = analyst.generate_executive_summary()
        print(summary)
    elif args.critical:
        # Show critical insights
        critical = get_critical_insights(hours=24)
        print(f"\n🚨 CRITICAL INSIGHTS (Last 24 hours)\n")
        for insight in critical:
            print(f"\n📍 {insight['title']}")
            print(f"   Type: {insight['event_type']} | Horizon: {insight['time_horizon']}")
            print(f"   {insight['impact_analysis']}")
    else:
        # Run analysis session
        results = analyst.run_daily_session(args.session)
        print(results['summary'])

if __name__ == "__main__":
    main()
