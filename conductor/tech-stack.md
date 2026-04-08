# Tech Stack: Agentic Trading MVP

## Languages & Runtimes
- **Python 3.10+**: Core language for scripts, data processing, and Alpaca integration. Libraries: `alpaca-py`, `google-genai`, `python-dotenv`.
- **Node.js**: Runtime for Claude Code and potential MCP server developments.

## Multi-Agent Ecosystem (LLMs)
- **Claude Code**: Primary agentic terminal for orchestration, code management, and task execution.
- **Gemini CLI (1.5 / 2.0 / 3.0)**: Used for large-scale research, news ingestion (Flash), and deep analysis (Pro).
- **Z.ai GLM 5.1**: Specialized agent for high-fidelity financial reasoning and complex decision-making.

## Data & Storage
- **SQLite**: Local, auditable database for storing news, sentiment scores, trade rationale, and execution history.
- **Environment Variables (.env)**: Secure management of API keys and project secrets.

## Financial APIs
- **Alpaca API**: Real-time market data, news streaming, and Paper Trading execution.
- **Financial Datasets / EODHD**: Potential MCP sources for enriched market and corporate data.
- **GDELT**: Global open-source news feed for geopolitical context.

## Infrastructure & Tooling
- **Python venv**: Isolated virtual environments for dependency management.
- **Git**: Version control for scripts, agent "skills", and project configuration.
- **MCP (Model Context Protocol)**: Connectivity framework between Claude Code and external data sources.