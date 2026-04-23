import re

with open('trading_mvp/agents/decision_agent.py', 'r') as f:
    content = f.read()

# 1. Replace _handle_bullish Pyramiding logic
bullish_old = """        # 3. Check for EXISTING EXPOSURE (Live) and evaluate PYRAMIDING
        if current_pos:
            decision = {
                'decision': 'FOLLOWED',
                'action': 'HELD',
                'rationale': f"Posición existente en rango alcista. Manteniendo (sin escalamiento por política actual).",
                'confidence_in_decision': confidence,
                'risk_level': 'low'
            }
            logger.info(f"   👀 DECISION: FOLLOWED - HOLD {ticker}")
            return decision"""

bullish_new = """        # 3. Check for EXISTING EXPOSURE (Live) and evaluate PYRAMIDING or TRIMMING
        if current_pos:
            unrealized_plpc = float(current_pos.get('unrealized_plpc', 0))
            # Evaluate Trimming first (if we have gains and momentum is exhausted)
            if unrealized_plpc > 0.05 and (rsi > 75 or quant_stats.get('momentum') == 'NEGATIVE'):
                decision = {
                    'decision': 'FOLLOWED',
                    'action': 'TRIM',
                    'rationale': f"Posición existente con ganancia del {unrealized_plpc:.1%}. Técnico extendido (RSI: {rsi:.1f}). Recortando 25% para asegurar caja.",
                    'confidence_in_decision': confidence,
                    'risk_level': 'low'
                }
                logger.info(f"   ✂️  DECISION: FOLLOWED - TRIM {ticker}")
                
                if self.config.autopilot_enabled and not self.config.dry_run:
                    if ALPACA_EXECUTION_AVAILABLE:
                        qty_to_sell = int(float(current_pos['qty']) * 0.25)
                        if qty_to_sell >= 1:
                            decision = self._execute_sell_order(ticker, decision, qty_to_sell=qty_to_sell)
                        else:
                            decision['action'] = 'HELD'
                            decision['rationale'] += " (Cancelado: Posición muy pequeña para recortar)"
                return decision
            
            # Evaluate Pyramiding (Scaling In)
            elif unrealized_plpc > 0 and confidence >= 0.85 and rsi < 65:
                is_pyramiding = True
                logger.info(f"   📈  Condiciones óptimas para ESCALAR (Pyramiding) en {ticker}. Calculando tamaño...")
                # We will continue the execution flow to calculate position size and buy
            else:
                decision = {
                    'decision': 'FOLLOWED',
                    'action': 'HELD',
                    'rationale': f"Posición existente en rango alcista. Manteniendo (condiciones no óptimas para escalar o recortar).",
                    'confidence_in_decision': confidence,
                    'risk_level': 'low'
                }
                logger.info(f"   👀 DECISION: FOLLOWED - HOLD {ticker}")
                return decision
        else:
            is_pyramiding = False"""

if bullish_old in content:
    content = content.replace(bullish_old, bullish_new)
    print("Bullish replacement successful.")
else:
    print("Bullish old text NOT FOUND.")

# 2. Add qty_to_sell to _execute_sell_order def
sell_old = """    def _execute_sell_order(
        self,
        ticker: str,
        decision: Dict
    ) -> Dict:"""

sell_new = """    def _execute_sell_order(
        self,
        ticker: str,
        decision: Dict,
        qty_to_sell: float = None
    ) -> Dict:"""

if sell_old in content:
    content = content.replace(sell_old, sell_new)
    print("Sell def replacement successful.")
else:
    print("Sell def old text NOT FOUND.")

