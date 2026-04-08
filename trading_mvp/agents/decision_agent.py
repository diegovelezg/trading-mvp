"""Decision Agent: Autonomous investment decision making.

Este agente:
- Analiza recomendaciones de la mesa de inversiones
- Toma decisiones automáticas basadas en reglas
- Gestiona posición sizing y risk parameters
- Puede estar en modo AUTOPILOT o MANUAL
- **EJECUTA ÓRDENES REALES en Alpaca Paper Trading**
- Registra todas las decisiones automáticamente

MODO AUTOPILOT: El agente decide, ejecuta y registra automáticamente
MODO MANUAL: El agente sugiere pero el usuario decide
"""

import os
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Import execution module for Alpaca
try:
    from trading_mvp.execution.alpaca_orders import (
        submit_order,
        get_positions,
        get_account
    )
    ALPACA_EXECUTION_AVAILABLE = True
    logger.info("✅ Alpaca Paper Trading execution available")
except ImportError as e:
    ALPACA_EXECUTION_AVAILABLE = False
    logger.warning(f"⚠️  Alpaca execution not available: {e}")
    logger.warning("   Decisions will be recorded but NOT executed")


@dataclass
class DecisionConfig:
    """Configuración del Decision Agent."""

    # Mode
    autopilot_enabled: bool = False  # ON/OFF switch

    # Risk parameters
    max_position_size: float = 10000.0  # Max USD per position
    max_portfolio_risk: float = 0.02  # 2% max portfolio risk
    default_stop_loss_pct: float = 0.05  # 5% stop loss
    default_take_profit_pct: float = 0.10  # 10% take profit

    # Decision rules
    min_confidence_for_buy: float = 0.80  # Minimum confidence to FOLLOW buy rec
    min_confidence_for_sell: float = 0.75  # Minimum confidence to FOLLOW sell rec
    min_positive_ratio_for_bullish: float = 0.60  # Min 60% positive for BULLISH
    max_negative_ratio_for_bullish: float = 0.30  # Max 30% negative for BULLISH

    # Position sizing
    position_sizing_method: str = "kelly"  # kelly, fixed, volatility_based
    base_position_size: float = 5000.0  # Base size for fixed method

    # Diversification
    max_positions_per_sector: int = 3
    max_total_positions: int = 10

    # Execution
    dry_run: bool = True  # If True, don't actually execute (for testing)


