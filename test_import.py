"""Test script for importing Trading212 JSON."""
import json
import requests

# Read sample trade JSON
with open("archive/trades/2025/03/2025-03-04T17-12-17_POS29013698894.json", "r") as f:
    trade_data = json.load(f)

print("Testing single trade import...")
print(f"Trade data: {json.dumps(trade_data, indent=2)}")

# Test import
try:
    response = requests.post(
        "http://localhost:8000/import/trades",
        json=trade_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success! Imported: {result['imported']}, Duplicates: {result['duplicates']}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Exception: {e}")
