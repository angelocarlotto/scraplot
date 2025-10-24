"""
Quick test of page discovery functionality
"""
import requests
import time

API_URL = "http://localhost:5001/scrape"
TEST_URL = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1"

print("\n" + "="*70)
print("QUICK PAGE DISCOVERY TEST")
print("="*70)

print(f"\n🔍 Testing URL: {TEST_URL}")
print("\n⏳ Scraping with automatic page discovery...")

start = time.time()

try:
    response = requests.post(
        API_URL,
        json={
            "url": TEST_URL,
            "wait_time": 5,
            "scrape_all_pages": True
        },
        timeout=120
    )
    
    elapsed = time.time() - start
    result = response.json()
    
    if result.get('success'):
        data = result['data']
        print(f"\n✅ SUCCESS!\n")
        print(f"   📄 Pages Found: {data.get('total_pages', 'N/A')}")
        print(f"   🚗 Total Lots: {data.get('total_lots', 0)}")
        print(f"   ⚡ Scraping Time: {data.get('scraping_time', 'N/A')}")
        print(f"   ⏱️  Total Time: {elapsed:.2f}s")
        
        lots = data.get('lots', [])
        if lots:
            # Show distribution by page
            pages = {}
            for lot in lots:
                page = lot.get('page', 0)
                pages[page] = pages.get(page, 0) + 1
            
            print(f"\n   📊 Distribution by Page:")
            for page in sorted(pages.keys()):
                print(f"      Page {page}: {pages[page]} lots")
        
        print("\n" + "="*70 + "\n")
        
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}\n")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}\n")
