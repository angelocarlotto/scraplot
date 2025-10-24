"""
Test script for automatic page discovery feature
"""
import requests
import json

API_URL = "http://localhost:5001/scrape"

# Test URL (Regal Auctions)
test_url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1"

print("=" * 70)
print("Testing Automatic Page Discovery")
print("=" * 70)
print(f"\nTest URL: {test_url}")
print("\nSending request with scrape_all_pages=True...")
print("-" * 70)

try:
    response = requests.post(
        API_URL,
        json={
            "url": test_url,
            "wait_time": 5,
            "scrape_all_pages": True
        },
        timeout=300  # 5 minutes timeout for scraping all pages
    )
    
    result = response.json()
    
    if result.get('success'):
        data = result.get('data', {})
        structured_data = data.get('structured_data', {})
        
        print("\n✓ SUCCESS!")
        print("-" * 70)
        print(f"Total Pages Discovered: {structured_data.get('total_pages', 'N/A')}")
        print(f"Total Lots Scraped: {structured_data.get('total_lots', 0)}")
        print(f"Scraping Time: {structured_data.get('scraping_time', 'N/A')}")
        print("-" * 70)
        
        lots = structured_data.get('lots', [])
        if lots:
            print(f"\nFirst 3 lots:")
            for i, lot in enumerate(lots[:3], 1):
                print(f"\n  {i}. Lot #{lot.get('lot_number', 'N/A')}")
                print(f"     Title: {lot.get('title', 'N/A')[:60]}...")
                print(f"     Page: {lot.get('page', 'N/A')}")
                print(f"     Starting Bid: {lot.get('starting_bid', 'N/A')}")
        
        # Save full results to file
        with open('data/page_discovery_test.json', 'w') as f:
            json.dump(structured_data, f, indent=2)
        print("\n✓ Full results saved to data/page_discovery_test.json")
        
    else:
        print("\n✗ FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        
except requests.exceptions.Timeout:
    print("\n✗ Request timed out (took more than 5 minutes)")
except Exception as e:
    print(f"\n✗ Exception: {e}")

print("\n" + "=" * 70)