class DecisionAgent:
    """Agente que toma decisiones de inversión autónomas."""

    def __init__(self, config: DecisionConfig = None):
        """Initialize decision agent.

        Args:
            config: Decision configuration (uses defaults if None)
        """

        self.config = config or DecisionConfig()
        self.decision_history = []

        # Check environment variable for autopilot mode
        autopilot_env = os.getenv("AUTOPILOT_MODE", "off").lower()
        if autopilot_env == "on":
            self.config.autopilot_enabled = True
            logger.warning("🤖 AUTOPILOT MODE ENABLED - Agent will make decisions automatically")
        else:
            logger.info("👨‍💼 MANUAL MODE - Agent will suggest decisions only")

        logger.info(f"✅ DecisionAgent initialized (autopilot: {self.config.autopilot_enabled})")

    def analyze_recommendation(
        self,
        ticker_analysis: Dict,
        portfolio_context: Dict = None
    ) -> Dict:
        """Analiza una recomendación y decide acción.

        Args:
            ticker_analysis: Ticker analysis from investment desk
            portfolio_context: Current portfolio state (optional)

        Returns:
            Decision with action, rationale, and execution details
        """

        ticker = ticker_analysis['ticker']
        recommendation = ticker_analysis['recommendation']
        confidence = ticker_analysis['avg_confidence']
        positive_ratio = ticker_analysis['positive_ratio']
        negative_ratio = ticker_analysis['negative_ratio']

        logger.info(f"🤔 Analyzing recommendation for {ticker}: {recommendation}")
        logger.info(f"   Confidence: {confidence:.2f} | Positive: {positive_ratio:.1%} | Negative: {negative_ratio:.1%}")

        # Determine if we should FOLLOW this recommendation
        decision = self._make_decision(
            ticker=ticker,
            recommendation=recommendation,
            confidence=confidence,
            positive_ratio=positive_ratio,
            negative_ratio=negative_ratio,
            ticker_analysis=ticker_analysis,
            portfolio_context=portfolio_context or {}
        )

        # Add metadata
        decision['ticker_analysis_id'] = ticker_analysis.get('id')
        decision['ticker'] = ticker
        decision['original_recommendation'] = recommendation
        decision['analysis_timestamp'] = ticker_analysis['analysis_timestamp']
        decision['decision_timestamp'] = datetime.now().isoformat()

        self.decision_history.append(decision)

        return decision

    def _make_decision(
        self,
        ticker: str,
        recommendation: str,
        confidence: float,
        positive_ratio: float,
        negative_ratio: float,
        ticker_analysis: Dict,
        portfolio_context: Dict
    ) -> Dict:
        """Core decision logic.

        Args:
            ticker: Ticker symbol
            recommendation: Original recommendation (BULLISH/BEARISH/CAUTIOUS)
            confidence: Average confidence
            positive_ratio: Positive entity ratio
            negative_ratio: Negative entity ratio
            ticker_analysis: Full ticker analysis
            portfolio_context: Portfolio state

        Returns:
            Decision dict with action, rationale, execution details
        """

        # Extract additional context
        top_risks = ticker_analysis.get('top_risks', [])
        top_opportunities = ticker_analysis.get('top_opportunities', [])
        news_count = ticker_analysis.get('related_news_count', 0)
        entities_found = ticker_analysis.get('unique_entities_found', 0)

        # Decision matrix
        if recommendation == "BULLISH":
            return self._handle_bullish(
                ticker=ticker,
                confidence=confidence,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                top_risks=top_risks,
                top_opportunities=top_opportunities,
                news_count=news_count,
                entities_found=entities_found,
                portfolio_context=portfolio_context
            )

        elif recommendation == "BEARISH":
            return self._handle_bearish(
                ticker=ticker,
                confidence=confidence,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                top_risks=top_risks,
                top_opportunities=top_opportunities,
                news_count=news_count,
                entities_found=entities_found,
                portfolio_context=portfolio_context
            )

        else:  # CAUTIOUS or NEUTRAL
            return self._handle_cautious(
                ticker=ticker,
                confidence=confidence,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                top_risks=top_risks,
                top_opportunities=top_opportunities,
                news_count=news_count,
                entities_found=entities_found,
                portfolio_context=portfolio_context
            )

    def _handle_bullish(
        self,
        ticker: str,
        confidence: float,
        positive_ratio: float,
        negative_ratio: float,
        top_risks: List,
        top_opportunities: List,
        news_count: int,
        entities_found: int,
        portfolio_context: Dict
    ) -> Dict:
        """Handle BULLISH recommendation."""

        # Check if criteria met to FOLLOW
        strong_signal = (
            confidence >= self.config.min_confidence_for_buy and
            positive_ratio >= self.config.min_positive_ratio_for_bullish and
            negative_ratio <= self.config.max_negative_ratio_for_bullish
        )

        if strong_signal:
            # Calculate position size
            position_size, entry_price = self._calculate_position_size(
                ticker=ticker,
                confidence=confidence,
                portfolio_context=portfolio_context
            )

            decision = {
                'decision': 'FOLLOWED',
                'action': 'BOUGHT',
                'position_size': position_size,
                'entry_price': entry_price,
                'rationale': self._generate_bullish_rationale(
                    confidence, positive_ratio, negative_ratio,
                    top_opportunities, news_count, entities_found
                ),
                'stop_loss': entry_price * (1 - self.config.default_stop_loss_pct),
                'take_profit': entry_price * (1 + self.config.default_take_profit_pct),
                'confidence_in_decision': confidence,
                'risk_level': self._assess_risk_level(top_risks, negative_ratio)
            }

            logger.info(f"   ✅ DECISION: FOLLOWED - BUY {ticker}")
            logger.info(f"      Size: ${position_size:.2f} @ ${entry_price:.2f}")
            logger.info(f"      Stop: ${decision['stop_loss']:.2f} | Target: ${decision['take_profit']:.2f}")

            # EXECUTE ORDER IN ALPACA (if autopilot and not dry_run)
            if self.config.autopilot_enabled and not self.config.dry_run:
                if ALPACA_EXECUTION_AVAILABLE:
                    decision = self._execute_buy_order(
                        ticker=ticker,
                        position_size=position_size,
                        entry_price=entry_price,
                        decision=decision
                    )
                else:
                    logger.warning("   ⚠️  Alpaca execution not available - recording decision only")
            else:
                if self.config.dry_run:
                    logger.info(f"   🧪 DRY RUN MODE - Order NOT executed (testing)")

        else:
            # Signal not strong enough
            reasons = []
            if confidence < self.config.min_confidence_for_buy:
                reasons.append(f"low confidence ({confidence:.2f} < {self.config.min_confidence_for_buy})")
            if positive_ratio < self.config.min_positive_ratio_for_bullish:
                reasons.append(f"weak positive sentiment ({positive_ratio:.1%})")
            if negative_ratio > self.config.max_negative_ratio_for_bullish:
                reasons.append(f"high negative sentiment ({negative_ratio:.1%})")

            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"BULLISH signal but criteria not met: {', '.join(reasons)}",
                'confidence_in_decision': confidence * 0.5,  # Lower confidence when ignoring
                'risk_level': 'low'
            }

            logger.info(f"   ⚠️  DECISION: IGNORED - {decision['rationale']}")

        return decision

    def _handle_bearish(
        self,
        ticker: str,
        confidence: float,
        positive_ratio: float,
        negative_ratio: float,
        top_risks: List,
        top_opportunities: List,
        news_count: int,
        entities_found: int,
        portfolio_context: Dict
    ) -> Dict:
        """Handle BEARISH recommendation."""

        # Check if we should AVOID
        strong_signal = (
            confidence >= self.config.min_confidence_for_sell and
            negative_ratio >= 0.60  # At least 60% negative
        )

        if strong_signal:
            decision = {
                'decision': 'FOLLOWED',
                'action': 'NONE',  # Avoid/Don't buy
                'rationale': self._generate_bearish_rationale(
                    confidence, negative_ratio, top_risks, news_count
                ),
                'confidence_in_decision': confidence,
                'risk_level': 'high'
            }

            logger.info(f"   ❌ DECISION: FOLLOWED - AVOID {ticker}")
        else:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"BEARISH signal but weak (confidence: {confidence:.2f})",
                'confidence_in_decision': confidence * 0.5,
                'risk_level': 'medium'
            }

            logger.info(f"   ⚠️  DECISION: IGNORED - {decision['rationale']}")

        return decision

    def _handle_cautious(
        self,
        ticker: str,
        confidence: float,
        positive_ratio: float,
        negative_ratio: float,
        top_risks: List,
        top_opportunities: List,
        news_count: int,
        entities_found: int,
        portfolio_context: Dict
    ) -> Dict:
        """Handle CAUTIOUS/NEUTRAL recommendation."""

        # For cautious, we generally WATCH
        decision = {
            'decision': 'FOLLOWED',
            'action': 'NONE',
            'rationale': f"CAUTIOUS recommendation - monitoring needed. Mixed signals (positive: {positive_ratio:.1%}, negative: {negative_ratio:.1%})",
            'confidence_in_decision': confidence,
            'risk_level': 'medium'
        }

        logger.info(f"   👀 DECISION: FOLLOWED - WATCH {ticker}")

        return decision

    def _calculate_position_size(
        self,
        ticker: str,
        confidence: float,
        portfolio_context: Dict
    ) -> Tuple[float, float]:
        """Calculate position size and entry price.

        Args:
            ticker: Ticker symbol
            confidence: Analysis confidence
            portfolio_context: Portfolio state

        Returns:
            (position_size_usd, entry_price)
        """

        # For now, use simplified fixed sizing with confidence adjustment
        # In production, this would use real-time price data
        base_size = self.config.base_position_size

        # Adjust by confidence
        confidence_multiplier = confidence / 0.90  # Normalize to 0.90 baseline
        position_size = min(
            base_size * confidence_multiplier,
            self.config.max_position_size
        )

        # Estimate entry price (in production, get from real-time data)
        # For energy stocks, use rough estimate
        estimated_prices = {
            'COP': 98.0,
            'USO': 75.0,
            'XLE': 85.0,
            'XOP': 110.0,
            'BNO': 25.0,
            'CVE': 18.0
        }

        entry_price = estimated_prices.get(ticker, 50.0)

        return position_size, entry_price

    def _generate_bullish_rationale(
        self,
        confidence: float,
        positive_ratio: float,
        negative_ratio: float,
        opportunities: List,
        news_count: int,
        entities_found: int
    ) -> str:
        """Generate rationale for BULLISH decision."""

        rationale_parts = [
            f"Strong BULLISH signal (confidence: {confidence:.2f})",
            f"Positive sentiment dominates ({positive_ratio:.1%} vs {negative_ratio:.1%} negative)"
        ]

        if opportunities:
            top_opp = opportunities[0].get('entity_name', 'N/A') if isinstance(opportunities[0], dict) else opportunities[0]
            rationale_parts.append(f"Key opportunity: {top_opp}")

        rationale_parts.append(f"Based on {news_count} news items and {entities_found} entities")

        return ". ".join(rationale_parts) + "."

    def _generate_bearish_rationale(
        self,
        confidence: float,
        negative_ratio: float,
        risks: List,
        news_count: int
    ) -> str:
        """Generate rationale for BEARISH decision."""

        rationale_parts = [
            f"Strong BEARISH signal (confidence: {confidence:.2f})",
            f"Negative sentiment elevated ({negative_ratio:.1%})"
        ]

        if risks:
            top_risk = risks[0].get('entity_name', 'N/A') if isinstance(risks[0], dict) else risks[0]
            rationale_parts.append(f"Key risk: {top_risk}")

        rationale_parts.append(f"Based on {news_count} news items")

        return ". ".join(rationale_parts) + "."

    def _assess_risk_level(self, risks: List, negative_ratio: float) -> str:
        """Assess overall risk level."""

        high_risk_count = sum(1 for r in risks if isinstance(r, dict) and r.get('overall_impact') == 'negative')

        if high_risk_count >= 3 or negative_ratio >= 0.60:
            return 'high'
        elif high_risk_count >= 1 or negative_ratio >= 0.40:
            return 'medium'
        else:
            return 'low'

    def _execute_buy_order(
        self,
        ticker: str,
        position_size: float,
        entry_price: float,
        decision: Dict
    ) -> Dict:
        """Execute buy order in Alpaca Paper Trading.

        Args:
            ticker: Ticker symbol
            position_size: Position size in USD
            entry_price: Estimated entry price
            decision: Decision dict to update

        Returns:
            Updated decision dict with execution details
        """

        logger.info(f"   💰 Executing BUY order in Alpaca Paper Trading...")

        try:
            # Calculate shares (round down to whole number)
            shares = int(position_size / entry_price)

            if shares < 1:
                logger.warning(f"   ⚠️  Position size too small for 1 share ({position_size:.2f} / {entry_price:.2f} = {shares:.2f} shares)")
                decision['execution_status'] = 'FAILED'
                decision['execution_error'] = 'Position size too small'
                return decision

            logger.info(f"   📊 Submitting order: {shares} shares of {ticker} @ market")

            # Submit market order
            order_result = submit_order(
                symbol=ticker,
                qty=shares,
                side='buy',
                order_type='market'
            )

            logger.info(f"   ✅ Order submitted successfully")
            logger.info(f"      Order ID: {order_result['order_id']}")
            logger.info(f"      Status: {order_result['status']}")

            # Update decision with execution details
            decision['execution_status'] = 'SUCCESS'
            decision['order_id'] = order_result['order_id']
            decision['shares'] = shares
            decision['actual_price'] = entry_price  # Will be updated when filled
            decision['execution_timestamp'] = datetime.now().isoformat()

            # Note: Stop loss and take profit would need to be handled separately
            # Alpaca doesn't support OCO orders natively
            logger.info(f"   📝 NOTE: Stop loss (${decision['stop_loss']:.2f}) and take profit (${decision['take_profit']:.2f}) need to be monitored manually")

        except Exception as e:
            logger.error(f"   ❌ Order execution failed: {e}")
            decision['execution_status'] = 'FAILED'
            decision['execution_error'] = str(e)

        return decision

    def process_desk_recommendations(
        self,
        desk_analysis: Dict,
        portfolio_context: Dict = None
    ) -> List[Dict]:
        """Process all recommendations from investment desk.

        Args:
            desk_analysis: Full desk analysis
            portfolio_context: Current portfolio state

        Returns:
            List of decisions for each ticker
        """

        logger.info("")
        logger.info("="*70)
        logger.info("🤖 DECISION AGENT - PROCESSING DESK RECOMMENDATIONS")
        logger.info("="*70)
        logger.info(f"Mode: {'AUTOPILOT' if self.config.autopilot_enabled else 'MANUAL'}")
        logger.info("")

        ticker_results = desk_analysis.get('ticker_results', [])
        decisions = []

        for ticker_analysis in ticker_results:
            ticker = ticker_analysis['ticker']

            logger.info(f"📊 Processing {ticker}...")

            decision = self.analyze_recommendation(
                ticker_analysis=ticker_analysis,
                portfolio_context=portfolio_context or {}
            )

            decisions.append(decision)

            logger.info("")

        # Summary
        logger.info("="*70)
        logger.info("📋 DECISION SUMMARY")
        logger.info("="*70)

        action_counts = {}
        for d in decisions:
            action = d['action']
            action_counts[action] = action_counts.get(action, 0) + 1

        for action, count in action_counts.items():
            logger.info(f"   {action}: {count}")

        logger.info("="*70)
        logger.info("")

        return decisions


def create_decision_agent(config: DecisionConfig = None) -> DecisionAgent:
    """Factory function to create decision agent.

    Args:
        config: Optional configuration

    Returns:
        Configured DecisionAgent
    """

    return DecisionAgent(config=config)


# Default configuration
DEFAULT_CONFIG = DecisionConfig(
    autopilot_enabled=False,  # Default to manual
    max_position_size=10000.0,
    max_portfolio_risk=0.02,
    default_stop_loss_pct=0.05,
    default_take_profit_pct=0.10,
    min_confidence_for_buy=0.80,
    min_confidence_for_sell=0.75,
    min_positive_ratio_for_bullish=0.60,
    max_negative_ratio_for_bullish=0.30,
    position_sizing_method="fixed",
    base_position_size=5000.0,
    max_positions_per_sector=3,
    max_total_positions=10,
    dry_run=False  # Execute in Alpaca Paper Trading by default
)
