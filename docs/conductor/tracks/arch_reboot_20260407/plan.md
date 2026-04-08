# Implementation Plan: Architectural Reboot

## Phase 1: Engine Migration
- [x] Task: Create `src/` hierarchy.
- [x] Task: Move and Refactor `db_manager.py` to `src/core/`.
- [x] Task: Move and Refactor `alpaca_news.py` to `src/news/`.
- [x] Task: Move and Refactor `gemini_sentiment.py` to `src/analysis/`.
- [x] Task: Move and Refactor `explorer_agent.py` and `macro_analyst.py` to `src/agents/`.
- [x] Task: Update `tests/` and verify with `PYTHONPATH=src pytest`.

## Phase 2: Claude Native Integration
- [x] Task: Create `.claude/subagents/` directory.
- [x] Task: Define `explorer.md` subagent.
- [x] Task: Define `macro_analyst.md` subagent.

## Phase 3: Final Polishing
- [x] Task: Rename `AGENTS.md` to `CLAUDE.md`.
- [x] Task: Update `README.md`.
- [x] Task: Cleanup root directory.
