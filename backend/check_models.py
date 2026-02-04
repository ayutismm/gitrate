import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    # Try to grab it from the file directly if it's not in env yet (restart pending?)
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("OPENROUTER_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break

print(f"Using Key: {api_key[:5]}...{api_key[-5:]}")

response = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    models = response.json()["data"]
    print("\nDeepSeek Models:")
    for m in models:
        if "deepseek" in m["id"].lower():
            print(f"- {m['id']} (pricing: {m.get('pricing', 'unknown')})")
else:
    print(f"Error: {response.status_code} - {response.text}")
