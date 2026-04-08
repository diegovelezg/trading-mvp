"""Macro Analyst Agent: News ingestion and sentiment analysis.

This subagent ingests high-volume market news from Alpaca and synthesizes
sentiment scores using Gemini AI to inform trading hypotheses.
"""

from .agent import ingest_and_analyze, main

__all__ = ["ingest_and_analyze", "main"]
