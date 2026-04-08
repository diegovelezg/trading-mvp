# Specification: Explorer/Scout Agent

## Goal
Establish a specialized "Explorer" or "Scout" agent that can take a thematic idea (e.g., "Small caps in gas and nuclear energy") and identify a cluster of related tickers. These clusters can then be passed to the Macro Analyst for deeper investigation.

## Components
1. **Explorer Agent (`explorer_agent.py`)**:
    - Takes a natural language prompt (thematic).
    - Uses Gemini 2.0 Flash (or Pro for deeper research) to brainstorm and search for companies matching the theme.
    - Extracts ticker symbols for the identified companies.
    - Verifies ticker validity (optional but recommended via Alpaca or web search).
2. **Cluster Export**:
    - Standardized output format (JSON/List of tickers).
    - Ability to trigger the `Macro Analyst` with the generated cluster.
3. **Storage**:
    - Log exploration results in `trading.db` (new `explorations` table).

## Success Criteria
- [ ] `explorer_agent.py` can generate a list of relevant tickers from a thematic prompt.
- [ ] Integration with Gemini to discover companies not already in the watchlist.
- [ ] Every exploration and identified cluster is logged in SQLite.
- [ ] Explorer can successfully "feed" a list of symbols to the `macro_analyst.py`.
- [ ] Code coverage for new modules exceeds 80%.
