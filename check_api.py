"""
Check for API endpoints or JavaScript data
"""

import requests
from bs4 import BeautifulSoup
import json
import re

url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=2"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

response = requests.get(url, headers=headers)
html_content = response.text

# Look for embedded JSON data
print("Searching for embedded JSON data...")
print("=" * 80)

# Common patterns for embedded data
patterns = [
    r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
    r'window\.__PRELOADED_STATE__\s*=\s*({.*?});',
    r'window\.initialData\s*=\s*({.*?});',
    r'__NEXT_DATA__["\']?\s*type=["\']application/json["\'].*?>(.*?)</script>',
    r'data-props=["\']({.*?})["\']',
]

for i, pattern in enumerate(patterns):
    matches = re.findall(pattern, html_content, re.DOTALL)
    if matches:
        print(f"\n✓ Pattern {i+1} found {len(matches)} matches")
        for j, match in enumerate(matches[:2]):  # Show first 2
            print(f"\nMatch {j+1} (first 500 chars):")
            print(match[:500])

# Look for script tags with JSON
soup = BeautifulSoup(response.content, 'lxml')
scripts = soup.find_all('script', type='application/json')
print(f"\n\n✓ Found {len(scripts)} script tags with type='application/json'")
for i, script in enumerate(scripts[:3]):
    print(f"\nScript {i+1} (first 500 chars):")
    print(script.string[:500] if script.string else "Empty")

# Try to find API endpoint by looking at script sources
print("\n\n" + "=" * 80)
print("Checking for API endpoints in script tags...")
all_scripts = soup.find_all('script', src=True)
api_patterns = ['api', 'data', 'ajax', 'json']
for script in all_scripts:
    src = script.get('src', '')
    if any(pattern in src.lower() for pattern in api_patterns):
        print(f"Potential API script: {src}")

# Check if there's a JSON API endpoint
print("\n" + "=" * 80)
print("Trying JSON API endpoint...")
json_url = url.replace('/lots?', '/lots.json?')
json_response = requests.get(json_url, headers=headers)
print(f"JSON endpoint: {json_url}")
print(f"Status: {json_response.status_code}")
if json_response.status_code == 200:
    print(f"Content-Type: {json_response.headers.get('content-type')}")
    try:
        data = json_response.json()
        print(f"✓ Valid JSON! Keys: {list(data.keys())}")
        print(f"Preview: {str(data)[:500]}")
    except:
        print(f"Not valid JSON. Content preview: {json_response.text[:500]}")
