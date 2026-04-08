"""CIO (Chief Investment Officer): Strategic decisions using Elite Quant Metrics."""

import os
import sys
import json
import logging
from typing import Dict, List
from dotenv import load_dotenv
import openai # Using OpenAI client for compatibility with Z.AI

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from trading_mvp.core.portfolio_logic import validate_trade_size, get_portfolio_health

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def make_investment_decision(
    tickers_analysis: List[Dict],
    portfolio_state: Dict,
    portfolio_metrics: Dict = None,
    strategy_metrics: Dict = None,
    macro_context: str = "Neutral"
) -> Dict:
    """Make a final investment decision as a CIO using GLM-5.1 and ELITE QUANT METRICS."""
    
    api_key = os.getenv("ZAI_API_KEY")
    model_name = os.getenv("ZAI_API_MODEL_01", "glm-5.1")

    if not api_key:
        logger.error("❌ ZAI_API_KEY is missing.")
        return {"selected_ticker": "NONE", "action": "WAIT", "rationale": "Missing ZAI_API_KEY"}

    # Initialize OpenAI-compatible client for Z.AI (Coding Plan)
    client = openai.OpenAI(api_key=api_key, base_url="https://api.z.ai/api/coding/paas/v4")

    # Prepare analysis summary
    analysis_summary = []
    for analysis in tickers_analysis:
        ticker = analysis.get('ticker')
        quant = analysis.get('quant_stats', {})
        analysis_summary.append({
            "ticker": ticker,
            "sentiment_score": analysis.get('sentiment_score', 0.0),
            "quant_metrics": {
                "trend": quant.get('trend'),
                "rsi_14": quant.get('rsi_14'),
                "beta_spy": quant.get('beta_spy'),
                "volatility_ratio_pct": quant.get('volatility_ratio')
            },
            "bull_case": analysis.get('bull_case', {}).get('overall_sentiment', 'N/A'),
            "bear_case": analysis.get('bear_case', {}).get('overall_sentiment', 'N/A'),
            "risk_score": analysis.get('risk_analysis', {}).get('risk_score', 'N/A'),
            "recommended_size_usd": analysis.get('requested_capital', 1000.0)
        })

    prompt = f"""
    You are the Chief Investment Officer (CIO) of an elite autonomous trading desk. 
    You are powered by GLM-5.1, optimized for strategic synthesis.

    YOUR SYSTEM PERFORMANCE (SELF-AWARENESS):
    - Sharpe Ratio: {portfolio_metrics.get('sharpe_ratio', 'N/A')} (Risk-adjusted skill)
    - Sortino Ratio: {portfolio_metrics.get('sortino_ratio', 'N/A')} (Downside protection)
    - Calmar Ratio: {portfolio_metrics.get('calmar_ratio', 'N/A')} (Return vs Drawdown)
    - Value at Risk (VaR 95%): {portfolio_metrics.get('var_95_daily', 'N/A')}%
    - Win Rate: {strategy_metrics.get('win_rate', 'N/A')}% (Consistency)
    - Gain-to-Pain Ratio: {strategy_metrics.get('gain_to_pain', 'N/A')} (Efficiency)
    - Ulcer Index: {portfolio_metrics.get('ulcer_index', 'N/A')} (Stress level)

    PORTFOLIO STATE:
    - Total Equity: ${portfolio_state.get('equity', 0):,.2f}
    - Available Cash: ${portfolio_state.get('cash', 0):,.2f}
    - Exposure: {portfolio_state.get('total_exposure_pct', 0)*100:.1f}%

    CANDIDATES ANALYSIS:
    {json.dumps(analysis_summary, indent=2)}

    STRATEGIC MANDATE:
    1. ANALYZE SYSTEM HEALTH: If Sharpe/Calmar are high, you have a "Hot Hand"; you can be more aggressive. If Ulcer Index or Max Drawdown is high, be defensive.
    2. OPTIMIZE SELECTION: Choose the ticker that maximizes Alpha while keeping Beta controlled.
    3. POSITION SIZING: Adjust size based on VaR and your Gain-to-Pain efficiency.

    OUTPUT FORMAT (JSON):
    {{
        "selected_ticker": "TICKER or NONE",
        "action": "BUY or WAIT",
        "target_size_usd": 1500.0,
        "conviction_score": 1-10,
        "rationale": "High-level strategic reasoning connecting System Health (Sharpe/Win Rate) with Candidate Analysis",
        "prioritization_list": [
            {{"ticker": "TICKER", "rank": 1, "score": 0.0-10.0}}
        ]
    }}
    """

    try:
        logger.info(f"🧠 CIO (GLM-5.1) is analyzing system health and candidates...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional CIO with institutional-grade self-awareness and quant skills."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        decision = json.loads(response.choices[0].message.content.strip())
        
        # Guardrail check
        if decision.get('selected_ticker') != "NONE" and decision.get('action') == "BUY":
            ticker = decision['selected_ticker']
            target_size = float(decision.get('target_size_usd', 0))
            is_valid, allowed_size, reason = validate_trade_size(ticker, target_size)
            if not is_valid or allowed_size <= 0:
                decision['action'] = "WAIT"
            elif allowed_size < target_size:
                decision['target_size_usd'] = allowed_size
        
        return decision

    except Exception as e:
        logger.error(f"❌ Error in CIO decision: {e}")
        return {"selected_ticker": "NONE", "action": "WAIT", "rationale": f"CIO System Error: {str(e)}"}
