#!/usr/bin/env python3
"""
Guardar empresas de energía nuclear en la DB.
Script offline que no depende de Gemini API.
"""
import sys
import os
import json

# Bootstrap to find project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_mvp.core.db_manager import insert_exploration
from trading_mvp.core.db_watchlist import create_watchlist, add_tickers_batch_to_watchlist

def main():
    print("🚀 Guardando empresas de Energía Nuclear en la DB...")

    # Lista completa de empresas nucleares
    nuclear_companies = [
        # MINERÍA DE URANIO (Tier 1)
        {'ticker': 'CCJ', 'company_name': 'Cameco Corporation', 'sector': 'Mining', 'reason': 'Largest uranium producer globally with tier-1 assets'},
        {'ticker': 'NXE', 'company_name': 'NexGen Energy', 'sector': 'Mining', 'reason': 'Developing world-class Arrow deposit in Canada'},
        {'ticker': 'EU', 'company_name': 'Energy Fuels', 'sector': 'Mining', 'reason': 'US uranium producer with ISR operations and rare earths'},
        {'ticker': 'UEC', 'company_name': 'Uranium Energy Corp', 'sector': 'Mining', 'reason': 'US-focused ISR uranium producer'},
        {'ticker': 'DYL', 'company_name': 'Deep Yellow Limited', 'sector': 'Mining', 'reason': 'Australian uranium developer in Namibia'},
        {'ticker': 'PALN', 'company_name': 'Paladin Energy', 'sector': 'Mining', 'reason': 'Australian uranium producer in Namibia'},
        {'ticker': 'EFR', 'company_name': 'Energy Resources of Australia', 'sector': 'Mining', 'reason': 'Ranger mine owner, Australian producer'},
        {'ticker': 'URA', 'company_name': 'Ur-Energy', 'sector': 'Mining', 'reason': 'US uranium producer with ISR operations'},
        {'ticker': 'DEN', 'company_name': 'Denison Mines', 'sector': 'Mining', 'reason': 'Athabasca Basin uranium developer'},
        {'ticker': 'FCUU', 'company_name': 'Fission Uranium', 'sector': 'Mining', 'reason': 'Patterson Lake South high-grade deposit'},
        {'ticker': 'FRU', 'company_name': 'Forsys Metals', 'sector': 'Mining', 'reason': 'Valenzuela uranium project in Namibia'},
        {'ticker': 'GXU', 'company_name': 'GoviEx Uranium', 'sector': 'Mining', 'reason': 'African uranium development projects'},
        {'ticker': 'ENNUF', 'company_name': 'enCore Energy', 'sector': 'Mining', 'reason': 'US ISR uranium producer and developer'},
        {'ticker': 'MGA', 'company_name': 'Mega Uranium', 'sector': 'Mining', 'reason': 'Australian uranium exploration company'},
        {'ticker': 'PTU', 'company_name': 'Purepoint Uranium', 'sector': 'Mining', 'reason': 'Athabasca Basin uranium exploration'},
        {'ticker': 'FSY', 'company_name': 'F3 Uranium', 'sector': 'Mining', 'reason': 'Athabasca Basin uranium exploration'},

        # ENRIQUECIMIENTO Y COMBUSTIBLE
        {'ticker': 'GLE', 'company_name': 'Centrus Energy', 'sector': 'Fuel Services', 'reason': 'Only US-owned uranium enrichment company'},
        {'ticker': 'LTBR', 'company_name': 'Lightbridge Corporation', 'sector': 'Technology', 'reason': 'Advanced nuclear fuel technology'},

        # UTILITIES NUCLEARES (EE.UU.)
        {'ticker': 'CEG', 'company_name': 'Constellation Energy', 'sector': 'Utility', 'reason': 'Largest US nuclear fleet operator'},
        {'ticker': 'EXC', 'company_name': 'Exelon Corporation', 'sector': 'Utility', 'reason': 'Major US nuclear utility (spun off CEG)'},
        {'ticker': 'NEE', 'company_name': 'NextEra Energy', 'sector': 'Utility', 'reason': 'Significant nuclear exposure in Florida'},
        {'ticker': 'DUK', 'company_name': 'Duke Energy', 'sector': 'Utility', 'reason': 'Multiple nuclear plants in Carolinas'},
        {'ticker': 'SO', 'company_name': 'Southern Company', 'sector': 'Utility', 'reason': 'Nuclear plants in Southeast US'},
        {'ticker': 'ETR', 'company_name': 'Entergy Corporation', 'sector': 'Utility', 'reason': 'Louisiana and Texas nuclear operations'},

        # TECNOLOGÍA DE REACTORES / SMR
        {'ticker': 'NNE', 'company_name': 'NuScale Power', 'sector': 'Technology', 'reason': 'Leading SMR technology developer'},
        {'ticker': 'SMR', 'company_name': 'SMR Nuclear', 'sector': 'Technology', 'reason': 'Small modular reactor development'},
        {'ticker': 'OKLO', 'company_name': 'Oklo Inc', 'sector': 'Technology', 'reason': 'Advanced fission micro-reactors'},

        # COMPONENTES Y SERVICIOS NUCLEARES
        {'ticker': 'BWXT', 'company_name': 'BWX Technologies', 'sector': 'Technology', 'reason': 'Nuclear components and fuel fabrication for US Navy'},
        {'ticker': 'WFRD', 'company_name': 'Woods Fusion', 'sector': 'Technology', 'reason': 'Fusion technology development'},

        # INTERNACIONAL
        {'ticker': '9504', 'company_name': 'CNNC (China National Nuclear)', 'sector': 'Utility', 'reason': 'Chinese state nuclear utility (Hong Kong listing)'},
    ]

    print(f"📊 Total empresas: {len(nuclear_companies)}")

    # Resumen por sector
    print("\n📋 Por sector:")
    sectors = {}
    for c in nuclear_companies:
        sectors[c['sector']] = sectors.get(c['sector'], 0) + 1
    for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
        print(f"  {sector}: {count}")

    # 1. Guardar en la tabla de exploraciones
    print("\n💾 Guardando exploración...")
    exploration_id = insert_exploration(
        prompt="Energía Atómica y Ciclo de Uranio Completo",
        criteria="Global nuclear energy value chain: Mining (16), Utilities (7), Technology (6), Fuel Services (1)",
        tickers=nuclear_companies,
        reasoning="Exploración exhaustiva del sector nuclear global incluyendo miners de uranio, utilities con exposición nuclear, tecnología de reactores/SMR, y servicios de combustible."
    )
    print(f"✅ Exploración guardada con ID: {exploration_id}")

    # 2. Crear Watchlist temática
    print("\n📋 Creando watchlist...")
    watchlist_id = create_watchlist(
        name="Energía Nuclear",
        description="Cartera temática del sector de energía nuclear y uranio. Incluye miners, utilities, tecnología SMR y servicios de combustible nuclear.",
        criteria_prompt="Todas las empresas públicas de energía nuclear y ciclo de combustible de uranio.",
        criteria_summary=f"{len(nuclear_companies)} empresas del sector nuclear global"
    )

    if watchlist_id:
        print(f"✅ Watchlist creada con ID: {watchlist_id}")

        # 3. Añadir tickers
        print("\n📈 Añadiendo tickers a la watchlist...")
        added = add_tickers_batch_to_watchlist(watchlist_id, nuclear_companies)
        print(f"✅ {added} empresas añadidas a la watchlist")

        # Mostrar muestra
        print("\n🔍 Muestra de top 10 empresas guardadas:")
        for i, c in enumerate(nuclear_companies[:10], 1):
            print(f"  {i}. {c['ticker']:6} | {c['company_name']:30} | {c['sector']}")

        print(f"\n✅ Pipeline completado exitosamente!")
        print(f"   - Exploración ID: {exploration_id}")
        print(f"   - Watchlist ID: {watchlist_id}")
        print(f"   - Empresas guardadas: {added}")
    else:
        print("❌ Error creando watchlist")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
