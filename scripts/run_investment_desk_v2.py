#!/usr/bin/env python3
"""
Investment Desk v2 - Workflow Orchestration con Fail-Fast

CAMBIOS CRÍTICOS:
1. PASO 0: Extracción forzada de noticias (NO puede fallar silenciosamente)
2. Fail-fast: Si cualquier paso falla, se DETIENE la ejecución
3. Logging estructurado: Cada paso queda registrado con timestamps
4. No silent failures: Todos los errores son explícitos y tracked

Uso:
    python run_investment_desk_v2.py --hours-back 48
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from datetime import datetime
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('investment_desk_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up environment
os.environ['ALPACA_PAPER_API_KEY'] = 'YOUR_ALPACA_PAPER_API_KEY'
os.environ['PAPER_API_SECRET'] = 'YOUR_ALPACA_SECRET_KEY'
os.environ['SERPAPI_API_KEY'] = 'YOUR_SERPAPI_API_KEY'
os.environ['GEMINI_API_KEY'] = 'AIzaSyCutHRoCMkN02KhsVYATzu5XRPjboQZxnc'
os.environ['GEMINI_API_MODEL_01'] = 'gemini-3.1-flash-lite-preview'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.claude', 'subagents'))

from trading_mvp.core.dashboard_api_client import get_active_watchlists
from trading_mvp.core.db_investment_tracking import (
    create_investment_tracking_tables,
    save_desk_run,
    save_ticker_analysis,
    record_decision
)
from trading_mvp.agents.decision_agent import DecisionAgent, DecisionConfig
from trading_mvp.execution.alpaca_orders import get_account, get_positions
from trading_mvp.core.workflow_orchestrator import (
    create_workflow_orchestrator,
    StepType
)
from trading_mvp.core.news_extraction import extract_and_validate_news
from trading_mvp.core.entity_extraction_workflow import extract_all_entities

# Import analyze_ticker function
import importlib.util
script_dir = os.path.dirname(os.path.abspath(__file__))
analyze_ticker_path = os.path.join(script_dir, "analyze_ticker.py")

spec = importlib.util.spec_from_file_location("analyze_ticker", analyze_ticker_path)
analyze_ticker_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyze_ticker_module)


def run_investment_desk_v2(hours_back: int = 48) -> Dict:
    """Run investment desk con workflow orchestration y fail-fast.

    Args:
        hours_back: Hours to look back for news

    Returns:
        Complete investment desk analysis
    """

    logger.info("="*70)
    logger.info("🏛️  INVESTMENT DESK v2 - FAIL-FAST WORKFLOW")
    logger.info("="*70)
    logger.info("⚠️  CRITICAL: Pipeline will STOP on ANY failure")
    logger.info("")

    # Inicializar orquestador
    orchestrator = create_workflow_orchestrator(retention_hours=72)

    try:
        # ============================================================
        # PASO 0: EXTRACTION AND VALIDATION OF NEWS
        # CRÍTICO: Si este paso falla, NO debe continuar
        # ============================================================
        logger.info("📰 EXECUTING STEP 0: NEWS EXTRACTION")
        logger.info("")

        news_extraction_result = orchestrator.execute_step(
            step_type=StepType.NEWS_EXTRACTION,
            step_function=extract_and_validate_news,
            step_id="news_extraction_001",
            input_data={
                'hours_back': hours_back,
                'min_news_count': 10,
                'max_age_hours': 24
            },
            fail_fast=True  # CRÍTICO: Detener si falla
        )

        # Validar éxito
        if not news_extraction_result['success']:
            error_msg = f"Step 0 failed: {news_extraction_result.get('error')}"
            logger.error(f"🛑 {error_msg}")
            logger.error("🛑 WORKFLOW ABORTED: Cannot proceed without fresh news")
            return {
                'success': False,
                'error': error_msg,
                'aborted_at': 'step_0_news_extraction'
            }

        logger.info("")
        logger.info("✅ Step 0 completed successfully. Proceeding with entity extraction...")
        logger.info("")

        # ============================================================
        # PASO 0.5: ENTITY EXTRACTION (CRÍTICO - DEPENDENCIA DE PASO 0)
        # ============================================================
        logger.info("🧠 EXECUTING STEP 0.5: ENTITY EXTRACTION")
        logger.info("⚠️  CRITICAL: This step processes ALL news from Step 0")
        logger.info("⏱️  This may take several minutes depending on news volume")
        logger.info("")

        entity_extraction_result = orchestrator.execute_step(
            step_type=StepType.NEWS_EXTRACTION,
            step_function=extract_all_entities,
            step_id="entity_extraction_001",
            input_data={
                'hours_back': hours_back,
                'min_coverage_pct': 0.5,  # 50% mínimo
                'min_total_entities': 100
            },
            fail_fast=True  # CRÍTICO: Detener si no hay suficientes entidades
        )

        if not entity_extraction_result['success']:
            error_msg = f"Step 0.5 failed: {entity_extraction_result.get('error')}"
            logger.error(f"🛑 {error_msg}")
            logger.error("🛑 CANNOT PROCEED TO STEP 4 WITHOUT ENTITIES")
            return {
                'success': False,
                'error': error_msg,
                'aborted_at': 'step_0_5_entity_extraction'
            }

        # VALIDACIÓN DE CHECKPOINTS CRÍTICOS
        validation_checks = entity_extraction_result.get('validation_checks', {})
        if not validation_checks.get('all_checks_passed', False):
            logger.warning("⚠️  Entity extraction validation warnings:")
            for check, passed in validation_checks.items():
                if check != 'all_checks_passed' and not passed:
                    logger.warning(f"   ❌ {check}: FAILED")

            # Si la cobertura es muy baja, fallar
            if entity_extraction_result.get('coverage_pct', 0) < 0.3:
                error_msg = f"Entity coverage too low: {entity_extraction_result['coverage_pct']:.1%} < 30%"
                logger.error(f"🛑 {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'aborted_at': 'step_0_5_entity_extraction'
                }

        logger.info("")
        logger.info(f"✅ Step 0.5 completed: {entity_extraction_result['coverage_pct']:.1%} coverage, ~{entity_extraction_result['total_entities']} entities")
        logger.info("")

        # ============================================================
        # PASO 1: LOAD PORTFOLIO CONTEXT
        # ============================================================
        logger.info("💰 EXECUTING STEP 1: LOAD PORTFOLIO")

        def load_portfolio_context():
            try:
                portfolio_positions = get_positions()
                portfolio_account = get_account()

                portfolio_tickers = [p['symbol'] for p in portfolio_positions]

                logger.info(f"   ✅ Portfolio: {len(portfolio_tickers)} positions")
                logger.info(f"   ✅ Buying Power: ${portfolio_account['buying_power']:.2f}")

                return {
                    'success': True,
                    'positions': portfolio_positions,
                    'account': portfolio_account,
                    'tickers': portfolio_tickers
                }
            except Exception as e:
                logger.error(f"   ❌ Failed to load portfolio: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        portfolio_result = orchestrator.execute_step(
            step_type=StepType.DATA_VALIDATION,
            step_function=load_portfolio_context,
            step_id="load_portfolio_001",
            fail_fast=True
        )

        if not portfolio_result['success']:
            error_msg = f"Step 1 failed: {portfolio_result.get('error')}"
            logger.error(f"🛑 {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'aborted_at': 'step_1_portfolio_load'
            }

        logger.info("")

        # ============================================================
        # PASO 2: GET WATCHLIST
        # ============================================================
        logger.info("📋 EXECUTING STEP 2: LOAD WATCHLIST")

        def load_watchlist():
            try:
                watchlists = get_active_watchlists()

                if not watchlists:
                    return {
                        'success': False,
                        'error': 'No watchlists available'
                    }

                watchlist = watchlists[0]
                watchlist_tickers = [
                    item['ticker']
                    for item in watchlist.get('items', [])
                ]

                logger.info(f"   ✅ Watchlist: {watchlist['name']}")
                logger.info(f"   ✅ Tickers: {len(watchlist_tickers)}")

                return {
                    'success': True,
                    'watchlist': watchlist,
                    'tickers': watchlist_tickers
                }
            except Exception as e:
                logger.error(f"   ❌ Failed to load watchlist: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        watchlist_result = orchestrator.execute_step(
            step_type=StepType.DATA_VALIDATION,
            step_function=load_watchlist,
            step_id="load_watchlist_001",
            fail_fast=True
        )

        if not watchlist_result['success']:
            error_msg = f"Step 2 failed: {watchlist_result.get('error')}"
            logger.error(f"🛑 {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'aborted_at': 'step_2_watchlist_load'
            }

        logger.info("")

        # ============================================================
        # PASO 3: COMBINE TICKERS
        # ============================================================
        all_tickers = list(set(
            portfolio_result['tickers'] +
            watchlist_result['tickers']
        ))

        if not all_tickers:
            logger.error("🛑 No tickers found in portfolio or watchlist")
            return {
                'success': False,
                'error': 'No tickers to analyze',
                'aborted_at': 'step_3_combine_tickers'
            }

        logger.info(f"📊 Total unique tickers to analyze: {len(all_tickers)}")
        logger.info("")

        # ============================================================
        # PASO 4: ANALYZE EACH TICKER
        # ============================================================
        logger.info("🎯 EXECUTING STEP 3: TICKER ANALYSIS")
        logger.info("")

        ticker_results = []
        failed_tickers = []

        for i, ticker in enumerate(all_tickers, 1):
            is_portfolio = ticker in portfolio_result['tickers']
            type_label = "[PORTFOLIO]" if is_portfolio else "[WATCHLIST]"

            logger.info(f"[{i}/{len(all_tickers)}] {type_label} {ticker}...")

            try:
                result = analyze_ticker_module.analyze_ticker(ticker, hours_back=hours_back)

                if result.get('success'):
                    result['is_in_portfolio'] = is_portfolio
                    ticker_results.append(result)
                    logger.info(f"   ✅ {ticker}: {result['recommendation']}")
                else:
                    failed_tickers.append(ticker)
                    logger.warning(f"   ⚠️  {ticker}: Analysis failed")

            except Exception as e:
                failed_tickers.append(ticker)
                logger.error(f"   ❌ {ticker}: {e}")

            logger.info("")

        # Validar que tengamos suficientes análisis
        if len(ticker_results) == 0:
            error_msg = "No ticker analyses completed successfully"
            logger.error(f"🛑 {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'aborted_at': 'step_4_ticker_analysis',
                'failed_tickers': failed_tickers
            }

        logger.info(f"✅ Step 3 completed: {len(ticker_results)}/{len(all_tickers)} tickers analyzed")
        logger.info("")

        # ============================================================
        # PASO 5: AGGREGATE RESULTS
        # ============================================================
        logger.info("📊 EXECUTING STEP 4: AGGREGATION")

        def aggregate_results():
            try:
                # Group by recommendation
                bullish = [t for t in ticker_results if t['recommendation'] == 'BULLISH']
                bearish = [t for t in ticker_results if t['recommendation'] == 'BEARISH']
                cautious = [t for t in ticker_results if t['recommendation'] == 'CAUTIOUS']
                neutral = [t for t in ticker_results if t['recommendation'] == 'NEUTRAL']

                # Sort by sentiment strength
                bullish.sort(key=lambda x: x['positive_ratio'], reverse=True)
                bearish.sort(key=lambda x: x['negative_ratio'], reverse=True)
                cautious.sort(
                    key=lambda x: -x['positive_ratio']
                    if x['positive_ratio'] > x['negative_ratio']
                    else x['negative_ratio']
                )

                # Calculate aggregate metrics
                avg_confidence = sum(t['avg_confidence'] for t in ticker_results) / len(ticker_results)
                avg_negative = sum(t['negative_ratio'] for t in ticker_results) / len(ticker_results)
                avg_positive = sum(t['positive_ratio'] for t in ticker_results) / len(ticker_results)
                total_news = sum(t['related_news_count'] for t in ticker_results)
                total_entities = sum(t['unique_entities_found'] for t in ticker_results)

                # Overall desk sentiment
                if len(bullish) > len(bearish) and avg_positive > avg_negative:
                    overall_sentiment = "BULLISH"
                elif len(bearish) > len(bullish) and avg_negative > avg_positive:
                    overall_sentiment = "BEARISH"
                elif avg_positive > avg_negative:
                    overall_sentiment = "CAUTIOUSLY BULLISH"
                elif avg_negative > avg_positive:
                    overall_sentiment = "CAUTIOUSLY BEARISH"
                else:
                    overall_sentiment = "NEUTRAL"

                return {
                    'success': True,
                    'bullish': bullish,
                    'bearish': bearish,
                    'cautious': cautious,
                    'neutral': neutral,
                    'avg_confidence': round(avg_confidence, 2),
                    'avg_negative_ratio': round(avg_negative, 2),
                    'avg_positive_ratio': round(avg_positive, 2),
                    'total_news_analyzed': total_news,
                    'total_entities_found': total_entities,
                    'overall_sentiment': overall_sentiment
                }
            except Exception as e:
                logger.error(f"   ❌ Aggregation failed: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        aggregation_result = orchestrator.execute_step(
            step_type=StepType.AGGREGATION,
            step_function=aggregate_results,
            step_id="aggregation_001",
            fail_fast=True
        )

        if not aggregation_result['success']:
            error_msg = f"Step 4 failed: {aggregation_result.get('error')}"
            logger.error(f"🛑 {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'aborted_at': 'step_5_aggregation'
            }

        logger.info("")
        logger.info("")

        # ============================================================
        # PASO 6: DECISION AGENT
        # ============================================================
        logger.info("🤖 EXECUTING STEP 5: DECISION ENGINE")
        logger.info("")

        # Ensure tracking tables exist
        create_investment_tracking_tables()

        # Check autopilot mode
        autopilot_mode = os.getenv("AUTOPILOT_MODE", "off").lower() == "on"

        def run_decision_engine():
            try:
                decision_config = DecisionConfig(
                    autopilot_enabled=autopilot_mode,
                    dry_run=False
                )
                decision_agent = DecisionAgent(config=decision_config)

                # Build desk analysis for decision agent
                desk_analysis = {
                    'success': True,
                    'ticker_results': ticker_results,
                    **aggregation_result
                }

                agent_decisions = decision_agent.process_desk_recommendations(
                    desk_analysis=desk_analysis,
                    portfolio_context={
                        'account': portfolio_result['account'],
                        'positions': portfolio_result['positions']
                    }
                )

                return {
                    'success': True,
                    'decisions': agent_decisions,
                    'autopilot_mode': autopilot_mode
                }
            except Exception as e:
                logger.error(f"   ❌ Decision engine failed: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        decision_result = orchestrator.execute_step(
            step_type=StepType.DECISION_ENGINE,
            step_function=run_decision_engine,
            step_id="decision_engine_001",
            fail_fast=False  # No detener si falla decision engine
        )

        if not decision_result['success']:
            logger.warning(f"⚠️  Decision engine failed, but continuing...")
            agent_decisions = []
        else:
            agent_decisions = decision_result['decisions']

        logger.info("")

        # ============================================================
        # PASO 7: PERSISTENCE
        # ============================================================
        logger.info("💾 EXECUTING STEP 6: PERSISTENCE")

        def persist_results():
            try:
                # Save desk run
                desk_analysis = {
                    'success': True,
                    'watchlist': watchlist_result['watchlist'],
                    'analysis_timestamp': datetime.now().isoformat(),
                    'time_window_hours': hours_back,
                    'total_tickers': len(all_tickers),
                    'analyzed_tickers': len(ticker_results),
                    'failed_tickers': failed_tickers,
                    'ticker_results': ticker_results,
                    **aggregation_result,
                    'agent_decisions': agent_decisions
                }

                desk_run_id = save_desk_run(desk_analysis)

                # Save each ticker analysis
                ticker_analysis_ids = {}
                for ticker_result in ticker_results:
                    ticker_analysis_id = save_ticker_analysis(ticker_result, desk_run_id)
                    if ticker_analysis_id:
                        ticker_analysis_ids[ticker_result['ticker']] = ticker_analysis_id

                # Record decisions if in autopilot
                if autopilot_mode and desk_run_id:
                    for decision in agent_decisions:
                        ticker_analysis_id = ticker_analysis_ids.get(decision['ticker'])
                        if ticker_analysis_id:
                            desk_action = 'WATCH'
                            if decision['action'] == 'BOUGHT': desk_action = 'BUY'
                            elif decision['action'] == 'SOLD': desk_action = 'SELL'
                            elif decision['action'] == 'NONE' and decision['decision'] == 'IGNORED':
                                desk_action = 'AVOID'

                            record_decision(
                                ticker_analysis_id=ticker_analysis_id,
                                desk_run_id=desk_run_id,
                                ticker=decision['ticker'],
                                recommendation=decision['original_recommendation'],
                                desk_action=desk_action,
                                decision=decision['decision'],
                                decision_notes=decision['rationale'],
                                action_taken=decision['action'],
                                position_size=decision.get('position_size'),
                                entry_price=decision.get('entry_price'),
                                alpaca_order_id=decision.get('order_id')
                            )

                return {
                    'success': True,
                    'desk_run_id': desk_run_id,
                    'ticker_analysis_ids': ticker_analysis_ids
                }
            except Exception as e:
                logger.error(f"   ❌ Persistence failed: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        persistence_result = orchestrator.execute_step(
            step_type=StepType.PERSISTENCE,
            step_function=persist_results,
            step_id="persistence_001",
            fail_fast=False  # No crítico si falla persistencia
        )

        # ============================================================
        # FINALIZE
        # ============================================================
        orchestrator.finalize_execution()

        # Compilar resultado final
        final_result = {
            'success': True,
            'execution_id': orchestrator.execution_id,
            'workflow_steps': len(orchestrator.steps),
            'completed_steps': len([s for s in orchestrator.steps
                                   if s.status == 'completed']),
            'failed_steps': len([s for s in orchestrator.steps
                                if s.status == 'failed']),
            'watchlist': watchlist_result['watchlist'],
            'total_tickers': len(all_tickers),
            'analyzed_tickers': len(ticker_results),
            'failed_tickers': failed_tickers,
            'overall_sentiment': aggregation_result['overall_sentiment'],
            'news_extraction_stats': news_extraction_result['stats'],
            'agent_decisions': agent_decisions,
            'autopilot_mode': autopilot_mode
        }

        if persistence_result['success']:
            final_result['desk_run_id'] = persistence_result['desk_run_id']

        logger.info("="*70)
        logger.info("✅ INVESTMENT DESK v2 COMPLETE")
        logger.info(f"   Execution ID: {orchestrator.execution_id}")
        logger.info(f"   Steps completed: {final_result['completed_steps']}/{final_result['workflow_steps']}")
        logger.info(f"   Overall sentiment: {final_result['overall_sentiment']}")
        logger.info("="*70)

        return final_result

    except Exception as e:
        # Error inesperado en el workflow
        orchestrator.finalize_execution()

        logger.error("="*70)
        logger.error(f"❌ WORKFLOW FAILED UNEXPECTEDLY: {e}")
        logger.error("="*70)

        return {
            'success': False,
            'error': str(e),
            'execution_id': orchestrator.execution_id
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run Investment Desk v2')
    parser.add_argument('--hours-back', type=int, default=48,
                       help='Hours to look back (default: 48)')

    args = parser.parse_args()

    result = run_investment_desk_v2(hours_back=args.hours_back)

    if not result.get('success'):
        sys.exit(1)
