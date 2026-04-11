import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Cargar variables de entorno
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: Supabase env vars missing")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

tables = [
    "investment_desk_runs",
    "ticker_analyses",
    "investment_decisions",
    "recommendation_performance",
    "investment_runs",
    "ticker_analysis"
]

print(f"{'Table Name':<30} | {'Count':<10}")
print("-" * 45)

for table in tables:
    try:
        response = supabase.table(table).select("*", count="exact").limit(1).execute()
        count = response.count if response.count is not None else len(response.data)
        print(f"{table:<30} | {count:<10}")
    except Exception as e:
        print(f"{table:<30} | ERROR: {str(e)[:40]}")
