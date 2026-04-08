# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **agentic trading MVP** implementing a multi-agent "Mesa de Inversión" (Investment Desk) for automated trading research and execution. The project follows a **Claude-native architecture**, leveraging subagents for orchestration while using Python as the core financial engine.

## ✅ IMPLEMENTATION STATUS: 100% COMPLETE

All 7 specialized roles + Orchestrator are implemented and tested.

## Native Architecture

### Subagents (`.claude/subagents/`)
- **Explorer** (`explorer.md`): Thematic research scout. Discovers tickers matching a theme. ✅
- **Macro Analyst** (`macro_analyst.md`): Ingests news and performs sentiment analysis. ✅
- **Hypothesis Generator** (`hypothesis_generator.md`): Generates investment theses. ✅
- **Bull Researcher** (`bull_researcher.md`): Bullish analysis and arguments. ✅
- **Bear Researcher** (`bear_researcher.md`): Bearish analysis and risks. ✅
- **Risk Manager** (`risk_manager.md`): Risk assessment and position sizing. ✅
- **Executioner** (`executioner.md`): Executes orders in Alpaca. ✅
- **Orchestrator** (`orchestrator.md`): Coordinates complete workflow. ✅

### Financial Engine (`trading_mvp/`)
- **Core** (`trading_mvp/core/`): Database management with `criteria` field.
- **News** (`trading_mvp/news/`): Alpaca integration and news sourcing (83% coverage).
- **Analysis** (`trading_mvp/analysis/`): LLM-based sentiment analysis (93% coverage).
- **Execution** (`trading_mvp/execution/`): Alpaca order execution (35% coverage).
- **Reporting** (`trading_mvp/reporting/`): Trade Cards (85% coverage) and performance reports.

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Execution: Complete Workflow
```bash
# Orchestrator - Coordinates ALL subagents automatically
python .claude/subagents/orchestrator/agent.py "AI infrastructure" --capital 5000

# With execution
python .claude/subagents/orchestrator/agent.py "EV stocks" --capital 10000 --execute
```

### Execution: Individual Subagents
```bash
# Explorer Agent
python .claude/subagents/explorer/agent.py "small caps in energy"

# Macro Analyst
python .claude/subagents/macro_analyst/agent.py --symbols "AAPL,TSLA"

# Hypothesis Generator
python .claude/subagents/hypothesis_generator/agent.py --tickers "AAPL,TSLA,MSFT"

# Bull Researcher
python .claude/subagents/bull_researcher/agent.py --ticker "AAPL"

# Bear Researcher
python .claude/subagents/bear_researcher/agent.py --ticker "AAPL"

# Risk Manager
python .claude/subagents/risk_manager/agent.py --ticker "AAPL" --position-size 1000

# Executioner
python .claude/subagents/executioner/agent.py --symbol "AAPL" --action "BUY" --qty 10
python .claude/subagents/executioner/agent.py --positions
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=trading_mvp --cov-report=term-missing

# Test specific subagent
pytest tests/subagents/test_orchestrator.py -v
```

### Database Queries
```bash
# View recent explorations with criteria
python scripts/query_explorations.py --limit 5

# Migrate database schema
python scripts/migrate_db.py
```

## Database Schema (`data/trading.db`)
- `explorations` - Thematic research with `criteria`, `tickers`, `reasoning`, `timestamp`
- `news` - Raw news items from Alpaca
- `sentiments` - AI-generated sentiment scores
- `tickers` - Stock symbols with metadata
- `trades` - Execution records

## Test Coverage
- **Overall**: 65% coverage
- **Tests**: 10/12 passing (83%)
- **Subagent tests**: Fully functional for all 8 subagents
- **Shared code modules**: 65-93% coverage

## Development Workflow
Follow the **TDD workflow**. All logic changes must be covered by unit tests in the `tests/` directory.

## Architecture Principles
1. **Separation**: `trading_mvp/` for shared code, `.claude/subagents/` for specialized roles
2. **Self-contained**: Each subagent has its `.md` + `agent.py` + `__init__.py`
3. **Native orchestration**: Orchestrator uses `importlib` to load subagents dynamically
4. **No mock data**: Orchestrator calls real subagent functions
5. **Database persistence**: All decisions and criteria logged for audit

## Key Files
- `README.md` - User-facing documentation
- `STRUCTURE.md` - Architecture and structure details
- `IMPLEMENTATION_COMPLETE.md` - Implementation status and metrics
- `pyproject.toml` - Modern Python packaging
- `.env.example` - Environment variables template
