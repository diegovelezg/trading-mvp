# Project Workflow (Quant-Mental Edition)

## Strategic Hierarchy
1.  **Orchestrator (Ops Manager):** Orchestrates the flow, handles subagent loading, and ensures data is passed correctly between steps.
2.  **Desk Subagents (Analysts):** Perform specialized analysis on multiple candidates (Batch processing).
3.  **CIO (The Decision Maker):** Strategic synthesis using GLM-5.1. Decides which asset to trade based on conviction and risk.
4.  **Portfolio Guardrails (Compliance):** Deterministic Python logic that enforces capital limits.

## Standard Execution Workflow

### 1. Discovery & Thematic Selection
*   **Explorer/Scout** identifies a list of 3-5 tickers matching the theme.
*   **Macro Analyst** assesses the general market regime (SMA 200, SPY performance).

### 2. Multi-Ticker Batch Analysis
The Orchestrator passes the selected tickers through the Desk in parallel:
*   **Sentiment Engine:** Extracts news and AI-generated sentiment scores.
*   **Quantitative Engine:** Calculates RSI, SMA, Beta, and ATR for each ticker.
*   **Dialectical Review:** Bull and Bear researchers provide arguments for/against each ticker.
*   **Risk Profile:** Risk Manager calculates ATR-based stop losses and position feasibility.

### 3. CIO Strategic Decision (GLM-5.1)
The CIO receives the "Full Desk Report" and makes a high-level decision:
*   **Synthesis:** Balances Bullish sentiment against technical overbought/oversold conditions (RSI).
*   **Selection:** Picks the single highest-probability candidate from the batch.
*   **Sizing:** Determines the investment amount in USD.

### 4. Deterministic Guardrail Check
Before passing the order to the Executioner, the system calls `portfolio_logic.py`:
*   Validates available cash.
*   Checks for sector and ticker concentration limits.
*   **Auto-scaling:** If the CIO requests $2,000 but the limit is $1,200, the system automatically adjusts the size.

### 5. Execution & Logging
*   **Executioner** places the order on Alpaca (Paper Trading).
*   **Audit Trail:** The full CIO rationale, desk analyses, and quant stats are saved to the SQLite database for post-mortem analysis.
