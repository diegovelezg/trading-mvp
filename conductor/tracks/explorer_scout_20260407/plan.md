# Implementation Plan: Explorer/Scout Agent

## Phase 1: Research & Discovery [checkpoint: ]
- [ ] Task: Exploration Schema
    - [ ] Create `explorations` table in `trading.db` to store prompts and results.
    - [ ] Update `db_manager.py` with insertion helpers for explorations.
- [ ] Task: Ticker Discovery Logic
    - [ ] Implement `explorer_agent.py` to use Gemini for company/ticker brainstorming.
    - [ ] Implement web search or financial data lookup (if needed) for validation.

## Phase 2: Core Explorer Implementation [checkpoint: ]
- [ ] Task: Explorer Command Line Interface
    - [ ] Add CLI arguments to `explorer_agent.py` for thematic prompts.
    - [ ] Implement the core discovery loop and results extraction.
- [ ] Task: Test Discovery Quality
    - [ ] Write tests to verify the agent's ability to find relevant tickers for specific themes.

## Phase 3: Integration & Handover [checkpoint: ]
- [ ] Task: Explorer-Analyst Handover
    - [ ] Implement a function to automatically trigger `macro_analyst.py` with the discovered tickers.
- [ ] Task: Conductor - User Manual Verification 'Explorer/Scout' (Protocol in workflow.md)
