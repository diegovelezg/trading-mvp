import sys
import os
import json
import asyncio
from datetime import datetime

# Bootstrap to find project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_mvp.core.dashboard_api_client import create_watchlist, add_ticker_to_watchlist
from trading_mvp.core.db_manager import insert_exploration  # Mantener temporalmente para explorations
from google import genai
from google.genai import types

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = os.getenv("GEMINI_API_MODEL_01", "gemini-2.0-flash-exp")

client = genai.Client(api_key=GEMINI_API_KEY)

async def perform_nuclear_exploration():
    print("🚀 Iniciando exploración de todas las empresas de Energía Atómica...")
    
    prompt = """
    Identifica TODAS las empresas públicas relevantes (cotizadas en bolsa) involucradas en el sector de la energía nuclear/atómica.
    Incluye:
    1. Minería y exploración de Uranio (Tier 1 y Junior miners relevantes).
    2. Operadores de plantas nucleares (Utilities con exposición nuclear masiva).
    3. Tecnología de reactores y SMR (Small Modular Reactors).
    4. Servicios de enriquecimiento y ciclo de combustible.
    
    Para cada empresa, proporciona:
    - Ticker (formato: SYMBOL, ej: CCJ)
    - Nombre de la empresa
    - Sub-sector (Mining, Utility, Technology, Service)
    - Una breve razón de 1 frase de por qué es relevante.
    
    Devuelve los resultados en formato JSON:
    {
      "theme": "Nuclear Energy & Uranium Cycle",
      "summary": "Exploración exhaustiva de la cadena de valor nuclear global.",
      "results": [
        {"ticker": "SYMBOL", "company_name": "NAME", "sector": "SUBSECTOR", "reason": "REASON"},
        ...
      ]
    }
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        data = json.loads(response.text)
        tickers = data.get('results', [])
        print(f"✅ Se han identificado {len(tickers)} empresas.")
        
        # 1. Guardar en la tabla de exploraciones
        exploration_id = insert_exploration(
            prompt="Energía Atómica y Ciclo de Uranio Completo",
            criteria="Global nuclear energy value chain: Mining, Utilities, SMRs, Fuel Services",
            tickers=tickers,
            reasoning=data.get('summary', '')
        )
        print(f"📦 Exploración guardada en Supabase con ID: {exploration_id}")
        
        # 2. Crear una Watchlist temática
        watchlist_id = create_watchlist(
            name="Atomic Energy Global",
            description="Exploración masiva de la cadena de valor de energía atómica y uranio.",
            criteria_prompt="Todas las empresas públicas de energía nuclear y uranio.",
            criteria_summary=data.get('summary', '')
        )
        
        if watchlist_id:
            # Añadir tickers individualmente via Dashboard API
            added = 0
            for t in tickers:
                ticker = t.get('ticker', '').upper()
                company_name = t.get('company_name', '')
                reason = f"{t.get('sector', 'N/A')}: {t.get('reason', '')}"

                if add_ticker_to_watchlist(watchlist_id, ticker, company_name, reason):
                    added += 1

            print(f"📈 Watchlist '{watchlist_id}' poblada con {added} empresas en la nube.")

            # Mostrar los primeros 5 para feedback
            for t in tickers[:5]:
                print(f"   - {t['ticker']}: {t['company_name']} ({t['sector']})")
        
    except Exception as e:
        print(f"❌ Error en la exploración: {e}")

if __name__ == "__main__":
    asyncio.run(perform_nuclear_exploration())
