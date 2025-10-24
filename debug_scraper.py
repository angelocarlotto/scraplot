"""
Debug script to examine what HTML is being received from the auction site
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1"
print(f"Testing URL: {url}\n")

driver = create_driver()

try:
    print("Loading page...")
    driver.get(url)
    
    print("Waiting 5 seconds for JavaScript to render...")
    time.sleep(5)
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    print("\n=== PAGE ANALYSIS ===\n")
    
    # Check for lot elements
    print("1. Looking for <div class='lot'>...")
    lot_divs = soup.find_all('div', class_='lot')
    print(f"   Found: {len(lot_divs)} elements")
    
    # Check for alternative lot classes
    print("\n2. Looking for divs with 'lot' in class name...")
    lot_variants = soup.find_all('div', class_=lambda x: x and 'lot' in x.lower())
    print(f"   Found: {len(lot_variants)} elements")
    if lot_variants:
        print("   Classes found:")
        for variant in lot_variants[:5]:
            print(f"   - {variant.get('class')}")
    
    # Check for any divs with data attributes
    print("\n3. Looking for divs with data-* attributes...")
    data_divs = soup.find_all('div', attrs={'data-lot-id': True})
    print(f"   Found with data-lot-id: {len(data_divs)}")
    
    data_divs2 = soup.find_all('div', attrs={'data-id': True})
    print(f"   Found with data-id: {len(data_divs2)}")
    
    # Check for table rows
    print("\n4. Looking for table rows...")
    rows = soup.find_all('tr')
    print(f"   Found: {len(rows)} table rows")
    
    # Check for list items
    print("\n5. Looking for list items...")
    list_items = soup.find_all('li')
    print(f"   Found: {len(list_items)} list items")
    
    # Look for article tags
    print("\n6. Looking for article tags...")
    articles = soup.find_all('article')
    print(f"   Found: {len(articles)} articles")
    
    # Check page title
    print("\n7. Page title:")
    print(f"   {soup.title.string if soup.title else 'No title'}")
    
    # Check for specific text patterns
    print("\n8. Searching for auction-related text...")
    text_content = soup.get_text()
    
    if 'lot' in text_content.lower():
        print("   ✓ Found 'lot' in page text")
    if 'bid' in text_content.lower():
        print("   ✓ Found 'bid' in page text")
    if 'auction' in text_content.lower():
        print("   ✓ Found 'auction' in page text")
    
    # Save HTML for inspection
    print("\n9. Saving full HTML to debug_page.html...")
    with open('debug_page.html', 'w', encoding='utf-8') as f:
        f.write(page_source)
    print("   ✓ Saved!")
    
    # Show first few main content divs
    print("\n10. Main content structure:")
    main_divs = soup.find_all('div', limit=20)
    for i, div in enumerate(main_divs[:10], 1):
        classes = div.get('class', [])
        id_attr = div.get('id', '')
        print(f"   Div {i}: classes={classes}, id='{id_attr}'")
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("\nCheck 'debug_page.html' for full page source")

finally:
    driver.quit()
