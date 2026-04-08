"""Tests for Executioner agent."""

import os
import sys
import pytest
import importlib.util
from unittest.mock import MagicMock, patch

# Load agent modules directly
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
executioner_agent = load_agent_module("executioner")
risk_manager_agent = load_agent_module("risk_manager")
orchestrator_agent = load_agent_module("orchestrator")

# Add project root for trading_mvp imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_executioner_submits_order():
    """Verify that Executioner can submit orders to Alpaca."""
    execute_trade = executioner_agent.execute_trade

    with patch.object(executioner_agent, 'submit_order') as mock_order:
        mock_order.return_value = {
            "order_id": "order_123",
            "symbol": "AAPL",
            "status": "accepted"
        }

        order = execute_trade("AAPL", "BUY", 10)

        assert order['order_id'] == "order_123"
        assert order['symbol'] == "AAPL"

def test_executioner_shows_positions():
    """Verify that Executioner can show current positions."""
    show_positions = executioner_agent.show_positions

    with patch.object(executioner_agent, 'get_positions') as mock_positions:
        with patch.object(executioner_agent, 'get_account') as mock_account:
            mock_positions.return_value = [
                {"symbol": "AAPL", "qty": 10, "unrealized_pl": 500.0}
            ]
            mock_account.return_value = {"portfolio_value": 10000.0}

            positions = show_positions()

            assert positions is not None
            assert isinstance(positions, list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
