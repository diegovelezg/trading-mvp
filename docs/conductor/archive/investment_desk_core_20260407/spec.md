# Specification: Investment Desk Core & News Ingestion

## Goal
Establish the foundational multi-agent infrastructure for the "Mesa de Inversión," focusing on automated news ingestion, sentiment analysis, and auditable storage.

## Components
1. **Environment & Scaffolding**: Setup Python virtual environment, `.env` for secrets, and initial project structure.
2. **Persistence Layer (SQLite)**: Initialize `trading.db` with tables for `news`, `sentiments`, `tickers`, and `trades`.
3. **Database Manager (`db_manager.py`)**: A utility module to handle SQLite connections and CRUD operations for agents.
4. **Macro Analyst Agent (`macro_analyst.py`)**:
    - Fetches news from Alpaca News API.
    - Processes news using Gemini 3 Flash to extract sentiment scores (-1 to 1) and summaries.
    - Stores results in SQLite.

## Success Criteria
- [ ] Database `trading.db` is initialized with the correct schema.
- [ ] Scripts can fetch news from Alpaca and analyze sentiment via Gemini 3 Flash.
- [ ] Every news item and sentiment score is correctly logged in SQLite.
- [ ] Code coverage for new modules exceeds 80%.