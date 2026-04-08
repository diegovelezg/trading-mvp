# Implementation Plan: Investment Desk Core

## Phase 1: Infrastructure & Database [checkpoint: 4aca89f]
- [x] Task: Project Scaffolding (8d8d284)
    - [ ] Create Python virtual environment (`venv`) and install dependencies (alpaca-py, google-genai, python-dotenv).
    - [ ] Create `.env.example` with required keys (ALPACA, GEMINI, ZAI).
- [x] Task: Database Schema Initialization (31ea7a2)
    - [ ] Write a script to create `trading.db` with tables for news, sentiments, and tickers.
    - [ ] Implement `db_manager.py` for standardized database access.
- [x] Task: Conductor - User Manual Verification 'Infrastructure & Database' (Protocol in workflow.md) (4aca89f)

## Phase 2: News Ingestion & Analysis
- [x] Task: Alpaca News Integration (bc19fb7)
    - [ ] Implement a script to fetch the latest news for a given watchlist from Alpaca.
- [x] Task: Gemini Sentiment Analysis (eb01565)
    - [ ] Implement a script using Gemini 3 Flash to score news sentiment and generate summaries.
- [x] Task: Integrated Ingestion Flow (a3baa98)
    - [ ] Connect news fetching, sentiment analysis, and database storage into a single "Macro Analyst" workflow.
- [~] Task: Conductor - User Manual Verification 'News Ingestion & Analysis' (Protocol in workflow.md)