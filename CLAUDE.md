# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **agentic trading MVP** implementing a multi-agent "Mesa de Inversión" (Investment Desk) for automated trading research and execution. The system uses multiple AI agents with specialized roles:

- **Explorer Agent** (`explorer_agent.py`): Discovers relevant stock tickers based on thematic prompts using Gemini
- **Macro Analyst** (`macro_analyst.py`): Ingests news from Alpaca and analyzes sentiment using Gemini
- **Gemini Sentiment** (`gemini_sentiment.py`): Analyzes financial news sentiment with Gemini 2.0 Flash
- **Alpaca News** (`alpaca_news.py`): Fetches market news from Alpaca API

## Common Development Commands

### Environment Setup
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies (if needed)
pip install alpaca-py google-genai python-dotenv pytest
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_explorer_agent.py

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Non-interactive mode (for CI)
CI=true pytest
```

### Running Agent Scripts
```bash
# Explorer Agent: discover tickers for a theme
python explorer_agent.py "small caps in gas and nuclear energy"

# Explorer Agent: discover and automatically analyze
python explorer_agent.py "semiconductor stocks" --analyze

# Macro Analyst: analyze news for specific symbols
python macro_analyst.py
```

### Database Operations
```bash
# Initialize/recreate database schema
python -c "from db_manager import init_db; init_db()"

# Quick check of database contents
sqlite3 trading.db "SELECT * FROM explorations ORDER BY id DESC LIMIT 5;"
```

## Architecture

### Data Flow
1. **Explorer Agent** receives thematic prompt → calls Gemini → discovers tickers → stores in `explorations` table
2. **Handover** (optional) → passes tickers to Macro Analyst
3. **Macro Analyst** → fetches Alpaca news → calls Gemini for sentiment → stores in `news` and `sentiments` tables

### Database Schema (`trading.db`)
- `news`: Raw news items from Alpaca (title, source, url, summary, published_at)
- `sentiments`: AI-generated sentiment scores linked to news items
- `tickers`: Stock symbols with metadata
- `trades`: Execution records
- `explorations`: Thematic research results (prompt + discovered tickers JSON)

### Multi-Agent Coordination
- Scripts are designed to be chainable: `explorer_agent.py` can trigger `macro_analyst.py` via `--analyze` flag
- Each agent has a single responsibility and can be run independently or pipelined

## Development Workflow

This project follows a **strict TDD workflow** defined in `conductor/workflow.md`:

1. **Red Phase**: Write failing tests first
2. **Green Phase**: Implement minimum code to pass tests
3. **Refactor**: Improve code while tests pass
4. **Coverage**: Aim for >80% code coverage
5. **Quality Gates**: All tests must pass before marking task complete

### Commit Conventions
- Use conventional commit format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `test`, `refactor`, `chore`
- Example: `feat(explorer): Add thematic ticker discovery CLI`

## Code Style

- **Python Style**: Follow Google Python Style Guide (`conductor/code_styleguides/python.md`)
  - 4-space indentation, 80-char line length
  - Type hints encouraged for public APIs
  - Docstrings with `Args:`, `Returns:`, `Raises:` sections
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Imports**: Standard library → third-party → local imports

## Environment Variables

Required in `.env` (see `.env.example`):
```
ALPACA_API_KEY_ID=your_key
ALPACA_API_SECRET_KEY=your_secret
GEMINI_API_KEY=your_gemini_key
```

## Key Files Reference

- `db_manager.py`: Database connection and CRUD operations
- `conductor/`: Project planning, workflow docs, and style guides
- `conductor/tracks/*/plan.md`: Implementation plans with task tracking
- `README.md`: Detailed project background and architecture research
