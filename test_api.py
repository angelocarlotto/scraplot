"""
Test script for the Web Scraper API
Tests the API with the Regal Auctions URL
"""

import requests
import json
import time

API_URL = "http://localhost:5001"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_api_documentation():
    """Test the API documentation endpoint"""
    print("Testing API documentation endpoint...")
    response = requests.get(f"{API_URL}/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_scrape_auction_url():
    """Test scraping the Regal Auctions URL"""
    print("="*70)
    print("Testing scraping of Regal Auctions URL...")
    print("="*70)
    
    # Test URL from the auction site
    test_url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1"
    
    payload = {
        "url": test_url,
        "wait_time": 5
    }
    
    print(f"Sending request to scrape: {test_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    start_time = time.time()
    response = requests.post(
        f"{API_URL}/scrape",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    elapsed_time = time.time() - start_time
    
    print(f"Status Code: {response.status_code}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print()
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ Scraping successful!")
            print()
            
            scraped_data = data.get('data', {})
            print(f"Page Title: {scraped_data.get('title', 'N/A')}")
            print(f"Meta Description: {scraped_data.get('meta_description', 'N/A')}")
            print()
            
            # Check for structured data
            structured = scraped_data.get('structured_data', {})
            if structured:
                print("Structured Data Found:")
                print(f"  Type: {structured.get('type', 'N/A')}")
                print(f"  Total Lots: {structured.get('total_lots', 0)}")
                print()
                
                lots = structured.get('lots', [])
                if lots:
                    print(f"First 3 lots:")
                    for i, lot in enumerate(lots[:3], 1):
                        print(f"\n  Lot #{i}:")
                        print(f"    Lot Number: {lot.get('lot_number', 'N/A')}")
                        print(f"    Title: {lot.get('title', 'N/A')}")
                        print(f"    Starting Bid: {lot.get('starting_bid', 'N/A')}")
                        print(f"    Reserve Price: {lot.get('reserve_price', 'N/A')}")
                        print(f"    Odometer: {lot.get('odometer', 'N/A')}")
                        print(f"    Engine: {lot.get('engine', 'N/A')}")
            
            # Save full response to file
            with open('api_test_response.json', 'w') as f:
                json.dump(data, f, indent=2)
            print()
            print("✅ Full response saved to: api_test_response.json")
        else:
            print("❌ Scraping failed!")
            print(f"Error: {data.get('error', 'Unknown error')}")
    else:
        print("❌ Request failed!")
        print(f"Response: {response.text}")

def test_invalid_url():
    """Test with an invalid URL"""
    print("="*70)
    print("Testing with invalid URL...")
    print("="*70)
    
    payload = {
        "url": "not-a-valid-url"
    }
    
    response = requests.post(
        f"{API_URL}/scrape",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def main():
    """Run all tests"""
    print()
    print("="*70)
    print("WEB SCRAPER API TEST SUITE")
    print("="*70)
    print()
    
    try:
        # Test health check
        test_health_check()
        
        # Test API documentation
        test_api_documentation()
        
        # Test scraping auction URL
        test_scrape_auction_url()
        
        # Test invalid URL
        test_invalid_url()
        
        print("="*70)
        print("✅ All tests completed!")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to API server!")
        print("Make sure the API is running with: python api.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    main()
