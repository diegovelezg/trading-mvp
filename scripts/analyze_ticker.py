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
from trading_mvp.core.dna_manager import DNAManager


def analyze_ticker(ticker: str, hours_back: int = 48, portfolio_position: Dict = None) -> Dict:
    """Analyze a ticker with semantic news and direct criteria extraction."""

    ticker = ticker.upper()
    logger.info("="*70)
    logger.info(f"🎯 INVESTMENT DESK ANALYSIS: {ticker}")
    logger.info("="*70)
    
    start_time = datetime.now()

    # 0. PRE-EMPTIVE QUANTITATIVE CHECK & MECHANICAL EXITS
    quant_stats = fetch_historical_stats(ticker)
    
    # DATA INTEGRITY CHECK: QUANT
    quant_valid = bool(quant_stats and 'error' not in quant_stats and quant_stats.get('current_price'))
    if not quant_valid:
        logger.error(f"⚠️  DATA INTEGRITY ALERT: Missing or invalid Quant stats for {ticker}.")
        return {
            'success': True,
            'ticker': ticker,
            'is_actionable': False,
            'recommendation': "DATA_ERROR",
            'rationale': f"ABORTED: {quant_stats.get('error', 'Quant data failure')}. Risk management impossible.",
            'quant_stats': quant_stats,
            'avg_confidence': 0.0,
            'positive_ratio': 0.0,
            'negative_ratio': 0.0,
            'related_news_count': 0,
            'unique_entities_found': 0,
            'analysis_timestamp': datetime.now().isoformat()
        }

    # Check Mechanical Exits (Stop Loss / Take Profit)
    if portfolio_position:
        entry_price = float(portfolio_position.get('avg_entry_price', 0))
        current_price = float(quant_stats.get('current_price', 0))
        atr = quant_stats.get('atr_14', 0)
        
        if atr > 0 and entry_price > 0:
            stop_loss = entry_price - (1.5 * atr)
            take_profit = entry_price + (3.0 * atr)
            
            if current_price <= stop_loss or current_price >= take_profit:
                action = "STOP_LOSS" if current_price <= stop_loss else "TAKE_PROFIT"
                reason = f"Current: ${current_price:.2f} <= Stop: ${stop_loss:.2f}" if action == "STOP_LOSS" else f"Current: ${current_price:.2f} >= Target: ${take_profit:.2f}"
                logger.warning(f"   🚨 MECHANICAL {action} TRIGGERED for {ticker}! Aborting heavy analysis. {reason}")
                
                return {
                    'success': True,
                    'ticker': ticker,
                    'is_actionable': True,
                    'is_mechanical_exit': True,
                    'mechanical_reason': action,
                    'recommendation': 'BEARISH', # We want the agent to sell
                    'rationale': f"MECHANICAL {action} TRIGGERED. {reason}",
                    'quant_stats': quant_stats,
                    'avg_confidence': 1.0, # Max confidence for mechanical exit
                    'positive_ratio': 0.0,
                    'negative_ratio': 1.0,
                    'related_news_count': 0,
                    'unique_entities_found': 0,
                    'analysis_timestamp': datetime.now().isoformat()
                }

    # 1. Load Asset DNA (Institutional Context)
    dna_manager = DNAManager()
    dna = dna_manager.get_dna(ticker)
    
    # DATA INTEGRITY CHECK: DNA
    dna_valid = bool(dna and dna.get('asset_type') and dna.get('embedding'))
    if dna_valid:
        logger.info(f"🧬 DNA Loaded: {dna.get('asset_type', 'Generic Asset')}")
    else:
        logger.warning(f"⚠️  DATA INTEGRITY ALERT: Missing DNA for {ticker}. Semantic search will be compromised.")

    # 1. Get ALL news in time window
    logger.info(f"📰 Step 1: Getting all recent news...")
    all_news = get_recent_news(hours_back=hours_back)
    logger.info(f"  ✅ Found {len(all_news)} total news items")

    # 2. Semantic Search (Optimized)
    related_news = []
    search_stats = {}
    if dna_valid:
        logger.info(f"🔍 Step 2: Finding relevant news via semantic search...")
        related_news, search_stats = find_related_news_for_ticker(
            ticker,
            all_news,
            method='semantic',
            similarity_threshold=0.75,
            hours_back=hours_back
        )
    
    top_news = related_news[:8]
    logger.info(f"  ✅ Found {len(related_news)} related news, using TOP {len(top_news)} for deep analysis")

    # 3. Extract Real Criteria and Build Evidence Chain
    news_insights = []
    evidence_chain = []
    
    # Only analyze sentiment if we have DNA and news
    if dna_valid and top_news:
        for news in top_news:
            text_to_analyze = f"TICKER: {ticker}\nTITLE: {news.get('title', '')}\nSUMMARY: {news.get('summary', '') or news.get('content', '')[:300]}"
            sentiment_result = analyze_sentiment(text_to_analyze, ticker=ticker, dna=dna)
            
            insight = {
                'title': news.get('title'),
                'source': news.get('source'),
                'sentiment': sentiment_result.get('sentiment', 'neutral'),
                'sentiment_score': sentiment_result.get('sentiment_score', 0.0),
                'confidence': sentiment_result.get('confidence', 0.5),
                'category': sentiment_result.get('category', 'sector'),
                'criteria': sentiment_result.get('explanation') if sentiment_result.get('sentiment') != 'neutral' else news.get('title'),
                'dna_alignment': sentiment_result.get('dna_alignment', 'N/A'),
                'published_at': news.get('published_at')
            }
            news_insights.append(insight)
            
            evidence_chain.append({
                'news_title': news.get('title', '')[:80] + '...',
                'news_source': news.get('source', 'Unknown'),
                'insight_text': insight['criteria'][:60] + '...',
                'sentiment': insight['sentiment'],
                'confidence': insight['confidence'],
                'dna_alignment': insight['dna_alignment'],
                'published_at': insight['published_at']
            })

    # 4. Aggregate Patterns (INSTITUTIONAL QUANT LOGIC)
    import math

    sentiment_variance = 0.0
    if news_insights:
        pos_items = [n for n in news_insights if n['sentiment'] == 'bullish']
        neg_items = [n for n in news_insights if n['sentiment'] == 'bearish']

        news_count = len(news_insights)
        
        # INSTITUTIONAL NLP SHOCK AGGREGATION: DNA SENSITIVITY MATRIX + BAYESIAN DECAY
        weighted_confidence_sum = 0.0
        
        tier_1 = ['reuters', 'bloomberg', 'wsj', 'sec', 'financial times', 'barrons']
        tier_2 = ['cnbc', 'yahoo', 'marketwatch', 'benzinga', 'investors business daily']

        # Half-life for news decay (3 days is institutional standard for news memory)
        half_life_days = 3.0
        decay_constant = math.log(2) / half_life_days

        # Sensitivity defaults
        geo_sens = float(dna.get('geopolitical_sensitivity', 0.5)) if dna else 0.5
        rate_sens = float(dna.get('interest_rate_sensitivity', 0.5)) if dna else 0.5
        sector_sens = 1.0 # Base sensitivity for sector news
        
        # Accumulators per category
        category_impact = {'macro': 0.0, 'geopolitical': 0.0, 'sector': 0.0}

        for n in news_insights:
            # 1. The LLM Sentiment (-1.0 to 1.0)
            base_sentiment = n['sentiment_score']
            
            # 2. DNA Relevance (Confidence from LLM prompt, 0.0 to 1.0)
            dna_relevance = n['confidence']
            
            # 3. Source Authority
            source_str = str(n.get('source', '')).lower()
            if any(t in source_str for t in tier_1):
                source_authority = 1.0
            elif any(t in source_str for t in tier_2):
                source_authority = 0.6
            else:
                source_authority = 0.2
            
            # 4. BAYESIAN DECAY (Based on news age)
            pub_date = n.get('published_at')
            decay_factor = 1.0
            if pub_date:
                try:
                    if isinstance(pub_date, str):
                        pub_dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    else:
                        pub_dt = pub_date
                    
                    if pub_dt.tzinfo is None:
                        from datetime import timezone
                        pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                    
                    now_dt = datetime.now(pub_dt.tzinfo)
                    delta_days = (now_dt - pub_dt).total_seconds() / 86400.0
                    
                    if delta_days > 0:
                        decay_factor = math.exp(-decay_constant * delta_days)
                except Exception as e:
                    logger.debug(f"Could not calculate decay for news: {e}")
                
            # 5. DNA Sensitivity Multiplier based on Category
            cat = n.get('category', 'sector').lower()
            if cat == 'macro':
                sens_mult = rate_sens * 2.0  # Scale 0.5 default to 1.0
            elif cat == 'geopolitical':
                sens_mult = geo_sens * 2.0   # Scale 0.5 default to 1.0
            else:
                sens_mult = sector_sens
                cat = 'sector'
                
            # Individual weighted impact (Decayed & Scaled by Sensitivity)
            impact = base_sentiment * dna_relevance * source_authority * decay_factor * sens_mult
            
            category_impact[cat] += impact
            weighted_confidence_sum += (dna_relevance * decay_factor)

        # 6. CAP IMPACT PER CATEGORY to prevent volume saturation (e.g. max +/- 1.5 per category before tanh)
        capped_total_impact = 0.0
        for cat, impact in category_impact.items():
            # Apply a soft cap per category: math.tanh(impact/1.5) * 1.5 limits each category to +/- 1.5
            capped_cat_impact = math.tanh(impact / 1.5) * 1.5
            capped_total_impact += capped_cat_impact

        # 7. FINAL SATURATION (math.tanh limits extremes to -1.0 to 1.0)
        sentiment_score = math.tanh(capped_total_impact)
        
        # Calculate Average Confidence (Weighted by decay)
        avg_confidence = weighted_confidence_sum / news_count if news_count > 0 else 0.5
        avg_confidence = min(1.0, avg_confidence)

        # Ratios
        positive_ratio = len(pos_items) / news_count
        negative_ratio = len(neg_items) / news_count

        # Calculate sentiment variance to detect dispersion
        if len(news_insights) > 1:
            mean_score = sum(n['sentiment_score'] for n in news_insights) / news_count
            variance = sum((n['sentiment_score'] - mean_score) ** 2 for n in news_insights) / (news_count - 1)
            sentiment_variance = variance

        logger.info(f"   📐 DNA Matrix: Macro {category_impact['macro']:+.2f} | Geo {category_impact['geopolitical']:+.2f} | Sec {category_impact['sector']:+.2f} -> FINAL SHOCK: {sentiment_score:+.3f}")
    else:
        positive_ratio, negative_ratio, avg_confidence, sentiment_score = 0.0, 0.0, 0.5, 0.0

    # 5. Build UI Objects (Arguments and Monologues)

    top_risks = []
    top_opportunities = []
    # (Simplified for the replace call context)
    for n in sorted([n for n in news_insights if n['sentiment'] == 'bearish'], key=lambda x: -x['confidence'])[:5]:
        top_risks.append({'insight_text': n['criteria'], 'overall_impact': n['sentiment'], 'intensity': 'medium', 'avg_confidence': n['confidence']})
    for n in sorted([n for n in news_insights if n['sentiment'] == 'bullish'], key=lambda x: -x['confidence'])[:5]:
        top_opportunities.append({'insight_text': n['criteria'], 'overall_impact': n['sentiment'], 'intensity': 'medium', 'avg_confidence': n['confidence']})

    # 6. Generate Recommendation and Narratives
    is_high_volatility = sentiment_variance > 0.3
    if not dna_valid:
        recommendation = "DATA_ERROR"
        rationale = "ABORTED: Missing Asset DNA. Actionable analysis impossible."
    elif is_high_volatility and negative_ratio > 0.0 and positive_ratio > 0.0:
        recommendation = "HIGH_VOLATILITY"
        rationale = f"Se detectaron noticias altamente polarizadas (Varianza: {sentiment_variance:.2f})."
    elif sentiment_score > 0.10:
        recommendation = "BULLISH"
        rationale = f"La Matriz de ADN arrojó un shock fundamental alcista ({sentiment_score:+.2f})."
    elif sentiment_score < -0.10:
        recommendation = "BEARISH"
        rationale = f"La Matriz de ADN arrojó un shock fundamental bajista ({sentiment_score:+.2f})."
    else:
        recommendation = "CAUTIOUS"
        rationale = f"Ruido de mercado sin choque fundamental significativo ({sentiment_score:+.2f})."

    # Quantitative Layer (Already fetched at the beginning)

    # Monologues (The Storytelling)
    analysis = {
        'success': True,
        'ticker': ticker,
        'is_actionable': dna_valid and quant_valid,
        'data_integrity': {
            'dna_valid': dna_valid,
            'quant_valid': quant_valid,
            'news_valid': len(related_news) > 0 or not dna_valid # news valid if we found some, or we skip if no dna
        },
        'analysis_timestamp': datetime.now().isoformat(),
        'semantic_context': [ticker, "Semantic Search via DNA"],
        'related_news_count': len(related_news),
        'unique_entities_found': len(news_insights),
        'top_risks': top_risks,
        'top_opportunities': top_opportunities,
        'quant_stats': quant_stats,
        'avg_confidence': round(avg_confidence, 2),
        'sentiment_score': round(sentiment_score, 2),
        'negative_ratio': round(negative_ratio, 2),
        'positive_ratio': round(positive_ratio, 2),
        'recommendation': recommendation,
        'rationale': rationale,
        'bull_case': {"arguments": [r['insight_text'] for r in top_opportunities]},
        'bear_case': {"arguments": [r['insight_text'] for r in top_risks]}
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
            print(f"   {i}. {r['insight_text']}")

    if analysis['top_opportunities']:
        print("\n🚀 TOP OPPORTUNITIES DETECTED:")
        for i, o in enumerate(analysis['top_opportunities'][:3], 1):
            print(f"   {i}. {o['insight_text']}")
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