# 3. Replace body of _execute_sell_order
sell_body_old = """            entry_price = float(current_pos['avg_entry_price'])
            current_price = float(current_pos['current_price'])
            qty = float(current_pos['qty'])

            # Calculate P&L
            profit_loss = (current_price - entry_price) * qty
            profit_loss_pct = ((current_price - entry_price) / entry_price) * 100

            logger.info(f"   📊 P&L Calculation: ${entry_price:.2f} → ${current_price:.2f} = ${profit_loss:.2f} ({profit_loss_pct:+.2f}%)")

            # Close position completely
            client.close_position(ticker)

            logger.info(f"   ✅ Position in {ticker} closed successfully")

            # Update decision with outcome in Supabase
            try:
                from trading_mvp.core.db_manager import get_connection
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        # Find the most recent OPEN decision for this ticker
                        cur.execute(\"\"\"
                            SELECT id, recommendation
                            FROM investment_decisions
                            WHERE ticker = %s
                            AND status IN ('PENDING', 'OPEN')
                            AND action_taken = 'BOUGHT'
                            ORDER BY decision_timestamp DESC
                            LIMIT 1
                        \"\"\", (ticker,))

                        result = cur.fetchone()
                        if result:
                            decision_id, recommendation = result

                            # Update with outcome
                            cur.execute(\"\"\"
                                UPDATE investment_decisions
                                SET exit_price = %s,
                                    exit_timestamp = CURRENT_TIMESTAMP,
                                    profit_loss = %s,
                                    profit_loss_pct = %s,
                                    status = 'CLOSED'
                                WHERE id = %s
                            \"\"\", (current_price, profit_loss, profit_loss_pct, decision_id))

                            conn.commit()
                            logger.info(f"   ✅ Updated decision {decision_id} with P&L: ${profit_loss:.2f} ({profit_loss_pct:+.2f}%)")
                        else:
                            logger.warning(f"   ⚠️  No OPEN decision found for {ticker} to update")
                finally:
                    conn.close()
            except Exception as db_error:
                logger.error(f"   ⚠️  Failed to update decision in DB: {db_error}")

            # Update decision dict
            decision['execution_status'] = 'SUCCESS'
            decision['execution_timestamp'] = datetime.now().isoformat()
            decision['order_type'] = 'liquidate'
            decision['exit_price'] = current_price
            decision['profit_loss'] = profit_loss
            decision['profit_loss_pct'] = profit_loss_pct"""

sell_body_new = """            entry_price = float(current_pos['avg_entry_price'])
            current_price = float(current_pos['current_price'])
            total_qty = float(current_pos['qty'])
            
            sell_qty = qty_to_sell if qty_to_sell is not None else total_qty

            # Calculate P&L for the sold portion
            profit_loss = (current_price - entry_price) * sell_qty
            profit_loss_pct = ((current_price - entry_price) / entry_price) * 100

            logger.info(f"   📊 P&L Calculation: ${entry_price:.2f} → ${current_price:.2f} = ${profit_loss:.2f} ({profit_loss_pct:+.2f}%)")

            if sell_qty >= total_qty:
                # Close position completely
                client.close_position(ticker)
                logger.info(f"   ✅ Position in {ticker} closed successfully")
                status_to_set = 'CLOSED'
            else:
                # Partial close
                from trading_mvp.execution.alpaca_orders import submit_order
                submit_order(symbol=ticker, qty=int(sell_qty), side='sell', order_type='market')
                logger.info(f"   ✅ Partial position ({sell_qty} shares) in {ticker} sold successfully")
                status_to_set = 'PARTIAL_CLOSED'

            # Update decision with outcome in Supabase
            try:
                from trading_mvp.core.db_manager import get_connection
                conn = get_connection()
                try:
                    with conn.cursor() as cur:
                        # Find the most recent OPEN decision for this ticker
                        cur.execute(\"\"\"
                            SELECT id, recommendation
                            FROM investment_decisions
                            WHERE ticker = %s
                            AND status IN ('PENDING', 'OPEN')
                            AND action_taken IN ('BOUGHT', 'SCALE_IN')
                            ORDER BY decision_timestamp DESC
                            LIMIT 1
                        \"\"\", (ticker,))

                        result = cur.fetchone()
                        if result:
                            decision_id, recommendation = result

                            # Update with outcome
                            cur.execute(\"\"\"
                                UPDATE investment_decisions
                                SET exit_price = %s,
                                    exit_timestamp = CURRENT_TIMESTAMP,
                                    profit_loss = %s,
                                    profit_loss_pct = %s,
                                    status = %s
                                WHERE id = %s
                            \"\"\", (current_price, profit_loss, profit_loss_pct, status_to_set, decision_id))

                            conn.commit()
                            logger.info(f"   ✅ Updated decision {decision_id} with P&L: ${profit_loss:.2f} ({profit_loss_pct:+.2f}%)")
                        else:
                            logger.warning(f"   ⚠️  No OPEN decision found for {ticker} to update")
                finally:
                    conn.close()
            except Exception as db_error:
                logger.error(f"   ⚠️  Failed to update decision in DB: {db_error}")

            # Update decision dict
            decision['execution_status'] = 'SUCCESS'
            decision['execution_timestamp'] = datetime.now().isoformat()
            decision['order_type'] = 'liquidate' if sell_qty >= total_qty else 'trim'
            decision['shares_sold'] = sell_qty
            decision['exit_price'] = current_price
            decision['profit_loss'] = profit_loss
            decision['profit_loss_pct'] = profit_loss_pct"""

