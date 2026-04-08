"""Tests for Risk Manager agent."""

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
risk_manager_agent = load_agent_module("risk_manager")

# Add project root for trading_mvp imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_risk_manager_assesses_position_size():
    """Verify that Risk Manager calculates appropriate position sizes."""
    assess_risk = risk_manager_agent.assess_risk

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch.object(risk_manager_agent, 'Client') as MockClient:
            mock_client = MockClient.return_value
            mock_response = MagicMock()
            mock_response.text = '''{
                "risk_score": "Medium",
                "stop_loss": {"percentage": 0.05, "price": 142.50},
                "take_profit": [{"level": 165.00, "target": "TP1"}],
                "position_size_recommendation": "appropriate"
            }'''
            mock_client.models.generate_content.return_value = mock_response

            risk = assess_risk("AAPL", 1000)

            assert risk['risk_score'] == "Medium"
            assert 'stop_loss' in risk

def test_risk_manager_calculates_risk_reward():
    """Verify that Risk Manager calculates risk/reward ratios."""
    assess_risk = risk_manager_agent.assess_risk

    with patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"}):
        with patch.object(risk_manager_agent, 'Client') as MockClient:
            mock_client = MockClient.return_value
            mock_response = MagicMock()
            mock_response.text = '''{
                "risk_reward_ratio": "1:3"
            }'''
            mock_client.models.generate_content.return_value = mock_response

            risk = assess_risk("AAPL", 1000)

            assert risk['risk_reward_ratio'] == "1:3"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
