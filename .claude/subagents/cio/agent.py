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
from trading_mvp.core.dna_manager import DNAManager

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
    """Make a final investment decision as a CIO using GLM-5.1 and ASSET DNA VALIDATION."""
    
    api_key = os.getenv("ZAI_API_KEY")
    model_name = os.getenv("ZAI_API_MODEL_01", "glm-5.1")
    
    dna_manager = DNAManager()

    if not api_key:
        logger.error("❌ ZAI_API_KEY is missing.")
        return {"selected_ticker": "NONE", "action": "WAIT", "rationale": "Missing ZAI_API_KEY"}

    # Initialize OpenAI-compatible client for Z.AI
    client = openai.OpenAI(api_key=api_key, base_url="https://api.z.ai/api/coding/paas/v4")

    # Prepare analysis summary with DNA integration
    analysis_summary = []
    for analysis in tickers_analysis:
        ticker = analysis.get('ticker')
        dna = dna_manager.get_dna(ticker)
        quant = analysis.get('quant_stats', {})
        
        analysis_summary.append({
            "ticker": ticker,
            "asset_dna": {
                "type": dna.get('asset_type'),
                "bullish_catalysts": dna.get('bullish_catalysts'),
                "bearish_catalysts": dna.get('bearish_catalysts')
            },
            "sentiment_score": analysis.get('sentiment_score', 0.0),
            "quant_metrics": {
                "trend": quant.get('trend'),
                "rsi_14": quant.get('rsi_14'),
                "beta_spy": quant.get('beta_spy')
            },
            "bull_case": analysis.get('bull_case', {}).get('overall_sentiment', 'N/A'),
            "bear_case": analysis.get('bear_case', {}).get('overall_sentiment', 'N/A'),
            "bull_rationale": analysis.get('bull_case', {}).get('deep_analysis', 'N/A'),
            "bear_rationale": analysis.get('bear_case', {}).get('deep_analysis', 'N/A'),
            "risk_score": analysis.get('risk_analysis', {}).get('risk_score', 'N/A'),
            "recommended_size_usd": analysis.get('requested_capital', 1000.0)
        })

    prompt = f"""
    You are the Chief Investment Officer (CIO). Your goal is to select the BEST investment opportunity while maintaining institutional-grade rigor.

    ASSET DNA MANDATE:
    You MUST validate the Bull/Bear rationales against the 'asset_dna' provided for each ticker. 
    - If an analyst recommends a trade that contradicts the asset's DNA (e.g., Bearish on Oil because of War), you MUST REJECT that analysis.
    - Prioritize trades where the Macro Sentiment aligns with the DNA's 'bullish_catalysts'.

    PORTFOLIO STATE & HEALTH:
    - Equity: ${portfolio_state.get('equity', 0):,.2f} | Cash: ${portfolio_state.get('cash', 0):,.2f}
    - Sharpe Ratio: {portfolio_metrics.get('sharpe_ratio', 'N/A')}
    - Win Rate: {strategy_metrics.get('win_rate', 'N/A')}%

    CANDIDATES FOR ANALYSIS:
    {json.dumps(analysis_summary, indent=2)}

    OUTPUT FORMAT (JSON):
    {{
        "selected_ticker": "TICKER or NONE",
        "action": "BUY or WAIT",
        "target_size_usd": 1500.0,
        "conviction_score": 1-10,
        "rationale": "High-level reasoning connecting DNA validation with System Health",
        "dna_validation_notes": "Specific mention of how you validated the analysts' thesis against the asset's DNA",
        "prioritization_list": []
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
