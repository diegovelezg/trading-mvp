#!/usr/bin/env python3
"""
Investment Desk Ticker Analysis

Analiza un ticker específico incluyendo:
- Noticias relacionadas (via entity matching)
- Análisis GeoMacro
- Análisis de Sentimiento
- Evaluación de Riesgo
- Recomendación consolidada

Uso:
    python analyze_ticker.py USO
    python analyze_ticker.py AAPL --hours-back 48
"""

import sys
import os
# Fix root path and subagents path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, '.claude', 'subagents'))

import logging
from datetime import datetime
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('investment_desk.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Note: API Keys should ideally be in .env, but keeping them as they were in the script
os.environ['ALPACA_PAPER_API_KEY'] = 'YOUR_ALPACA_PAPER_API_KEY'
os.environ['PAPER_API_SECRET'] = 'YOUR_ALPACA_SECRET_KEY'
os.environ['SERPAPI_API_KEY'] = 'YOUR_SERPAPI_API_KEY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCutHRoCMkN02KhsVYATzu5XRPjboQZxnc'
os.environ['GEMINI_API_MODEL_01'] = 'gemini-3.1-flash-lite-preview'
os.environ['GEMINI_API_MODEL_02'] = 'gemini-3.1-flash-lite-preview'

from trading_mvp.core.db_geo_news import get_recent_news
from trading_mvp.core.db_geo_entities import get_recent_entities, get_entities_by_name
from watchlist_manager.agent import get_ticker_entities, get_news_for_ticker
from trading_mvp.analysis.quant_stats import fetch_historical_stats


def analyze_ticker(ticker: str, hours_back: int = 48) -> Dict:
    """Analyze a ticker with related news and insights.

    Args:
        ticker: Ticker symbol
        hours_back: Hours to look back for news

    Returns:
        Complete analysis dictionary
    """

    ticker = ticker.upper()

    logger.info("="*70)
    logger.info(f"🎯 INVESTMENT DESK ANALYSIS: {ticker}")
    logger.info("="*70)
    logger.info(f"⏰ Time window: Last {hours_back} hours")
    logger.info("")

    start_time = datetime.now()

    # 1. Get ticker's entity mapping
    logger.info(f"📋 Step 1: Getting entity mapping for {ticker}...")
    ticker_entities = get_ticker_entities(ticker)

    if not ticker_entities:
        logger.warning(f"⚠️  No entity mapping found for {ticker}")
        return {
            "ticker": ticker,
            "error": "No entity mapping found",
            "success": False
        }

    logger.info(f"  ✅ Found {len(ticker_entities)} entities: {', '.join(ticker_entities)}")

    # 2. Get related news via entity matching
    logger.info(f"📰 Step 2: Finding related news via entity matching...")
    related_news = get_news_for_ticker(ticker, hours_back=hours_back)
    logger.info(f"  ✅ Found {len(related_news)} related news items")
    logger.info("")

    # 3. Get entities mentioned in that news
    logger.info(f"🧠 Step 3: Extracting entities from related news...")
    news_entities = []

    for news in related_news[:20]:  # Limit to top 20 for performance
        news_id = news.get('id')
        if news_id:
            entities = get_entities_for_news(news_id)
            for entity in entities:
                entity['news_title'] = news.get('title', '')
                entity['news_source'] = news.get('source', '')
            news_entities.extend(entities)

    logger.info(f"  ✅ Extracted {len(news_entities)} entities from news")
    logger.info("")

    # 4. Analyze entity patterns
    logger.info(f"📊 Step 4: Analyzing entity patterns...")

    # Group by entity name
    entity_groups = {}
    for entity in news_entities:
        name = entity.get('entity_name', 'unknown')
        if name not in entity_groups:
            entity_groups[name] = []
        entity_groups[name].append(entity)

    # Calculate aggregate metrics
    entity_analysis = []
    for entity_name, entities in entity_groups.items():
        impacts = [e.get('impact', 'neutral') for e in entities]
        confidences = [e.get('confidence', 0.5) for e in entities]

        negative_count = impacts.count('negative')
        positive_count = impacts.count('positive')
        total_count = len(impacts)

        if negative_count > positive_count:
            overall_impact = 'negative'
            intensity = 'high' if negative_count >= total_count * 0.7 else 'medium'
        elif positive_count > negative_count:
            overall_impact = 'positive'
            intensity = 'high' if positive_count >= total_count * 0.7 else 'medium'
        else:
            overall_impact = 'neutral'
            intensity = 'low'

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # Collect all sectors/regions AND source news
        all_sectors = set()
        all_regions = set()
        source_news = []  # Track which news mentioned this entity

        for e in entities:
            all_sectors.update(e.get('sectors', []))
            all_regions.update(e.get('regions', []))

            # Add news source if not already tracked
            if e.get('news_title') and e.get('news_source'):
                news_entry = {
                    'title': e['news_title'],
                    'source': e['news_source']
                }

                # Avoid duplicate news entries
                if not any(sn['title'] == news_entry['title'] for sn in source_news):
                    source_news.append(news_entry)

        entity_analysis.append({
            'entity_name': entity_name,
            'mention_count': total_count,
            'overall_impact': overall_impact,
            'intensity': intensity,
            'avg_confidence': round(avg_confidence, 2),
            'related_sectors': list(all_sectors),
            'related_regions': list(all_regions),
            'source_news': source_news  # NEW: Track which news mentioned this entity
        })

    # Sort by mention count and impact
    impact_priority = {'negative': 0, 'positive': 1, 'neutral': 2}
    entity_analysis.sort(key=lambda x: (impact_priority.get(x['overall_impact'], 3), -x['mention_count']))

    logger.info(f"  ✅ Analyzed {len(entity_analysis)} unique entities")
    logger.info("")

    # 5. Generate insights
    logger.info(f"💡 Step 5: Generating investment insights...")

    # Fetch quantitative stats
    quant_stats = fetch_historical_stats(ticker)

    # Top negative entities (risks)
    top_risks = [e for e in entity_analysis if e['overall_impact'] == 'negative'][:5]

    # Top positive entities (opportunities)
    top_opportunities = [e for e in entity_analysis if e['overall_impact'] == 'positive'][:5]

    # Most mentioned entities
    most_mentioned = sorted(entity_analysis, key=lambda x: -x['mention_count'])[:5]

    # Calculate scores
    if entity_analysis:
        avg_confidence = sum(e['avg_confidence'] for e in entity_analysis) / len(entity_analysis)
        negative_ratio = len([e for e in entity_analysis if e['overall_impact'] == 'negative']) / len(entity_analysis)
        positive_ratio = len([e for e in entity_analysis if e['overall_impact'] == 'positive']) / len(entity_analysis)
    else:
        avg_confidence = 0.5
        negative_ratio = 0.0
        positive_ratio = 0.0

    # Generate recommendation
    if negative_ratio > 0.6:
        recommendation = "BEARISH"
        rationale = f"High negative sentiment ({negative_ratio:.1%} of entities). Consider reducing exposure or hedging."
    elif positive_ratio > 0.6:
        recommendation = "BULLISH"
        rationale = f"Strong positive sentiment ({positive_ratio:.1%} of entities). Favorable conditions for upside."
    elif negative_ratio > 0.4 or positive_ratio > 0.4:
        recommendation = "CAUTIOUS"
        rationale = "Mixed signals with moderate bias. Wait for clearer direction before committing."
    else:
        recommendation = "NEUTRAL"
        rationale = "No clear directional signal. Monitor for developing themes."

    # Construct evidence for dashboard
    bull_case = {
        "arguments": [f"{e['entity_name']} (intensity: {e['intensity']})" for e in top_opportunities],
        "deep_analysis": f"Analyzed {len(related_news)} news items → {len(entity_analysis)} entities identified. Positive signal: {positive_ratio:.0%} bullish entities vs {negative_ratio:.0%} bearish. Top drivers: {', '.join([e['entity_name'] for e in top_opportunities[:3]])}." if top_opportunities else f"Analyzed {len(related_news)} news items → {len(entity_analysis)} entities. No positive signals detected (0% bullish entities).",
        "evidence_chain": []  # Will be populated below
    }
    bear_case = {
        "arguments": [f"{e['entity_name']} (intensity: {e['intensity']})" for e in top_risks],
        "deep_analysis": f"Analyzed {len(related_news)} news items → {len(entity_analysis)} entities. Negative signal: {negative_ratio:.0%} bearish entities vs {positive_ratio:.0%} bullish. Key risks: {', '.join([e['entity_name'] for e in top_risks[:3]])} (all high intensity). Combined with quant signal (RSI: {quant_stats.get('rsi_14', 'N/A')}, Trend: {quant_stats.get('trend', 'N/A')}) → {recommendation} recommendation." if top_risks else f"Analyzed {len(related_news)} news items → {len(entity_analysis)} entities. No negative risks detected (0% bearish entities).",
        "evidence_chain": []  # Will be populated below
    }
    risk_analysis = {
        "stop_loss": {
            "percentage": 0.05,
            "technical_defense": "Standard variance protection based on sector volatility."
        },
        "deep_analysis": f"Risk level: {'HIGH' if negative_ratio > 0.6 else 'MEDIUM' if negative_ratio > 0.3 else 'LOW'} based on {len(top_risks)} negative entities with avg {sum([e.get('avg_confidence', 0.5) for e in top_risks]) / len(top_risks):.0%} confidence. Stop loss set at 5% to protect against {top_risks[0].get('entity_name', 'market volatility') if top_risks else 'market'} downside." if top_risks else "Risk level: LOW. Stop loss set at 5% as standard protection.",
        "evidence_chain": []  # Will be populated below
    }

    # Build evidence chain for each entity (NEWS → ENTITY trace)
    for entity in top_risks[:5]:  # Top 5 risks
        if entity.get('source_news'):
            for news in entity['source_news'][:2]:  # Max 2 news per entity
                bear_case['evidence_chain'].append({
                    'news_title': news['title'][:80] + '...' if len(news['title']) > 80 else news['title'],
                    'news_source': news['source'],
                    'entity_name': entity['entity_name'],
                    'intensity': entity['intensity'],
                    'confidence': entity['avg_confidence'],
                    'impact': entity['overall_impact']
                })

    for entity in top_opportunities[:5]:  # Top 5 opportunities
        if entity.get('source_news'):
            for news in entity['source_news'][:2]:  # Max 2 news per entity
                bull_case['evidence_chain'].append({
                    'news_title': news['title'][:80] + '...' if len(news['title']) > 80 else news['title'],
                    'news_source': news['source'],
                    'entity_name': entity['entity_name'],
                    'intensity': entity['intensity'],
                    'confidence': entity['avg_confidence'],
                    'impact': entity['overall_impact']
                })

    logger.info(f"  ✅ Generated {recommendation} recommendation")
    logger.info("")

    # 6. Compile final report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    analysis = {
        'success': True,
        'ticker': ticker,
        'analysis_timestamp': datetime.now().isoformat(),
        'time_window_hours': hours_back,
        'duration_seconds': round(duration, 1),

        # Entity mapping
        'mapped_entities': ticker_entities,

        # News summary
        'related_news_count': len(related_news),
        'news_sources': list(set(n.get('source', '') for n in related_news)),

        # Entity analysis
        'unique_entities_found': len(entity_analysis),
        'total_entity_mentions': len(news_entities),

        # Top entities
        'top_risks': top_risks,
        'top_opportunities': top_opportunities,
        'most_mentioned': most_mentioned,

        # Dashboard evidence
        'bull_case': bull_case,
        'bear_case': bear_case,
        'risk_analysis': risk_analysis,
        'quant_stats': quant_stats,

        # Scores
        'avg_confidence': round(avg_confidence, 2),
        'negative_ratio': round(negative_ratio, 2),
        'positive_ratio': round(positive_ratio, 2),

        # Recommendation
        'recommendation': recommendation,
        'rationale': rationale,

        # Related news (for reference)
        'related_news': related_news[:10]  # Top 10 for reference
    }

    logger.info("="*70)
    logger.info(f"✅ ANALYSIS COMPLETE: {recommendation}")
    logger.info(f"   Duration: {duration:.1f}s")
    logger.info(f"   News analyzed: {len(related_news)}")
    logger.info(f"   Entities found: {len(entity_analysis)}")
    logger.info("="*70)

    return analysis


