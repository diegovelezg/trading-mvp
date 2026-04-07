# Implementation Plan: Investment Desk Core

## Phase 1: Infrastructure & Database
- [ ] Task: Project Scaffolding
    - [ ] Create Python virtual environment (`venv`) and install dependencies (alpaca-py, google-genai, python-dotenv).
    - [ ] Create `.env.example` with required keys (ALPACA, GEMINI, ZAI).
- [ ] Task: Database Schema Initialization
    - [ ] Write a script to create `trading.db` with tables for news, sentiments, and tickers.
    - [ ] Implement `db_manager.py` for standardized database access.
- [ ] Task: Conductor - User Manual Verification 'Infrastructure & Database' (Protocol in workflow.md)

## Phase 2: News Ingestion & Analysis
- [ ] Task: Alpaca News Integration
    - [ ] Implement a script to fetch the latest news for a given watchlist from Alpaca.
- [ ] Task: Gemini Sentiment Analysis
    - [ ] Implement a script using Gemini 3 Flash to score news sentiment and generate summaries.
- [ ] Task: Integrated Ingestion Flow
    - [ ] Connect news fetching, sentiment analysis, and database storage into a single "Macro Analyst" workflow.
- [ ] Task: Conductor - User Manual Verification 'News Ingestion & Analysis' (Protocol in workflow.md)