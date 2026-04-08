# Specification: Architectural Reboot (Claude-Native)

## Goal
Fundamental reorganization of the project structure to prioritize Claude Code native subagent/skill architecture while isolating Python logic as a high-fidelity execution engine.

## New Structure
```
.claude/
  subagents/         # Agent roles (Explorer, Macro Analyst, etc.)
  skills/            # Domain-specific tools
src/
  core/              # Persistence and common utilities
  news/              # Alpaca and news sourcing
  analysis/          # LLM Sentiment and reasoning
  agents/            # Logic for automated workflows
```

## Success Criteria
- [ ] No Python logic remains in the root directory.
- [ ] Subagents are defined as native Claude configuration files.
- [ ] Tests remain fully functional against the new structure.
- [ ] Documentation (`CLAUDE.md`) is the definitive source of truth for Claude Code.
