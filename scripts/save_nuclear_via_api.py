#!/usr/bin/env python3
"""
Guardar empresas de energía nuclear en la DB usando SOLO la API del dashboard.
No usa acceso directo a la DB.
"""
import requests
import json
import sys

API_BASE = "http://localhost:3000/api"

def main():
    print("🚀 Guardando empresas de Energía Nuclear vía API...")

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

    # 1. Crear Watchlist vía API
    print("\n📋 Creando watchlist vía API...")
    watchlist_data = {
        "name": "Energía Nuclear",
        "description": "Cartera temática del sector de energía nuclear y uranio. Incluye miners, utilities, tecnología SMR y servicios de combustible nuclear.",
        "criteria_prompt": "Todas las empresas públicas de energía nuclear y ciclo de combustible de uranio.",
        "criteria_summary": f"{len(nuclear_companies)} empresas del sector nuclear global"
    }

    response = requests.post(f"{API_BASE}/watchlists", json=watchlist_data)
    if response.status_code != 201:
        print(f"❌ Error creando watchlist: {response.status_code} - {response.text}")
        return 1

    watchlist = response.json()
    watchlist_id = watchlist['id']
    print(f"✅ Watchlist creada con ID: {watchlist_id}")

    # 2. Añadir tickers vía API
    print("\n📈 Añadiendo tickers a la watchlist...")
    added_count = 0
    failed = []

    for company in nuclear_companies:
        item_data = {
            "watchlist_id": watchlist_id,
            "ticker": company['ticker'],
            "company_name": company['company_name'],
            "reason": f"{company['sector']}: {company['reason']}"
        }

        response = requests.post(f"{API_BASE}/watchlists/items", json=item_data)
        if response.status_code == 201:
            added_count += 1
            if added_count % 5 == 0:
                print(f"  Progreso: {added_count}/{len(nuclear_companies)}")
        else:
            failed.append(company['ticker'])
            print(f"  ❌ Error añadiendo {company['ticker']}: {response.status_code} - {response.text}")

    print(f"\n✅ {added_count} empresas añadidas a la watchlist")

    if failed:
        print(f"\n⚠️  Fallaron {len(failed)} empresas: {', '.join(failed)}")

    # 3. Verificar vía API
    print("\n🔍 Verificando vía API...")
    response = requests.get(f"{API_BASE}/watchlists")
    if response.status_code == 200:
        watchlists = response.json()
        nuclear_wl = next((wl for wl in watchlists if wl['name'] == 'Energía Nuclear'), None)

        if nuclear_wl:
            print(f"✅ Watchlist verificada:")
            print(f"   - ID: {nuclear_wl['id']}")
            print(f"   - Nombre: {nuclear_wl['name']}")
            print(f"   - Total tickers: {nuclear_wl.get('ticker_count', 0)}")
            print(f"\n📊 Muestra de top 10 empresas:")
            for i, item in enumerate(nuclear_wl.get('items', [])[:10], 1):
                print(f"   {i}. {item['ticker']:6} | {item['company_name'][:30]:30}")
        else:
            print("❌ No se encontró la watchlist 'Energía Nuclear'")
            return 1
    else:
        print(f"❌ Error verificando: {response.status_code}")
        return 1

    print(f"\n✅ Pipeline completado exitosamente!")
    print(f"   - Watchlist ID: {watchlist_id}")
    print(f"   - Empresas guardadas: {added_count}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
