import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_zai_auth():
    api_key = os.getenv("ZAI_API_KEY")
    base_url = "https://api.z.ai/api/coding/paas/v4"
    model = "glm-5.1"
    
    print(f"--- Z.AI AUTHENTICATION TEST ---")
    print(f"URL: {base_url}")
    print(f"Model: {model}")
    print(f"API Key (first 8 chars): {api_key[:8] if api_key else 'MISSING'}...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Ping"}],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=10)
        
        print(f"\nHTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Authentication valid!")
            print(f"Response: {response.json()['choices'][0]['message']['content']}")
        elif response.status_code == 401:
            print("❌ FAILED: Unauthorized (Invalid or expired API Key)")
            print(f"Error detail: {response.text}")
        else:
            print(f"❓ UNKNOWN ERROR: {response.status_code}")
            print(f"Body: {response.text}")
            
    except Exception as e:
        print(f"💥 CONNECTION ERROR: {e}")

if __name__ == "__main__":
    test_zai_auth()