if sell_body_old in content:
    content = content.replace(sell_body_old, sell_body_new)
    print("Sell body replacement successful.")
else:
    print("Sell body old text NOT FOUND.")

# 4. Handle cautious trimming
cautious_old = """        action_taken = 'HELD' if current_pos else 'NONE'
        log_action = 'HOLD' if current_pos else 'WATCH'

        decision = {
            'decision': 'FOLLOWED',
            'action': action_taken,
            'rationale': reason,
            'confidence_in_decision': confidence,
            'risk_level': 'medium',
            'technical_context': technical_note
        }

        logger.info(f"   👀 DECISION: FOLLOWED - {log_action} {ticker}")
        logger.info(f"      Technical Context: {technical_note}")

        return decision"""

cautious_new = """        if current_pos:
            unrealized_plpc = float(current_pos.get('unrealized_plpc', 0))
            if unrealized_plpc > 0.05 and (rsi > 75 or quant_stats.get('momentum') == 'NEGATIVE'):
                decision = {
                    'decision': 'FOLLOWED',
                    'action': 'TRIM',
                    'rationale': f"Posición existente con ganancia del {unrealized_plpc:.1%}. {reason}. Recortando 25% para asegurar caja.",
                    'confidence_in_decision': confidence,
                    'risk_level': 'low',
                    'technical_context': technical_note
                }
                logger.info(f"   ✂️  DECISION: FOLLOWED - TRIM {ticker}")
                
                if self.config.autopilot_enabled and not self.config.dry_run:
                    if ALPACA_EXECUTION_AVAILABLE:
                        qty_to_sell = int(float(current_pos['qty']) * 0.25)
                        if qty_to_sell >= 1:
                            decision = self._execute_sell_order(ticker, decision, qty_to_sell=qty_to_sell)
                        else:
                            decision['action'] = 'HELD'
                            decision['rationale'] += " (Cancelado: Posición muy pequeña para recortar)"
                return decision

        action_taken = 'HELD' if current_pos else 'NONE'
        log_action = 'HOLD' if current_pos else 'WATCH'

        decision = {
            'decision': 'FOLLOWED',
            'action': action_taken,
            'rationale': reason,
            'confidence_in_decision': confidence,
            'risk_level': 'medium',
            'technical_context': technical_note
        }

        logger.info(f"   👀 DECISION: FOLLOWED - {log_action} {ticker}")
        logger.info(f"      Technical Context: {technical_note}")

        return decision"""

if cautious_old in content:
    content = content.replace(cautious_old, cautious_new)
    print("Cautious replacement successful.")
else:
    print("Cautious old text NOT FOUND.")

with open('trading_mvp/agents/decision_agent.py', 'w') as f:
    f.write(content)
