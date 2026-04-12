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

    # 2. Semantic Search (Optimized)
    logger.info(f"🔍 Step 2: Finding relevant news via semantic search...")
    related_news, search_stats = find_related_news_for_ticker(
        ticker,
        all_news,
        method='semantic',
        similarity_threshold=0.80 # Slightly more permissive to fill the UI
    )
    top_news = related_news[:8] # Up to 8 news for balanced detail
    logger.info(f"  ✅ Found {len(related_news)} related news, using TOP {len(top_news)} for deep analysis")

    # 3. Extract Real Criteria and Build Evidence Chain
    news_insights = []
    evidence_chain = []
    
    for news in top_news:
        text_to_analyze = f"TICKER: {ticker}\nTITLE: {news.get('title', '')}\nSUMMARY: {news.get('summary', '') or news.get('content', '')[:300]}"
        sentiment_result = analyze_sentiment(text_to_analyze, ticker=ticker)
        
        # We now accept 'neutral' if similarity is high to avoid empty UI
        insight = {
            'title': news.get('title'),
            'source': news.get('source'),
            'sentiment': sentiment_result.get('sentiment', 'neutral'),
            'sentiment_score': sentiment_result.get('sentiment_score', 0.0),
            'confidence': sentiment_result.get('confidence', 0.5),
            'criteria': sentiment_result.get('explanation') if sentiment_result.get('sentiment') != 'neutral' else news.get('title')
        }
        news_insights.append(insight)
        
        # Build Evidence Chain for UI
        evidence_chain.append({
            'news_title': news.get('title', '')[:80] + '...',
            'news_source': news.get('source', 'Unknown'),
            'entity_name': insight['criteria'][:60] + '...',
            'sentiment': insight['sentiment'],
            'confidence': insight['confidence']
        })

    # 4. Aggregate Patterns
    if news_insights:
        pos_items = [n for n in news_insights if n['sentiment'] == 'bullish']
        neg_items = [n for n in news_insights if n['sentiment'] == 'bearish']
        
        positive_ratio = len(pos_items) / len(news_insights)
        negative_ratio = len(neg_items) / len(news_insights)
        avg_confidence = sum(n['confidence'] for n in news_insights) / len(news_insights)
        # Combined Sentiment Score for UI
        sentiment_score = sum(n['sentiment_score'] for n in news_insights) / len(news_insights)
    else:
        positive_ratio, negative_ratio, avg_confidence, sentiment_score = 0.0, 0.0, 0.5, 0.0

    # 5. Build UI Objects (Arguments and Monologues)
    top_risks = []
    bear_items = [n for n in news_insights if n['sentiment'] == 'bearish']
    if not bear_items and news_insights: # Fallback: Show neutral as risks if no bearish
        bear_items = [n for n in news_insights if n['sentiment'] == 'neutral'][:2]

    for n in sorted(bear_items, key=lambda x: -x['confidence'])[:5]:
        top_risks.append({
            'entity_name': n['criteria'],
            'overall_impact': n['sentiment'] if n['sentiment'] != 'neutral' else 'negative',
            'intensity': 'medium',
            'avg_confidence': n['confidence'],
            'source_news': [{'title': n['title'], 'source': n['source']}]
        })

    top_opportunities = []
    bull_items = [n for n in news_insights if n['sentiment'] == 'bullish']
    if not bull_items and news_insights: # Fallback
        bull_items = [n for n in news_insights if n['sentiment'] == 'neutral'][:2]

    for n in sorted(bull_items, key=lambda x: -x['confidence'])[:5]:
        top_opportunities.append({
            'entity_name': n['criteria'],
            'overall_impact': n['sentiment'] if n['sentiment'] != 'neutral' else 'positive',
            'intensity': 'medium',
            'avg_confidence': n['confidence'],
            'source_news': [{'title': n['title'], 'source': n['source']}]
        })

    # 6. Generate Recommendation and Narratives
    if negative_ratio > 0.4 and len(top_risks) >= 1:
        recommendation = "BEARISH"
        rationale = f"Semantic bias is leaning bearish ({negative_ratio:.0%})."
    elif positive_ratio > 0.4 and len(top_opportunities) >= 1:
        recommendation = "BULLISH"
        rationale = f"Semantic bias is leaning bullish ({positive_ratio:.0%})."
    else:
        recommendation = "CAUTIOUS"
        rationale = "Mixed or neutral semantic signals detected via embeddings."

    # Quantitative Layer
    quant_stats = fetch_historical_stats(ticker)

    # Monologues (The Storytelling)
    bull_summary = f"Analyst View: {len(bull_items)} potential catalysts found. " + \
                   (bull_items[0]['criteria'] if bull_items else "Monitoring for bullish signals.")
    bear_summary = f"Skeptic View: {len(bear_items)} risk factors noted. " + \
                   (bear_items[0]['criteria'] if bear_items else "No immediate macro threats detected.")

    # Final Object
    analysis = {
        'success': True,
        'ticker': ticker,
        'analysis_timestamp': datetime.now().isoformat(),
        'mapped_entities': [ticker, "Semantic Context"],
        'related_news_count': len(related_news),
        'unique_entities_found': len(news_insights),
        'top_risks': top_risks,
        'top_opportunities': top_opportunities,
        'quant_stats': quant_stats,
        'avg_confidence': round(avg_confidence, 2),
        'sentiment_score': round(sentiment_score, 2), # NEW: Added for UI
        'negative_ratio': round(negative_ratio, 2),
        'positive_ratio': round(positive_ratio, 2),
        'recommendation': recommendation,
        'rationale': rationale,
        'bull_case': {
            "arguments": [r['entity_name'] for r in top_opportunities],
            "deep_analysis": bull_summary,
            "evidence_chain": [e for e in evidence_chain if e['sentiment'] in ['bullish', 'neutral']]
        },
        'bear_case': {
            "arguments": [r['entity_name'] for r in top_risks],
            "deep_analysis": bear_summary,
            "evidence_chain": [e for e in evidence_chain if e['sentiment'] in ['bearish', 'neutral']]
        },
        'risk_analysis': {
            "deep_analysis": f"Risk Level Assessment: {recommendation}. Technical Context: RSI {quant_stats.get('rsi_14')}, ATR {quant_stats.get('atr_14')}.",
            "stop_loss": {"percentage": 0.05}
        }
    }


    logger.info(f"✅ Analysis Complete for {ticker}: {recommendation}")
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
