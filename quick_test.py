"""
Quick test script - sends a single request to the API
"""

import requests
import json

API_URL = "http://localhost:5001"

# Test scraping the Regal Auctions URL
test_url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1"

print("="*70)
print("Testing Web Scraper API")
print("="*70)
print(f"API URL: {API_URL}")
print(f"Target URL: {test_url}")
print("="*70)

payload = {
    "url": test_url,
    "wait_time": 5
}

try:
    print("\nSending POST request to /scrape endpoint...")
    response = requests.post(
        f"{API_URL}/scrape",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('success'):
            print("✅ SUCCESS!\n")
            
            scraped_data = data.get('data', {})
            print(f"Page Title: {scraped_data.get('title', 'N/A')[:100]}")
            
            # Check for structured data
            structured = scraped_data.get('structured_data', {})
            if structured and 'lots' in structured:
                lots = structured.get('lots', [])
                print(f"Total Lots Found: {len(lots)}\n")
                
                if lots:
                    print("First 3 lots:")
                    for i, lot in enumerate(lots[:3], 1):
                        print(f"\n  #{i}: {lot.get('title', 'N/A')[:60]}")
                        print(f"      Lot #: {lot.get('lot_number', 'N/A')}")
                        print(f"      Starting Bid: {lot.get('starting_bid', 'N/A')}")
                        print(f"      Reserve: {lot.get('reserve_price', 'N/A')}")
                        print(f"      Odometer: {lot.get('odometer', 'N/A')}")
                
                # Save to file
                with open('api_response.json', 'w') as f:
                    json.dump(structured.get('lots', []), f, indent=2)
                print(f"\n✅ Full data saved to: api_response.json")
            else:
                print("No structured data found")
        else:
            print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to API!")
    print("Start the API with: python api.py")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*70)
