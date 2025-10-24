"""
Debug script to inspect the HTML structure of the auction page
"""

import requests
from bs4 import BeautifulSoup

url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=2"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Fetching: {url}\n")
response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Content Length: {len(response.content)}")
print(f"\nFirst 3000 characters of HTML:\n")
print("=" * 80)
print(response.text[:3000])
print("=" * 80)

# Parse and look for common patterns
soup = BeautifulSoup(response.content, 'lxml')

# Try to find lot containers
print("\n\nSearching for lot elements...")
print("-" * 80)

# Try various common selectors
selectors_to_try = [
    'article',
    'div[class*="lot"]',
    'div[class*="item"]',
    'div[class*="card"]',
    'li[class*="lot"]',
    'tr',
    '[data-lot-id]',
    '[data-id]',
]

for selector in selectors_to_try:
    elements = soup.select(selector)
    if elements:
        print(f"\n✓ Found {len(elements)} elements with selector: {selector}")
        if elements:
            print(f"First element preview:")
            print(str(elements[0])[:500])
    else:
        print(f"✗ No elements found with selector: {selector}")

# Check for JavaScript-rendered content
if 'window.__INITIAL_STATE__' in response.text or 'window.__PRELOADED_STATE__' in response.text:
    print("\n⚠️  Page may be JavaScript-rendered (React/Vue)")
    
if 'next' in response.text.lower() and 'script' in response.text.lower():
    print("⚠️  May be a Next.js application")
