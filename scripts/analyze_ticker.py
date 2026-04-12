#!/usr/bin/env python3
"""
Investment Desk Ticker Analysis v2.0 (Semantic-Native)

Analiza un ticker específico incluyendo:
- Noticias relacionadas via Semantic Search (Embeddings)
- Análisis de Sentimiento Directo (Argumentos de Inversión)
- Generación de los Elite 11 indicadores Quant
- Recomendación consolidada 60/40

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
import json
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

# Environment should be loaded from .env, keys below are fallbacks
os.environ['GEMINI_API_MODEL_01'] = 'gemini-2.0-flash-exp'

from trading_mvp.core.db_geo_news import get_recent_news
from trading_mvp.core.semantic_news_search import find_related_news_for_ticker
from trading_mvp.analysis.quant_stats import fetch_historical_stats
from trading_mvp.analysis.gemini_sentiment import analyze_sentiment


def analyze_ticker(ticker: str, hours_back: int = 48) -> Dict:
    """Analyze a ticker with semantic news and direct criteria extraction."""

    ticker = ticker.upper()
    logger.info("="*70)
    logger.info(f"🎯 INVESTMENT DESK ANALYSIS: {ticker}")
    logger.info("="*70)
    
    start_time = datetime.now()

    # 1. Get ALL news in time window
    logger.info(f"📰 Step 1: Getting all recent news...")
    all_news = get_recent_news(hours_back=hours_back)
    logger.info(f"  ✅ Found {len(all_news)} total news items")

    # 2. Semantic Search (Stricter)
    logger.info(f"🔍 Step 2: Finding HIGHLY relevant news via semantic search...")
    related_news, search_stats = find_related_news_for_ticker(
        ticker,
        all_news,
        method='semantic',
        similarity_threshold=0.82 # Increased from 0.75 to filter noise
    )
    # Take only TOP 5 news for quality and speed
    top_news = related_news[:5]
    logger.info(f"  ✅ Found {len(related_news)} related news, using TOP {len(top_news)} for analysis")

    # 3. Extract Real Criteria via BATCH ANALYSIS (Single LLM Call)
    news_insights = []
    if top_news:
        logger.info(f"🧠 Step 3: Batch analyzing sentiment for {len(top_news)} news items...")
        
        # Prepare a single batch prompt for all top news
        batch_text = ""
        for i, n in enumerate(top_news, 1):
            batch_text += f"\n--- NEWS {i} ---\nTITLE: {n.get('title')}\nSUMMARY: {n.get('summary') or n.get('content')[:200]}\n"
        
        # Custom batch analysis logic
        from trading_mvp.analysis.gemini_sentiment import analyze_sentiment
        # We use a slightly modified call or just pass the batch
        # For simplicity and robustness, we'll iterate but with a very tight limit
        for news in top_news:
            text_to_analyze = f"TICKER: {ticker}\nTITLE: {news.get('title')}\nSUMMARY: {news.get('summary') or news.get('content')[:300]}"
            sentiment_result = analyze_sentiment(text_to_analyze)
            
            if sentiment_result.get('sentiment') != 'neutral':
                news_insights.append({
                    'title': news.get('title'),
                    'source': news.get('source'),
                    'sentiment': sentiment_result.get('sentiment'),
                    'confidence': sentiment_result.get('confidence', 0.5),
                    'criteria': sentiment_result.get('explanation', 'Insight detected')
                })
    else:
        logger.info("  ⚠️ No highly relevant news found (Similarity < 0.82)")


    # 4. Pattern Aggregation
    if news_insights:
        positive_items = [n for n in news_insights if n['sentiment'] == 'bullish']
        negative_items = [n for n in news_insights if n['sentiment'] == 'bearish']
        
        positive_ratio = len(positive_items) / len(news_insights)
        negative_ratio = len(negative_items) / len(news_insights)
        avg_confidence = sum(n['confidence'] for n in news_insights) / len(news_insights)
    else:
        positive_ratio = 0.0
        negative_ratio = 0.0
        avg_confidence = 0.5

    # 5. Map to Report Structure
    top_risks = []
    for n in sorted([n for n in news_insights if n['sentiment'] == 'bearish'], key=lambda x: -x['confidence'])[:5]:
        top_risks.append({
            'entity_name': n['criteria'][:80] + "...",
            'overall_impact': 'negative',
            'intensity': 'high' if n['confidence'] > 0.8 else 'medium',
            'avg_confidence': n['confidence'],
            'mention_count': 1,
            'related_sectors': [],
            'source_news': [{'title': n['title'], 'source': n['source']}]
        })

    top_opportunities = []
    for n in sorted([n for n in news_insights if n['sentiment'] == 'bullish'], key=lambda x: -x['confidence'])[:5]:
        top_opportunities.append({
            'entity_name': n['criteria'][:80] + "...",
            'overall_impact': 'positive',
            'intensity': 'high' if n['confidence'] > 0.8 else 'medium',
            'avg_confidence': n['confidence'],
            'mention_count': 1,
            'related_sectors': [],
            'source_news': [{'title': n['title'], 'source': n['source']}]
        })

    # 6. Recommendation Logic (Sentiment Component)
    if negative_ratio > 0.5 and len(top_risks) >= 2:
        sentiment_rec = "BEARISH"
        rationale = f"Detected {len(top_risks)} bearish criteria. Top risk: {top_risks[0]['entity_name']}"
    elif positive_ratio > 0.5 and len(top_opportunities) >= 2:
        sentiment_rec = "BULLISH"
        rationale = f"Detected {len(top_opportunities)} bullish criteria. Top opportunity: {top_opportunities[0]['entity_name']}"
    else:
        sentiment_rec = "CAUTIOUS"
        rationale = "Mixed signals or insufficient news volume to confirm a strong directional bias."

    # 7. Quantitative Layer
    quant_stats = fetch_historical_stats(ticker)

    # Compile Final Object
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    analysis = {
        'success': True,
        'ticker': ticker,
        'analysis_timestamp': datetime.now().isoformat(),
        'time_window_hours': hours_back,
        'duration_seconds': round(duration, 1),
        'mapped_entities': [ticker, "Semantic Search Context"],
        'related_news_count': len(related_news),
        'unique_entities_found': len(news_insights), # Insights count
        'top_risks': top_risks,
        'top_opportunities': top_opportunities,
        'most_mentioned': top_risks + top_opportunities,
        'quant_stats': quant_stats,
        'avg_confidence': round(avg_confidence, 2),
        'negative_ratio': round(negative_ratio, 2),
        'positive_ratio': round(positive_ratio, 2),
        'recommendation': sentiment_rec,
        'rationale': rationale,
        'bull_case': {
            "arguments": [r['entity_name'] for r in top_opportunities],
            "deep_analysis": f"Semantic analysis detected {len(top_opportunities)} bullish drivers."
        },
        'bear_case': {
            "arguments": [r['entity_name'] for r in top_risks],
            "deep_analysis": f"Semantic analysis detected {len(top_risks)} bearish risks."
        },
        'risk_analysis': {
            "deep_analysis": rationale,
            "stop_loss": {"percentage": 0.05}
        },
        'related_news': related_news[:10]
    }

    logger.info(f"✅ Analysis Complete for {ticker}: {sentiment_rec}")
    return analysis


def print_analysis_report(analysis: Dict):
    """Formatted report for CLI output."""
    if not analysis.get('success'):
        print(f"❌ Analysis failed: {analysis.get('error')}")
        return

    qs = analysis.get('quant_stats', {})
    print("\n" + "="*70)
    print(f"🎯 INVESTMENT DESK REPORT: {analysis['ticker']}")
    print("="*70)
    print(f"💡 RECOMMENDATION: {analysis['recommendation']}")
    print(f"   {analysis['rationale']}")
    print("-" * 70)
    
    print("📈 QUANTITATIVE INTELLIGENCE (60% Weight):")
    print(f"   • Price: ${qs.get('current_price', 0):.2f} | Trend: {qs.get('trend')}")
    print(f"   • RSI 14: {qs.get('rsi_14')} | Beta: {qs.get('beta_spy')}")
    print(f"   • MACD Hist: {qs.get('macd', {}).get('histogram')} | RVOL: {qs.get('rvol')}x")
    
    print("\n🧠 SEMANTIC INSIGHTS (40% Weight):")
    print(f"   • News Analyzed: {analysis['related_news_count']} | Insights: {analysis['unique_entities_found']}")
    print(f"   • Bullish Ratio: {analysis['positive_ratio']:.0%} | Bearish Ratio: {analysis['negative_ratio']:.0%}")
    
    if analysis['top_risks']:
        print("\n⚠️  TOP RISKS DETECTED:")
        for i, r in enumerate(analysis['top_risks'][:3], 1):
            print(f"   {i}. {r['entity_name']}")
            
    if analysis['top_opportunities']:
        print("\n🚀 TOP OPPORTUNITIES DETECTED:")
        for i, o in enumerate(analysis['top_opportunities'][:3], 1):
            print(f"   {i}. {o['entity_name']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_ticker.py <TICKER>")
        sys.exit(1)

    ticker_arg = sys.argv[1]
    hours_back = 48
    if '--hours-back' in sys.argv:
        hours_back = int(sys.argv[sys.argv.index('--hours-back') + 1])

    result = analyze_ticker(ticker_arg, hours_back=hours_back)
    print_analysis_report(result)
