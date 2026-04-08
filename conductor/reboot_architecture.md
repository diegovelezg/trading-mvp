# Implementation Plan: Architectural Reboot (Claude-Native)

## Objective
Reorganize the project from the root to align with Claude Code's native subagent and skill system while maintaining Python as the core financial engine.

## Root Reorganization

### 1. Logic Isolation (`src/`)
Move current root Python scripts into a structured `src/` directory:
- `src/core/`: Database management (`db_manager.py`).
- `src/news/`: Alpaca integration (`alpaca_news.py`).
- `src/analysis/`: Sentiment analysis (`gemini_sentiment.py`).
- `src/agents/`: Agent specific logic (`explorer_agent.py`, `macro_analyst.py`).

### 2. Claude Native Layer (`.claude/`)
- `.claude/subagents/`: Markdown definitions for specialized agents.
- `.claude/skills/`: (Optional) Specialized TS/JS tools if bash-to-python is insufficient.

## Implementation Steps

### Phase 1: Engine Migration
- [ ] Create `src/` directory structure.
- [ ] Move Python modules and fix imports.
- [ ] Update `tests/` to reflect new paths.
- [ ] Update `.claude/settings.local.json` permissions if necessary.

### Phase 2: Native Agent Codification
- [ ] Define `explorer.md` subagent in `.claude/subagents/`.
- [ ] Define `macro_analyst.md` subagent in `.claude/subagents/`.
- [ ] Define `sentiment_analyst.md` subagent in `.claude/subagents/`.

### Phase 3: Documentation & Sync
- [ ] Rename `AGENTS.md` to `CLAUDE.md` and update its content.
- [ ] Update `README.md` with new architecture diagrams.
- [ ] Synchronize `conductor` metadata.

## Verification
- [ ] All tests pass with `PYTHONPATH=src pytest`.
- [ ] Subagents can be invoked via Claude CLI (if supported by environment).
- [ ] Root directory is clean (only config and entry points).
