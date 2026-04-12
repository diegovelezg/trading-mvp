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
    from trading_mvp.core.portfolio_logic import validate_trade_size
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
        
        # Load Risk Parameters from .env if available
        env_min_conf = os.getenv("MIN_CONFIDENCE_SCORE")
        if env_min_conf:
            try:
                conf_val = float(env_min_conf)
                self.config.min_confidence_for_buy = conf_val
                self.config.min_confidence_for_sell = conf_val * 0.9  # Sell slightly more sensitive
                logger.info(f"🛡️ Loaded MIN_CONFIDENCE_SCORE from env: {conf_val}")
            except ValueError:
                pass

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

    def _calculate_quant_score(self, quant_stats: Dict) -> Tuple[float, str]:
        """Calculates a normalized 0-1 score based on the 11 quant indicators.
        
        Returns: (score, summary)
        """
        if not quant_stats or 'error' in quant_stats:
            return 0.5, "Insufficient quant data"

        score = 0.0
        details = []

        # I. STRUCTURE (Weight: 0.25)
        struct_score = 0.0
        if quant_stats.get('trend') == 'BULLISH': struct_score += 0.4
        if quant_stats.get('momentum') == 'POSITIVE': struct_score += 0.3
        # Price to SMA 200 distance - reward being above, but not TOO far (mean reversion)
        dist = quant_stats.get('price_to_sma200_dist', 0)
        if 0 < dist < 15: struct_score += 0.3
        elif 15 <= dist < 30: struct_score += 0.2
        elif dist >= 30: struct_score += 0.1 # Overextended
        
        score += struct_score * 0.25
        details.append(f"Structure: {struct_score:.2f}")

        # II. MOMENTUM (Weight: 0.20)
        mom_score = 0.0
        rsi = quant_stats.get('rsi_14', 50)
        if 40 <= rsi <= 60: mom_score += 0.5 # Healthy momentum
        elif 30 <= rsi < 40 or 60 < rsi <= 70: mom_score += 0.3
        
        macd = quant_stats.get('macd', {})
        if macd.get('histogram', 0) > 0: mom_score += 0.5
        
        score += mom_score * 0.20
        details.append(f"Momentum: {mom_score:.2f}")

        # III. CONVICTION (Weight: 0.15)
        conv_score = 0.0
        rvol = quant_stats.get('rvol')

        # Handle None RVOL (insufficient volume data)
        if rvol is None:
            conv_score = 0.0
            logger.info("   ⚠️  RVOL UNAVAILABLE (insufficient volume data). Invalidating conviction score.")
        elif rvol > 1.2:
            conv_score += 1.0
        elif rvol >= 1.0:
            conv_score += 0.5
        else:
            # Harsh penalty for low volume (RVOL < 1.0)
            conv_score = 0.0
            logger.info(f"   ⚠️  LOW VOLUME DETECTED (RVOL: {rvol:.2f}). Invalidating conviction score.")

        score += conv_score * 0.15
        details.append(f"Conviction: {conv_score:.2f}")

        # IV. VOLATILITY (Weight: 0.20)
        vol_score = 1.0 # Start with perfect score, penalize risk
        vol_ratio = quant_stats.get('volatility_ratio')

        if vol_ratio is not None:
            if vol_ratio > 10: vol_score -= 0.6 # Too volatile
            elif vol_ratio > 5: vol_score -= 0.3
        else:
            # No volatility data available - neutral score
            vol_score = 0.5
            logger.info("   ⚠️  Volatility ratio unavailable (ATR calculation failed). Using neutral score.")

        # Penalize momentum if volume is missing or low
        if rvol is not None and rvol < 1.0:
            mom_score *= 0.5
            logger.info("   ⚠️  Reducing Momentum score by 50% due to lack of volume confirmation.")

        score += vol_score * 0.20
        details.append(f"Volatility: {vol_score:.2f}")

        # V. SENSITIVITY (Weight: 0.20)
        sens_score = 0.0
        beta = quant_stats.get('beta_spy')
        corr = quant_stats.get('corr_spy_20d')

        # Handle None values for Beta/Correlation
        if beta is None or corr is None:
            # No sensitivity data available - neutral score
            sens_score = 0.5
            details.append(f"Sensitivity: N/A (no SPY data)")
        else:
            # We prefer lower beta and moderate correlation for stability
            if beta < 1.0: sens_score += 0.5
            if abs(corr) < 0.7: sens_score += 0.5 # Some decoupling is good for Alpha
            details.append(f"Sensitivity: {sens_score:.2f}")

        score += sens_score * 0.20

        summary = ", ".join(details)
        return round(score, 2), summary

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
        """Core decision logic using 60/40 Weighted Model.
        
        Quant (60%) + LLM/Context (40%)
        """

        # 1. Get LLM Score (0-1) from sentiment ratios
        llm_score = (positive_ratio * 0.7) + (confidence * 0.3)
        if negative_ratio > 0.4: llm_score *= (1 - negative_ratio)
        
        # 2. Get Quant Score (0-1) from the 11 indicators
        quant_stats = ticker_analysis.get('quant_stats', {})
        quant_score, quant_summary = self._calculate_quant_score(quant_stats)

        # 3. Final Weighted Score
        final_score = (quant_score * 0.6) + (llm_score * 0.4)
        
        # ALIGNMENT CHECK (Feedback 3): Final score should not exceed confidence by much
        if final_score > (confidence * 1.1):
            logger.warning(f"   ⚖️  Final score ({final_score:.2f}) over-extended vs Confidence ({confidence:.2f}). Clipping to {confidence*1.1:.2f}")
            final_score = min(final_score, confidence * 1.1)
        
        logger.info(f"⚖️  Weighted Model for {ticker}:")
        logger.info(f"   - Quant (60%): {quant_score:.2f} ({quant_summary})")
        logger.info(f"   - LLM/Context (40%): {llm_score:.2f}")
        logger.info(f"   - FINAL SCORE: {final_score:.2f}")

        # 4. Handle Decision based on Final Score
        top_risks = ticker_analysis.get('top_risks', [])
        top_opportunities = ticker_analysis.get('top_opportunities', [])
        news_count = ticker_analysis.get('related_news_count', 0)
        entities_found = ticker_analysis.get('unique_entities_found', 0)

        # Context for handlers
        portfolio_context['quant_stats'] = quant_stats
        portfolio_context['weighted_score'] = final_score
        portfolio_context['sentiment_score'] = getattr(ticker_analysis, 'get', lambda k, d: 0.0)('sentiment_score', 0.0) # Safety fetch

        # Decisions based on final score thresholds
        decision = None
        if final_score >= 0.75:
            decision = self._handle_bullish(
                ticker=ticker,
                confidence=final_score, 
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                top_risks=top_risks,
                top_opportunities=top_opportunities,
                news_count=news_count,
                entities_found=entities_found,
                portfolio_context=portfolio_context
            )
        elif final_score <= 0.35:
            decision = self._handle_bearish(
                ticker=ticker,
                confidence=1.0 - final_score,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                top_risks=top_risks,
                top_opportunities=top_opportunities,
                news_count=news_count,
                entities_found=entities_found,
                portfolio_context=portfolio_context
            )
        else:
            decision = self._handle_cautious(
                ticker=ticker,
                confidence=final_score,
                positive_ratio=positive_ratio,
                negative_ratio=negative_ratio,
                top_risks=top_risks,
                top_opportunities=top_opportunities,
                news_count=news_count,
                entities_found=entities_found,
                portfolio_context=portfolio_context
            )
        
        # FINAL ENRICHMENT FOR UI
        decision['sentiment_score'] = ticker_analysis.get('sentiment_score', 0.0)
        decision['confidence_in_decision'] = final_score
        
        return decision

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
        """Handle BULLISH recommendation with technical filters and exposure check."""

        # 1. Check for EXISTING EXPOSURE (Live + Pending)
        positions = portfolio_context.get('positions', [])
        orders = portfolio_context.get('orders', [])
        
        current_pos = next((p for p in positions if p['symbol'] == ticker), None)
        pending_buy = next((o for o in orders if o['symbol'] == ticker and o['side'].lower() == 'buy'), None)
        
        if pending_buy:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"Already have a PENDING BUY order for {ticker}. Avoiding over-exposure.",
                'confidence_in_decision': confidence,
                'risk_level': 'low'
            }
            logger.info(f"   🛡️  DECISION: IGNORED - {decision['rationale']}")
            return decision

        if current_pos:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"Already have a LIVE position in {ticker}. To increase size, use manual adjustment.",
                'confidence_in_decision': confidence,
                'risk_level': 'low'
            }
            logger.info(f"   🛡️  DECISION: IGNORED - {decision['rationale']}")
            return decision

        # 2. Extract technical data
        quant_stats = portfolio_context.get('quant_stats', {}) 
        rsi = quant_stats.get('rsi_14', 50)
        atr = quant_stats.get('atr_14', 0)
        trend = quant_stats.get('trend', 'UNKNOWN')

        # 3. Basic criteria (Now using the 60/40 Weighted Score via 'confidence')
        # We assume 'confidence' passed here IS the weighted final_score
        strong_signal = confidence >= self.config.min_confidence_for_buy

        # 4. TECHNICAL FILTERS
        technical_rejection = None
        if rsi > 75:
            technical_rejection = f"Asset is OVERBOUGHT (RSI: {rsi:.1f})"
        elif trend == "BEARISH":
            # Optional: Allow buying against trend but with lower confidence
            confidence *= 0.8
            logger.info(f"   ⚠️  Buying against trend (Price < SMA 200). Reducing confidence.")

        if strong_signal and not technical_rejection:
            # Calculate position size
            position_size, entry_price = self._calculate_position_size(
                ticker=ticker,
                confidence=confidence,
                portfolio_context=portfolio_context
            )

            if position_size <= 0:
                return {
                    'decision': 'IGNORED',
                    'action': 'NONE',
                    'rationale': f"Risk Manager rejected trade size for {ticker}: {getattr(self, 'last_risk_reason', 'Unknown reason')}",
                    'confidence_in_decision': confidence,
                    'risk_level': 'high'
                }

            # 5. DYNAMIC VOLATILITY STOP LOSS (Feedback 2)
            # Use 1.5x ATR below entry price, with a 7% max cap for safety
            if atr > 0:
                stop_loss = entry_price - (1.5 * atr)
                logger.info(f"   🛡️  Dynamic Stop Loss (1.5x ATR): ${stop_loss:.2f}")
                take_profit = entry_price + (3.0 * atr) # 1:2 R/R
            else:
                # Conservative fallback for volatile energy stocks (7% instead of 5%)
                stop_loss = entry_price * (1 - 0.07)
                take_profit = entry_price * (1 + 0.15)
                logger.warning(f"   ⚠️  ATR not available. Using 7% fixed stop: ${stop_loss:.2f}")

            decision = {
                'decision': 'FOLLOWED',
                'action': 'BOUGHT',
                'position_size': position_size,
                'entry_price': entry_price,
                'rationale': self._generate_bullish_rationale(
                    confidence, positive_ratio, negative_ratio,
                    top_opportunities, news_count, entities_found
                ),
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
                'confidence_in_decision': confidence,
                'risk_level': self._assess_risk_level(top_risks, negative_ratio),
                'risk_guardrail': getattr(self, 'last_risk_reason', 'Passed all guardrails'),
                'technical_context': f"RSI: {rsi:.1f}, ATR: ${atr:.2f}, Trend: {trend}"
            }

            logger.info(f"   ✅ DECISION: FOLLOWED - BUY {ticker}")
            
            # EXECUTE ORDER
            if self.config.autopilot_enabled and not self.config.dry_run:
                if ALPACA_EXECUTION_AVAILABLE:
                    decision = self._execute_buy_order(ticker, position_size, entry_price, decision)
            
        elif technical_rejection:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"BULLISH sentiment but TECHNICAL REJECTION: {technical_rejection}",
                'confidence_in_decision': 0.0,
                'risk_level': 'high'
            }
            logger.warning(f"   🛡️  DECISION: IGNORED - {decision['rationale']}")
        else:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"BULLISH signal but final score ({confidence:.2f}) < threshold",
                'confidence_in_decision': confidence,
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
        """Handle BEARISH recommendation with Sell-Off capability and pending check."""

        # 1. Check for EXISTING POSITIONS and PENDING SELLS
        positions = portfolio_context.get('positions', [])
        orders = portfolio_context.get('orders', [])
        
        current_pos = next((p for p in positions if p['symbol'] == ticker), None)
        pending_sell = next((o for o in orders if o['symbol'] == ticker and o['side'].lower() == 'sell'), None)
        
        if pending_sell:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"Already have a PENDING SELL order for {ticker}. Avoiding redundant sell.",
                'confidence_in_decision': confidence,
                'risk_level': 'low'
            }
            logger.info(f"   🛡️  DECISION: IGNORED - {decision['rationale']}")
            return decision

        # 2. Check if we should SELL or AVOID
        # Using confidence as the (1.0 - final_score) or similar from handle_bearish
        strong_sell_signal = confidence >= self.config.min_confidence_for_sell

        if current_pos and strong_sell_signal:
            # LIQUIDATE POSITION
            qty = current_pos['qty']
            quant = portfolio_context.get('quant_stats', {})
            decision = {
                'decision': 'FOLLOWED',
                'action': 'SOLD',
                'shares': qty,
                'rationale': f"Strong BEARISH weighted signal ({confidence:.2f}). Negative ratio {negative_ratio:.0%}. Technicals: RSI {quant.get('rsi_14', 'N/A')}. LIQUIDATING {qty} shares.",
                'confidence_in_decision': confidence,
                'risk_level': 'high'
            }

            logger.warning(f"   🚨 DECISION: FOLLOWED - SELL {ticker}")

            if self.config.autopilot_enabled and not self.config.dry_run:
                if ALPACA_EXECUTION_AVAILABLE:
                    decision = self._execute_sell_order(ticker, decision)
            
            return decision

        elif strong_sell_signal:
            decision = {
                'decision': 'FOLLOWED',
                'action': 'NONE',
                'rationale': self._generate_bearish_rationale(confidence, negative_ratio, top_risks, news_count),
                'confidence_in_decision': confidence,
                'risk_level': 'high'
            }
            logger.info(f"   ❌ DECISION: FOLLOWED - AVOID {ticker}")
            return decision
        else:
            decision = {
                'decision': 'IGNORED',
                'action': 'NONE',
                'rationale': f"BEARISH signal but final score too low",
                'confidence_in_decision': confidence,
                'risk_level': 'medium'
            }
            logger.info(f"   ⚠️  DECISION: IGNORED - {decision['rationale']}")
            return decision

    def _execute_sell_order(
        self,
        ticker: str,
        decision: Dict
    ) -> Dict:
        """Execute sell/liquidate order in Alpaca.

        Args:
            ticker: Ticker symbol
            decision: Decision dict to update

        Returns:
            Updated decision dict with execution details
        """

        logger.warning(f"   💰 Executing SELL/LIQUIDATE order in Alpaca Paper Trading...")

        try:
            from trading_mvp.execution.alpaca_orders import get_trading_client
            client = get_trading_client()

            # Close position completely
            client.close_position(ticker)

            logger.info(f"   ✅ Position in {ticker} closed successfully")

            # Update decision
            decision['execution_status'] = 'SUCCESS'
            decision['execution_timestamp'] = datetime.now().isoformat()
            decision['order_type'] = 'liquidate'

        except Exception as e:
            logger.error(f"   ❌ Sell execution failed: {e}")
            decision['execution_status'] = 'FAILED'
            decision['execution_error'] = str(e)

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
        """Handle CAUTIOUS/NEUTRAL recommendation with technical context."""

        # Extract technical data for visibility
        quant_stats = portfolio_context.get('quant_stats', {})
        rsi = quant_stats.get('rsi_14', 50)
        atr = quant_stats.get('atr_14', 0)
        trend = quant_stats.get('trend', 'UNKNOWN')

        technical_note = f"RSI: {rsi:.1f}, ATR: ${atr:.2f}, Trend: {trend}"

        # Determine WHY neutral
        if news_count == 0:
            reason = f"SIN DATOS DE NOTICIAS - Técnicos mixtos (RSI {rsi:.1f}, Tendencia {trend}). Información insuficiente para actuar."
        elif positive_ratio == 0 and negative_ratio == 0:
            reason = f"SENTIMIENTO NEUTRAL - Sin sesgo claro en {news_count} noticias. Técnicos inconcluyentes."
        elif abs(positive_ratio - negative_ratio) < 0.2:
            reason = f"SEÑALES MIXTAS - Positivo: {positive_ratio:.0%}, Negativo: {negative_ratio:.0%}. Sentimiento de noticias equilibrado. Técnicos: {technical_note}."
        else:
            reason = f"Señal de BAJA CONFIANZA ({confidence:.2f}). {technical_note}. Monitoreando para una dirección más clara."

        decision = {
            'decision': 'FOLLOWED',
            'action': 'NONE',
            'rationale': reason,
            'confidence_in_decision': confidence,
            'risk_level': 'medium',
            'technical_context': technical_note
        }

        logger.info(f"   👀 DECISION: FOLLOWED - WATCH {ticker}")
        logger.info(f"      Technical Context: {technical_note}")

        return decision

    def _calculate_position_size(
        self,
        ticker: str,
        confidence: float,
        portfolio_context: Dict
    ) -> Tuple[float, float]:
        """Calculate position size using Risk Management guardrails.

        Args:
            ticker: Ticker symbol
            confidence: Analysis confidence
            portfolio_context: Portfolio state

        Returns:
            (position_size_usd, entry_price)
        """

        # 1. Start with a base size adjusted by confidence
        base_size = self.config.base_position_size
        confidence_multiplier = confidence / 0.85  # Normalize to our MIN_CONFIDENCE_SCORE
        
        # Proposed size based only on analysis
        proposed_size = min(
            base_size * confidence_multiplier,
            self.config.max_position_size
        )

        # 2. Estimate entry price (Fallback for energy stocks MVP)
        estimated_prices = {
            'COP': 98.0, 'USO': 75.0, 'XLE': 85.0, 'XOP': 110.0, 'BNO': 25.0, 'CVE': 18.0, 'NXE': 24.5
        }
        entry_price = estimated_prices.get(ticker, 50.0)

        # 3. Apply HUMAN-DEFINED GUARDRAILS from portfolio_logic
        is_valid, allowed_size, reason = validate_trade_size(ticker, proposed_size)
        
        # Store risk metadata for reporting
        self.last_risk_reason = reason if not is_valid or allowed_size < proposed_size else "Passed all guardrails"
        
        if not is_valid:
            logger.warning(f"🛡️  RISK GUARDRAIL: Rejected {ticker} - {reason}")
            return 0.0, entry_price
        
        if allowed_size < proposed_size:
            logger.info(f"🛡️  RISK GUARDRAIL: Resized {ticker} - {reason}")
            return allowed_size, entry_price

        return proposed_size, entry_price

    def _generate_bullish_rationale(
        self,
        confidence: float,
        positive_ratio: float,
        negative_ratio: float,
        opportunities: List,
        news_count: int,
        entities_found: int
    ) -> str:
        """Generate rationale for BULLISH decision using 60/40 Weighted Model."""

        rationale_parts = [
            f"Fuerte Puntuación Ponderada ALCISTA ({confidence:.2f} >= umbral {self.config.min_confidence_for_buy})",
            f"Sentimiento: {positive_ratio:.0%} positivo vs {negative_ratio:.0%} negativo basado en {news_count} noticias"
        ]

        if opportunities:
            opp_names = [o.get('entity_name', 'N/A') if isinstance(o, dict) else o for o in opportunities[:3]]
            rationale_parts.append(f"Principales impulsores: {', '.join(opp_names)}")

        rationale_parts.append("El peso técnico del 60% confirma una estructura saludable, momentum (MACD/RSI) y convicción de volumen (RVOL)")

        return ". ".join(rationale_parts) + "."

    def _generate_bearish_rationale(
        self,
        confidence: float,
        negative_ratio: float,
        risks: List,
        news_count: int
    ) -> str:
        """Generate rationale for BEARISH decision using 60/40 Weighted Model."""

        rationale_parts = [
            f"Fuerte Puntuación Ponderada BAJISTA ({confidence:.2f} >= umbral {self.config.min_confidence_for_sell})",
            f"Sentimiento: {negative_ratio:.0%} de sesgo negativo a través de {news_count} noticias"
        ]

        if risks:
            risk_names = [r.get('entity_name', 'N/A') if isinstance(r, dict) else r for r in risks[:3]]
            rationale_parts.append(f"Riesgos clave: {', '.join(risk_names)}")

        rationale_parts.append("El peso técnico del 60% muestra debilidad, momentum bajista o convicción insuficiente para anular el riesgo macro")

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
    autopilot_enabled=False,  # Default to manual (overridden by AUTOPILOT_MODE env var)
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
    dry_run=False  # Execute in Alpaca Paper Trading when in AUTOPILOT mode
)
