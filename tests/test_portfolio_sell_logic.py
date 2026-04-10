
import os
import unittest
from unittest.mock import patch, MagicMock
from trading_mvp.agents.decision_agent import DecisionAgent, DecisionConfig

class TestPortfolioSellLogic(unittest.TestCase):

    def setUp(self):
        # Configuramos para Autopilot ON para ver la ejecución total
        os.environ["AUTOPILOT_MODE"] = "on"
        os.environ["MIN_CONFIDENCE_SCORE"] = "0.80"
        
    @patch('trading_mvp.agents.decision_agent.ALPACA_EXECUTION_AVAILABLE', True)
    @patch('trading_mvp.agents.decision_agent.DecisionAgent._execute_sell_order')
    def test_automatic_sell_on_bearish_signal(self, mock_execute_sell):
        """Prueba que el agente VENDA automáticamente si tiene la acción y el reporte es malo."""
        agent = DecisionAgent()
        agent.config.dry_run = False # Queremos simular ejecución real
        
        # Mock de la función de ejecución para que no llame a Alpaca realmente
        mock_execute_sell.side_effect = lambda ticker, decision: {**decision, 'execution_status': 'SUCCESS'}

        # 1. Contexto de Cartera: Tenemos COP
        portfolio_context = {
            'positions': [
                {'symbol': 'COP', 'qty': 100, 'current_price': 95.0}
            ]
        }
        
        # 2. Análisis de la Mesa: BEARISH muy fuerte para COP
        bearish_analysis = {
            'ticker': 'COP',
            'recommendation': 'BEARISH',
            'avg_confidence': 0.95,
            'positive_ratio': 0.10,
            'negative_ratio': 0.85,
            'top_risks': ['Global oversupply', 'Price drop'],
            'analysis_timestamp': '2026-04-09T12:00:00',
            'id': 123
        }
        
        # Ejecutar decisión
        decision = agent.analyze_recommendation(bearish_analysis, portfolio_context=portfolio_context)
        
        # VERIFICACIÓN
        self.assertEqual(decision['action'], 'SOLD')
        self.assertEqual(decision['decision'], 'FOLLOWED')
        self.assertIn("Liquidating 100 shares", decision['rationale'])
        print(f"✅ Test Venta: ¡COP liquidado correctamente por señal BEARISH! (Conf: 0.95)")

    def test_no_sell_if_not_in_portfolio(self, *args):
        """Prueba que el agente no intente vender si no tiene la acción."""
        agent = DecisionAgent()
        
        # Cartera VACÍA
        portfolio_context = {'positions': []}
        
        # Análisis BEARISH para un ticker que NO tenemos
        bearish_analysis = {
            'ticker': 'TSLA',
            'recommendation': 'BEARISH',
            'avg_confidence': 0.90,
            'positive_ratio': 0.10,
            'negative_ratio': 0.80,
            'analysis_timestamp': '2026-04-09T12:00:00',
            'id': 456
        }
        
        decision = agent.analyze_recommendation(bearish_analysis, portfolio_context=portfolio_context)
        
        # VERIFICACIÓN
        self.assertEqual(decision['action'], 'NONE') # No vende porque no tiene
        self.assertEqual(decision['decision'], 'FOLLOWED') # Pero sigue la recomendación de "evitar"
        print(f"✅ Test Evitar: TSLA ignorado correctamente (no está en cartera)")

if __name__ == '__main__':
    unittest.main()
