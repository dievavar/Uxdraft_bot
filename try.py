import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/models"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

resp = requests.get(url, headers=headers, timeout=30)
resp.raise_for_status()

models = resp.json()["data"]

print("Доступные модели:")
for m in models:
    print(f"- {m['id']}")
