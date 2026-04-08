# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **agentic trading MVP** implementing a multi-agent "Mesa de Inversión" (Investment Desk) for automated trading research and execution. The project follows a **Claude-native architecture**, leveraging subagents and skills for orchestration while using Python as the core financial engine.

## Native Architecture

### Subagents (`.claude/subagents/`)
- **Explorer** (`explorer.md`): Thematic research scout. Discovers tickers matching a theme.
- **Macro Analyst** (`macro_analyst.md`): Ingests news and performs sentiment analysis.

### Financial Engine (`src/`)
- **Core** (`src/core/`): Database management and common utilities.
- **News** (`src/news/`): Alpaca integration and news sourcing.
- **Analysis** (`src/analysis/`): LLM-based sentiment and reasoning logic.
- **Agents** (`src/agents/`): Automated workflow logic.

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install alpaca-py google-genai python-dotenv pytest pytest-cov
```

### Execution (Engine Layer)
```bash
# Explorer Agent
PYTHONPATH=. python3 src/agents/explorer_agent.py "small caps in energy"

# Macro Analyst
PYTHONPATH=. python3 src/agents/macro_analyst.py --symbols "AAPL,TSLA"
```

### Testing
```bash
# Run all tests
PYTHONPATH=. pytest tests/

# Run with coverage
PYTHONPATH=. pytest --cov=src --cov-report=term-missing
```

## Database Schema (`trading.db`)
- `news`: Raw news items from Alpaca.
- `sentiments`: AI-generated sentiment scores.
- `tickers`: Stock symbols with metadata.
- `trades`: Execution records.
- `explorations`: Thematic research results.

## Development Workflow
Follow the **strict TDD workflow** defined in `conductor/workflow.md`. All logic changes must be covered by unit tests in the `tests/` directory.
