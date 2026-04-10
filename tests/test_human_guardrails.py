
import os
import unittest
from unittest.mock import patch, MagicMock
from trading_mvp.agents.decision_agent import DecisionAgent, DecisionConfig
from trading_mvp.core.portfolio_logic import validate_trade_size

class TestHumanGuardrails(unittest.TestCase):

    def setUp(self):
        # Configuramos variables de entorno para el test
        os.environ["MIN_CONFIDENCE_SCORE"] = "0.85"
        os.environ["MAX_PORTFOLIO_EXPOSURE_PCT"] = "0.80"
        os.environ["MIN_CASH_RESERVE_PCT"] = "0.20"
        os.environ["MAX_POSITION_SIZE_PCT"] = "0.10"
        
    @patch('trading_mvp.agents.decision_agent.get_account')
    @patch('trading_mvp.agents.decision_agent.get_positions')
    def test_confidence_threshold(self, mock_positions, mock_account):
        """Prueba que el MIN_CONFIDENCE_SCORE bloquee trades dudosos."""
        agent = DecisionAgent()
        
        # Simulación de análisis con confianza de 0.70 (menor al 0.85 definido)
        low_conf_analysis = {
            'ticker': 'AAPL',
            'recommendation': 'BULLISH',
            'avg_confidence': 0.70,
            'positive_ratio': 0.80,
            'negative_ratio': 0.10,
            'analysis_timestamp': '2026-04-09T10:00:00',
            'id': 1
        }
        
        decision = agent.analyze_recommendation(low_conf_analysis)
        
        # Debe ser ignorado por baja confianza
        self.assertEqual(decision['decision'], 'IGNORED')
        self.assertIn("low confidence", decision['rationale'])
        print(f"✅ Test Confianza: Bloqueado correctamente (Score 0.70 < 0.85)")

    @patch('trading_mvp.core.portfolio_logic.get_account')
    @patch('trading_mvp.core.portfolio_logic.get_positions')
    def test_portfolio_exposure_limit(self, mock_positions, mock_account):
        """Prueba que el MAX_PORTFOLIO_EXPOSURE_PCT detenga compras si ya estamos muy invertidos."""
        # Simulamos cuenta con $100,000 equity, pero solo $10,000 cash (90% invertido)
        mock_account.return_value = {
            'equity': 100000.0,
            'cash': 10000.0,
            'portfolio_value': 100000.0
        }
        mock_positions.return_value = [] # No importa para este test
        
        # Intentamos invertir $5,000 más
        is_valid, size, reason = validate_trade_size("TSLA", 5000.0)
        
        self.assertFalse(is_valid)
        self.assertIn("Max total portfolio exposure reached", reason)
        print(f"✅ Test Exposición: Bloqueado correctamente (Inversión actual > 80%)")

    @patch('trading_mvp.core.portfolio_logic.get_account')
    @patch('trading_mvp.core.portfolio_logic.get_positions')
    def test_cash_reserve_limit(self, mock_positions, mock_account):
        """Prueba que el MIN_CASH_RESERVE_PCT proteja el colchón de seguridad."""
        # Tenemos $21,000 cash en una cuenta de $100,000. 
        # El límite de reserva es 20% ($20,000). Solo podemos usar $1,000.
        mock_account.return_value = {
            'equity': 100000.0,
            'cash': 21000.0,
            'portfolio_value': 100000.0
        }
        mock_positions.return_value = []
        
        # Intentamos comprar $5,000
        is_valid, size, reason = validate_trade_size("MSFT", 5000.0)
        
        # Debe reducir el tamaño a $1,000 para no tocar la reserva del 20%
        self.assertTrue(is_valid)
        self.assertEqual(size, 1000.0)
        self.assertIn("Size reduced", reason)
        print(f"✅ Test Reserva: Tamaño reducido de $5000 a $1000 para mantener el 20% de reserva")

if __name__ == '__main__':
    unittest.main()