def print_analysis_report(analysis: Dict):
    """Print a formatted investment desk report.

    Args:
        analysis: Analysis dictionary from analyze_ticker()
    """

    if not analysis.get('success'):
        print(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}")
        return

    ticker = analysis['ticker']
    print()
    print("="*70)
    print(f"🎯 INVESTMENT DESK REPORT: {ticker}")
    print("="*70)
    print()

    # Header
    print(f"⏰ Analysis Time: {analysis['analysis_timestamp']}")
    print(f"📊 Time Window: Last {analysis['time_window_hours']} hours")
    print(f"⚡ Duration: {analysis['duration_seconds']}s")
    print()

    # Entity Mapping
    print("🏷️  MAPPED ENTITIES:")
    for entity in analysis['mapped_entities']:
        print(f"   • {entity}")
    print()

    # News Summary
    print("📰 NEWS SUMMARY:")
    print(f"   • Related news found: {analysis['related_news_count']}")
    print(f"   • Sources: {', '.join(analysis['news_sources'])}")
    print()

    # Top News
    if analysis.get('related_news'):
        print("   TOP NEWS:")
        for i, news in enumerate(analysis['related_news'][:5], 1):
            title = news.get('title', 'N/A')[:70]
            source = news.get('source', 'N/A')
            print(f"   {i}. [{source}] {title}...")
    print()

    # Recommendation
    print(f"💡 RECOMMENDATION: {analysis['recommendation']}")
    print(f"   {analysis['rationale']}")
    print()

    # Scores
    print("📊 SENTIMENT SCORES:")
    print(f"   • Average Confidence: {analysis['avg_confidence']:.2f}")
    print(f"   • Negative Ratio: {analysis['negative_ratio']:.1%}")
    print(f"   • Positive Ratio: {analysis['positive_ratio']:.1%}")
    print()

    # Top Risks
    if analysis.get('top_risks'):
        print("⚠️  TOP RISKS:")
        for i, risk in enumerate(analysis['top_risks'][:3], 1):
            print(f"   {i}. {risk['entity_name']}")
            print(f"      Mentioned {risk['mention_count']}x | Impact: {risk['overall_impact']} ({risk['intensity']}) | Conf: {risk['avg_confidence']}")
            if risk['related_sectors']:
                print(f"      Sectors: {', '.join(risk['related_sectors'][:3])}")
        print()

    # Top Opportunities
    if analysis.get('top_opportunities'):
        print("🚀 TOP OPPORTUNITIES:")
        for i, opp in enumerate(analysis['top_opportunities'][:3], 1):
            print(f"   {i}. {opp['entity_name']}")
            print(f"      Mentioned {opp['mention_count']}x | Impact: {opp['overall_impact']} ({opp['intensity']}) | Conf: {opp['avg_confidence']}")
            if opp['related_sectors']:
                print(f"      Sectors: {', '.join(opp['related_sectors'][:3])}")
        print()

    # Most Mentioned
    if analysis.get('most_mentioned'):
        print("🔥 MOST MENTIONED:")
        for i, entity in enumerate(analysis['most_mentioned'][:5], 1):
            print(f"   {i}. {entity['entity_name']}: {entity['mention_count']} mentions")
    print()

    # Quantitative Stats
    if analysis.get('quant_stats') and not analysis['quant_stats'].get('error'):
        qs = analysis['quant_stats']
        print("📈 QUANTITATIVE SNAPSHOT:")
        print(f"   • Current Price: ${qs['current_price']:.2f}")
        print(f"   • Trend: {qs['trend']} (SMA 200: ${qs['sma_200']})")
        print(f"   • Momentum: {qs['momentum']} (SMA 50: ${qs['sma_50']})")
        print(f"   • Relative Strength (RSI 14): {qs['rsi_14']}")
        
        # RSI Interpretation
        rsi_label = "OVERBOUGHT" if qs['rsi_14'] > 70 else "OVERSOLD" if qs['rsi_14'] < 30 else "NEUTRAL"
        print(f"   • RSI Condition: {rsi_label}")
        
        print(f"   • Volatility (ATR 14): ${qs['atr_14']:.2f} ({qs['volatility_ratio']}% of price)")
        print(f"   • Market Beta (vs SPY): {qs['beta_spy']}")
        
        # Beta interpretation
        beta_desc = "High correlation" if qs['beta_spy'] > 1.2 else "Low correlation" if qs['beta_spy'] < 0.8 else "Moves with market"
        print(f"   • Correlation: {beta_desc}")
    elif analysis.get('quant_stats') and analysis['quant_stats'].get('error'):
        print(f"📈 QUANTITATIVE SNAPSHOT: ⚠️ Data unavailable ({analysis['quant_stats']['error']})")
    print()

    print("="*70)


def get_entities_for_news(news_id: int) -> List[Dict]:
    """Get entities for a news item via Supabase.

    Args:
        news_id: News ID

    Returns:
        List of entity dicts
    """

    import os
    from supabase import create_client

    # Supabase client
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ Supabase credentials not found")
        return []

    try:
        supabase = create_client(supabase_url, supabase_key)

        # Obtener entities de Supabase (tabla geo_macro_entities)
        result = supabase.table('geo_macro_entities').select('*').eq('news_id', news_id).execute()

        if result.data:
            # Formatear resultado para compatibilidad
            return result.data
        else:
            return []

    except Exception as e:
        logger.error(f"❌ Error getting entities for news {news_id}: {e}")
        return []


if __name__ == "__main__":
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python analyze_ticker.py <TICKER> [--hours-back N]")
        sys.exit(1)

    ticker_arg = sys.argv[1]
    hours_back = 48

    if len(sys.argv) > 2 and sys.argv[2] == '--hours-back':
        hours_back = int(sys.argv[3])

    # Run analysis
    result = analyze_ticker(ticker_arg, hours_back=hours_back)

    # Print report
    print_analysis_report(result)

    # Exit with error code if failed
    if not result.get('success'):
        sys.exit(1)
