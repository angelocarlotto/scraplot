"""
Debug script to analyze pagination structure
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
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

url = "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1"
driver = create_driver()

try:
    print("Loading page...")
    driver.get(url)
    time.sleep(5)
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')
    
    # Save HTML for inspection
    with open('debug/pagination_analysis.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("\n" + "="*70)
    print("PAGINATION ANALYSIS")
    print("="*70)
    
    # Look for all links with page parameter
    print("\n1. Links with 'page=' parameter:")
    page_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        if 'page=' in href:
            text = link.get_text(strip=True)
            print(f"   - {text}: {href}")
            page_links.append(href)
    
    # Look for pagination navigation
    print("\n2. Pagination navigation elements:")
    nav_elements = soup.find_all('nav')
    for nav in nav_elements:
        nav_class = nav.get('class', [])
        print(f"   - <nav class='{nav_class}'>")
        links = nav.find_all('a')
        for link in links:
            print(f"     Link: {link.get_text(strip=True)} -> {link.get('href', '')}")
    
    # Look for pagination in other common containers
    print("\n3. Elements with 'pagination' in class:")
    pag_elements = soup.find_all(class_=lambda x: x and 'pagination' in str(x).lower())
    for elem in pag_elements:
        print(f"   - <{elem.name} class='{elem.get('class')}'>")
        print(f"     Text: {elem.get_text(strip=True)[:100]}")
    
    # Look for page info text
    print("\n4. Searching for 'Page X of Y' text patterns:")
    text_content = soup.get_text()
    import re
    matches = re.findall(r'(Page\s+\d+\s+of\s+\d+)', text_content, re.IGNORECASE)
    for match in matches:
        print(f"   - Found: {match}")
    
    # Look for ul/li pagination
    print("\n5. Looking for ul/li pagination structures:")
    uls = soup.find_all('ul')
    for ul in uls:
        ul_class = ul.get('class', [])
        if 'pagination' in str(ul_class).lower() or 'pager' in str(ul_class).lower():
            print(f"   - <ul class='{ul_class}'>")
            for li in ul.find_all('li'):
                link = li.find('a')
                if link:
                    print(f"     {li.get_text(strip=True)} -> {link.get('href', '')}")
    
    # Look for buttons
    print("\n6. Pagination buttons:")
    buttons = soup.find_all('button')
    for button in buttons:
        btn_text = button.get_text(strip=True)
        if any(word in btn_text.lower() for word in ['next', 'prev', 'page']):
            print(f"   - Button: {btn_text}")
    
    print("\n" + "="*70)
    print("HTML saved to: debug/pagination_analysis.html")
    print("="*70)
    
finally:
    driver.quit()
