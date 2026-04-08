# Initial Concept

QUIERO CONTRUIR UN ENTORNO CON SCRIPTS, SKILLS, BD ETC ETC PARA QUE SISTEMAS MULTIAGENTE QUE SE EJECUTEN MEDIANTE CLAUDE-CODE O GEMINI-CLI SE ENCARGUEN DE LAS EJECUCIONES Y DE LA GENERACIÓN DE REPORTES, SEÑALES, ETC. POR AOHRA NO NECESITAMOS UNA UI, NI NADA, TODO LO MANEJAREMOS MEDIANTE CLIS

---

# Product Definition: Agentic Trading MVP

## Vision
To build a highly modular, multi-agent "Mesa de Inversión" (Investment Desk) where specialized AI agents handle the end-to-end lifecycle of trading: from geopolitical news analysis to automated execution and reporting. This project emulates institutional trading desk dynamics using Claude Code and Gemini CLI as the primary interfaces.

## Core Objectives
1. **Multi-Agent "Mesa de Inversión"**: Implement a specialized multi-agent framework (inspired by TradingAgents) where roles are clearly defined: Explorer/Scout, Macro Analyst, Hypothesis Generator, Bull/Bear Researchers, Risk Manager, and Executioner.
2. **Context-Driven Trading**: Leverage LLMs (Gemini 3 Flash/Pro, Z.ai GLM 5.1) to analyze geopolitical events and corporate news (e.g., Google News, Alpaca, SEC filings) to inform trading decisions.
3. **CLI-First Experience**: All interactions, status reports, and controls are managed via command-line tools (Claude Code, Gemini CLI).
4. **Persistent Memory & Auditing**: Use SQLite as a lightweight, auditable storage for news, sentiment scores, and trade rationale.

## Key Features
- **Investment Desk Roles**: Specialized agents collaborating through dialectical processes (Bull vs. Bear) to synthesize information and mitigate bias.
- **Automated News Ingestion**: Continuous monitoring of news sources (GDELT, SEC, etc.) using Gemini 3 Flash for high-volume, low-cost processing.
- **Agentic Hypothesis Testing**: Deep analysis of market events by Gemini 3 Pro and Z.ai GLM 5.1 to formulate actionable investment strategies.
- **Paper Trading Execution**: Seamless integration with Alpaca API for executing orders based on agent consensus.
- **Self-Reporting Engine**: Automated generation of "Trade Cards" and performance reports directly in the terminal.

## Target Audience
- **Agentic Traders**: Developers and investors looking for an autonomous, extensible, and high-performance trading setup.
- **AI Researchers**: Users exploring the intersection of LLM reasoning and financial markets.

## Scope (Iteration 1)
- **Multi-Agent Scaffolding (In Progress)**: Setup of the basic "Mesa de Inversión" agent communication and workflow. Explorer and Macro Analyst roles established.
- **Dynamic Watchlist Management**: Support for defining and switching between different segments, groups, or research lines (e.g., "Power", "Small Caps", "Geopolitical Trends").
- **SQLite Core Implementation (Done)**: Database initialization and schema setup to store modular research logs, news, and trade data.
- **Alpaca News & Execution (Partial)**: Scripts for connecting to Alpaca (Paper Trading) and fetching context-aware news.
- **CLI Reports**: Initial generation of "Trade Cards" and terminal-based status summaries.