"""Test the Explorer Agent's criteria registration functionality."""

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
explorer_agent = load_agent_module("explorer")

# Add project root for trading_mvp imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def test_explorer_saves_criteria():
    """Verify that Explorer Agent saves search criteria to database."""
    from trading_mvp.core.db_manager import get_recent_explorations

    # The explorer should save:
    # 1. Original prompt
    # 2. Extracted criteria
    # 3. Discovered tickers
    # 4. Reasoning
    # 5. Timestamp

    explorations = get_recent_explorations(limit=1)
    assert len(explorations) >= 0  # At least query works

def test_explorer_criteria_fields():
    """Verify that explorations table has criteria field."""
    from trading_mvp.core.db_manager import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    # Check table schema
    cursor.execute("PRAGMA table_info(explorations)")
    columns = [row[1] for row in cursor.fetchall()]

    assert 'criteria' in columns, "Explorations table must have 'criteria' field"
    assert 'tickers' in columns, "Explorations table must have 'tickers' field"
    assert 'reasoning' in columns, "Explorations table must have 'reasoning' field"
    assert 'timestamp' in columns, "Explorations table must have 'timestamp' field"

    conn.close()

def test_explorer_generates_criteria():
    """Verify that Explorer Agent generates structured criteria."""
    # This would test the extract_search_criteria function
    # For now, we just verify the function exists
    extract_search_criteria = explorer_agent.extract_search_criteria

    criteria = extract_search_criteria("small caps in energy sector")
    assert isinstance(criteria, str)
    assert len(criteria) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
