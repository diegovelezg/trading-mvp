# Product Guidelines: Agentic Trading MVP

## Prose & Communication Style
- **Technical & Concise**: Use precise technical language. Avoid conversational filler in automated reports.
- **Action-Oriented**: Focus on clear signals and actionable outcomes.
- **Consistent Terminology**: Use standardized terms for agent roles (e.g., "Macro Analyst") and artifacts (e.g., "Trade Card").

## CLI Design Principles
- **High-Signal Outputs**: Terminal outputs should be structured for quick scanning. Use Markdown elements (headers, tables) for clarity.
- **Structured Reports**: All agent reports and trade signals must follow a consistent template to ensure interoperability between Claude Code and Gemini CLI.
- **Idempotency**: CLI scripts and agent actions should be idempotent wherever possible to ensure reliability in an automated environment.

## Multi-Agent Interaction Guidelines
- **Dialectical Rigor**: The "Bull vs. Bear" debate must be grounded in documented news and data points.
- **Transparent Reasoning**: Every trade signal must include a "Reasoning" section that links back to specific SQLite entries.
- **Role Autonomy**: Agents should operate within their defined scope (e.g., the Macro Analyst doesn't suggest trade sizes; that's the Risk Manager's job).

## Technical & Security Guidelines
- **Credential Hygiene**: Strictly use `.env` files for API keys. Never hardcode credentials.
- **Environment Isolation**: Always use Python virtual environments (`venv`) for project execution.
- **Auditable State**: Every decision and news ingestion event must be logged in SQLite with a timestamp and agent ID.
- **Modular Design**: Scripts and skills should be self-contained and reusable across different agent tasks.