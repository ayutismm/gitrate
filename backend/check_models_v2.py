import os
import requests
from dotenv import load_dotenv
import sys

# Force output to utf-8
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

print("Fetching models...")
try:
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        print(f"Found {len(data)} total models.")
        
        print("\n--- FREE DEEPSEEK MODELS ---")
        found = False
        for m in data:
            mid = m["id"]
            pricing = m.get("pricing", {})
            price_str = repr(pricing)
            
            # Check for free pricing (0 prompt, 0 completion)
            is_free = False
            if isinstance(pricing, dict):
                p_in = pricing.get("prompt")
                p_out = pricing.get("completion")
                if p_in == "0" and p_out == "0":
                    is_free = True
            
            if "deepseek" in mid.lower() and is_free:
                print(f"ID: {mid}")
                found = True
                
        if not found:
            print("No free DeepSeek models found directly.")
            print("\n--- ALL FREE MODELS (Top 10) ---")
            count = 0
            for m in data:
                mid = m["id"]
                pricing = m.get("pricing", {})
                p_in = pricing.get("prompt")
                p_out = pricing.get("completion")
                if p_in == "0" and p_out == "0":
                    print(f"Free: {mid}")
                    count += 1
                    if count >= 10: break

    else:
        print(f"API Error: {response.status_code}")
except Exception as e:
    print(f"Request failed: {e}")
