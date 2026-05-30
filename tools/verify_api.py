"""Quick API verifier. Usage: python tools/verify_api.py [/path]"""
import sys, requests

BASE = "http://localhost:8000"
path = sys.argv[1] if len(sys.argv) > 1 else "/api/categories"

r = requests.get(f"{BASE}{path}")
data = r.json()
print(f"{r.status_code} {path}")
if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
            for item in v[:5]:
                print(f"    {item}")
        else:
            print(f"  {k}: {v}")
