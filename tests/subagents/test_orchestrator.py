"""Tests for the Orchestrator agent - NATIVE ORCHESTRATION."""

import os
import sys
import pytest
import importlib.util
from unittest.mock import MagicMock, patch

# Load agent module directly
def load_agent_module(agent_name):
    """Load a subagent module by name."""
    # Get the project root (parent of tests/subagents/)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    agent_path = os.path.join(project_root, ".claude", "subagents", agent_name, "agent.py")
    spec = importlib.util.spec_from_file_location(f"{agent_name}_agent", agent_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{agent_name}_agent"] = module
    spec.loader.exec_module(module)
    return module

# Load required modules
orchestrator_agent = load_agent_module("orchestrator")
explorer_agent = load_agent_module("explorer")
hypothesis_agent = load_agent_module("hypothesis_generator")
bull_agent = load_agent_module("bull_researcher")
bear_agent = load_agent_module("bear_researcher")
risk_agent = load_agent_module("risk_manager")
macro_agent = load_agent_module("macro_analyst")

# Add project root for trading_mvp imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_orchestrator_workflow_with_real_agents():
    """Verify that orchestrator coordinates all agents in sequence using real agent calls."""
    orchestrate_investment_workflow = orchestrator_agent.orchestrate_investment_workflow

    # Mock all the real agent calls - must patch them where they're imported
    with patch.object(explorer_agent, 'discover_tickers') as mock_discover:
        with patch.object(hypothesis_agent, 'generate_hypothesis') as mock_hypothesis:
            with patch.object(macro_agent, 'ingest_and_analyze') as mock_ingest:
                with patch.object(bull_agent, 'analyze_bull_case') as mock_bull:
                    with patch.object(bear_agent, 'analyze_bear_case') as mock_bear:
                        with patch.object(risk_agent, 'assess_risk') as mock_risk:
                            with patch.object(orchestrator_agent, 'get_avg_sentiment') as mock_sentiment:

                                # Setup mock returns
                                mock_discover.return_value = ["AAPL", "TSLA", "MSFT"]
                                mock_hypothesis.return_value = {
                                    "thesis": "bullish",
                                    "drivers": ["AI growth", "Cloud expansion"],
                                    "reasoning": "Strong fundamentals"
                                }
                                mock_ingest.return_value = None  # This function doesn't return anything
                                mock_bull.return_value = {
                                    "arguments": ["Strong growth", "Market leadership", "Innovation"],
                                    "overall_sentiment": "Strong Buy",
                                    "price_targets": {"base": 175, "bull": 200, "super_bull": 250}
                                }
                                mock_bear.return_value = {
                                    "arguments": ["Valuation concerns"],
                                    "overall_sentiment": "Hold",
                                    "price_targets": {"base": 120, "bear": 100, "super_bear": 80}
                                }
                                mock_risk.return_value = {
                                    "risk_score": "Medium",
                                    "position_size_recommendation": "appropriate",
                                    "stop_loss": {"percentage": 0.05, "price": 142.50},
                                    "take_profit": [{"level": 165.00, "target": "TP1"}],
                                    "risk_reward_ratio": "1:3"
                                }
                                mock_sentiment.return_value = 0.75

                                # Run orchestrator
                                result = orchestrate_investment_workflow("AI stocks", 5000)

                                # Verify all agents were called
                                mock_discover.assert_called_once_with("AI stocks")
                                mock_hypothesis.assert_called_once_with(["AAPL", "TSLA", "MSFT"])
                                mock_ingest.assert_called_once()
                                mock_bull.assert_called_once_with("AAPL")
                                mock_bear.assert_called_once_with("AAPL")
                                mock_risk.assert_called_once_with("AAPL", 5000)

                                # Verify workflow completed
                                assert result is not None
                                assert 'theme' in result
                                assert result['theme'] == "AI stocks"
                                assert 'action' in result
                                assert 'trade_card' in result
                                assert 'selected_ticker' in result
                                assert result['selected_ticker'] == "AAPL"

def test_orchestrator_generates_trade_card():
    """Verify that orchestrator generates complete Trade Card with real data."""
    orchestrate_investment_workflow = orchestrator_agent.orchestrate_investment_workflow

    # Mock all agent calls
    with patch.object(explorer_agent, 'discover_tickers', return_value=["AAPL"]):
        with patch.object(hypothesis_agent, 'generate_hypothesis', return_value={"thesis": "bullish", "drivers": ["Growth"]}):
            with patch.object(macro_agent, 'ingest_and_analyze', return_value=None):
                with patch.object(bull_agent, 'analyze_bull_case', return_value={"arguments": ["Strong"], "overall_sentiment": "Buy"}):
                    with patch.object(bear_agent, 'analyze_bear_case', return_value={"arguments": ["Risk"], "overall_sentiment": "Hold"}):
                        with patch.object(risk_agent, 'assess_risk', return_value={"risk_score": "Low"}):
                            with patch.object(orchestrator_agent, 'get_avg_sentiment', return_value=0.8):

                                result = orchestrate_investment_workflow("tech stocks", 1000)

                                # Should generate a trade card
                                assert 'trade_card' in result
                                assert 'RECOMMENDATION:' in result['trade_card']
                                assert 'INVESTMENT HYPOTHESIS' in result['trade_card']
                                assert 'BULL CASE' in result['trade_card']
                                assert 'BEAR CASE' in result['trade_card']
                                assert 'RISK ANALYSIS' in result['trade_card']
                                assert 'SENTIMENT SCORE' in result['trade_card']

def test_orchestrator_determine_action():
    """Verify that orchestrator determines investment action correctly."""
    determine_investment_action = orchestrator_agent.determine_investment_action

    # Strong bullish case
    action = determine_investment_action(
        hypothesis={"thesis": "bullish"},
        bull_case={"arguments": ["A", "B", "C"]},
        bear_case={"arguments": ["A"]},
        risk_analysis={"risk_score": "Low"},
        sentiment_score=0.8
    )
    assert action == "BUY"

    # Strong bearish case
    action = determine_investment_action(
        hypothesis={"thesis": "bearish"},
        bull_case={"arguments": ["A"]},
        bear_case={"arguments": ["A", "B", "C"]},
        risk_analysis={"risk_score": "High"},
        sentiment_score=-0.8
    )
    assert action == "SELL"

    # Neutral case
    action = determine_investment_action(
        hypothesis={"thesis": "neutral"},
        bull_case={"arguments": ["A", "B"]},
        bear_case={"arguments": ["A", "B"]},
        risk_analysis={"risk_score": "Medium"},
        sentiment_score=0.0
    )
    assert action == "HOLD"

def test_orchestrator_calculate_quantity():
    """Verify that orchestrator calculates position size correctly."""
    calculate_quantity = orchestrator_agent.calculate_quantity

    # Medium risk
    qty = calculate_quantity(5000, "AAPL", {"position_size_recommendation": "appropriate"})
    assert qty == int(5000 / 150)  # Based on estimated $150/share

    # Conservative
    qty = calculate_quantity(5000, "AAPL", {"position_size_recommendation": "conservative"})
    assert qty == int((5000 * 0.5) / 150)

    # Aggressive
    qty = calculate_quantity(5000, "AAPL", {"position_size_recommendation": "aggressive"})
    assert qty == int((5000 * 1.5) / 150)

def test_orchestrator_get_avg_sentiment():
    """Verify sentiment retrieval from database."""
    get_avg_sentiment = orchestrator_agent.get_avg_sentiment

    # Mock database query
    with patch('trading_mvp.core.db_manager.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_conn.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [0.65]

        sentiment = get_avg_sentiment("AAPL")

        assert sentiment == 0.65
        mock_cursor.execute.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
