"""
Auction Data Scraper for Regal Auctions
Scrapes lot data from pages 1-8 and saves to CSV/JSON
Uses Selenium for JavaScript-rendered content
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from typing import List, Dict
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class AuctionScraper:
    """Scraper for Regal Auctions website"""
    
    def __init__(self, base_url: str, auction_id: str, date: str, headless: bool = True):
        """
        Initialize the scraper
        
        Args:
            base_url: Base URL of the auction site
            auction_id: Auction ID
            date: Auction date (YYYY-MM-DD format)
            headless: Run browser in headless mode
        """
        self.base_url = base_url
        self.auction_id = auction_id
        self.date = date
        self.headless = headless
        self.driver = None
        self.lock = threading.Lock()  # Thread safety for shared resources
        
    def setup_driver(self):
        """Setup Selenium WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Browser driver initialized")
        
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")
        
    def get_page_url(self, page_num: int) -> str:
        """Generate URL for a specific page"""
        return f"{self.base_url}/auctions/{self.auction_id}/lots?date={self.date}&page={page_num}"
    
    def scrape_page(self, page_num: int) -> List[Dict]:
        """
        Scrape data from a single page
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            List of lot dictionaries
        """
        # Create a new driver for this thread
        driver = self._create_driver()
        
        url = self.get_page_url(page_num)
        print(f"[Thread-{threading.current_thread().name}] Scraping page {page_num}: {url}")
        
        try:
            driver.get(url)
            
            # Wait for page to load
            time.sleep(5)  # Give JavaScript time to render
            
            # Get the rendered page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Save HTML for debugging (thread-safe)
            with self.lock:
                os.makedirs('debug', exist_ok=True)
                with open(f'debug/page_{page_num}_rendered.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"[Thread-{threading.current_thread().name}] Saved rendered HTML to debug/page_{page_num}_rendered.html")
            
            # Find all lot cards
            lot_items = soup.find_all('div', class_='lot-card')
            
            if not lot_items:
                print(f"[Thread-{threading.current_thread().name}] Warning: No lot items found on page {page_num}")
                return []
            
            print(f"[Thread-{threading.current_thread().name}] Found {len(lot_items)} lot cards on page {page_num}")
            
            # Extract data from each lot
            lots = []
            for item in lot_items:
                lot_data = self.extract_lot_data(item, page_num)
                if lot_data and (lot_data.get('lot_number') or lot_data.get('title')):
                    lots.append(lot_data)
            
            print(f"[Thread-{threading.current_thread().name}] Extracted {len(lots)} valid lots from page {page_num}")
            return lots
            
        except Exception as e:
            print(f"[Thread-{threading.current_thread().name}] Error scraping page {page_num}: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            # Close the driver for this thread
            driver.quit()
    
    def _create_driver(self):
        """Create a new WebDriver instance for thread use"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    
    def extract_lot_data(self, item, page_num: int) -> Dict:
        """
        Extract data from a single lot item
        
        Args:
            item: BeautifulSoup element containing lot data
            page_num: Current page number
            
        Returns:
            Dictionary with lot data
        """
        try:
            # Extract lot number from .lot-number
            lot_number_elem = item.find('div', class_='lot-number')
            lot_number = lot_number_elem.find('strong').get_text(strip=True) if lot_number_elem and lot_number_elem.find('strong') else ""
            
            # Extract title from .lot__name
            title_elem = item.find('div', class_='lot__name')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract description from .lot__description
            desc_elem = item.find('div', class_='lot__description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract image URL
            img_elem = item.find('img')
            image_url = img_elem.get('src', '') if img_elem else ""
            
            # Extract link URL (from image or description)
            link_elem = desc_elem.find('a') if desc_elem else None
            lot_url = link_elem.get('href', '') if link_elem else ""
            
            # Extract bidding information
            bid_elem = item.find('div', class_='lot__bidding')
            current_bid = ""
            reserve_price = ""
            starting_bid = ""
            
            if bid_elem:
                # Try to find starting bid
                bid_text = bid_elem.get_text()
                if 'STARTING BID' in bid_text:
                    starting_bid_match = bid_elem.find('span', class_='fs-4')
                    if starting_bid_match:
                        starting_bid = starting_bid_match.get_text(strip=True)
                
                # Check for reserve price in description
                if desc_elem and 'RESERVE PRICE' in desc_elem.get_text():
                    reserve_match = desc_elem.find('td')
                    if reserve_match:
                        # Find the next td after RESERVE PRICE
                        reserve_td = reserve_match.find_next('td')
                        if reserve_td:
                            reserve_price = reserve_td.get_text(strip=True)
            
            # Extract additional data from table in description
            odometer = ""
            engine = ""
            declarations = ""
            options = ""
            
            if desc_elem:
                table = desc_elem.find('table')
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True).upper()
                            value = cells[1].get_text(strip=True)
                            
                            if 'ODOMETER' in key:
                                odometer = value
                            elif 'ENGINE' in key:
                                engine = value
                            elif 'DECLARATION' in key:
                                declarations = value
                            elif 'OPTIONS' in key:
                                options = value
                            elif 'RESERVE' in key:
                                reserve_price = value
            
            lot_data = {
                'page': page_num,
                'lot_number': lot_number,
                'title': title,
                'description': description[:500] if description else "",  # Limit description length
                'image_url': image_url,
                'lot_url': lot_url,
                'starting_bid': starting_bid,
                'current_bid': current_bid,
                'reserve_price': reserve_price,
                'odometer': odometer,
                'engine': engine,
                'declarations': declarations,
                'options': options,
            }
            
            # Clean up URLs
            if lot_data['lot_url'] and not lot_data['lot_url'].startswith('http'):
                lot_data['lot_url'] = self.base_url + lot_data['lot_url']
            
            if lot_data['image_url'] and not lot_data['image_url'].startswith('http'):
                lot_data['image_url'] = self.base_url + lot_data['image_url']
            
            return lot_data
            
        except Exception as e:
            print(f"Error extracting lot data: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _safe_extract(self, element, attrs: List[str]) -> str:
        """Safely extract attribute value"""
        for attr in attrs:
            value = element.get(attr)
            if value:
                return str(value).strip()
        return ""
    
    def _safe_extract_text(self, element, selectors: List[str]) -> str:
        """Safely extract text from element using multiple selectors"""
        for selector in selectors:
            try:
                found = element.select_one(selector) if selector.startswith('.') or selector.startswith('#') else element.find(selector)
                if found and found.get_text(strip=True):
                    return found.get_text(strip=True)
            except:
                continue
        return ""
    
    def _safe_extract_attr(self, element, tag: str, attr: str) -> str:
        """Safely extract attribute from a tag"""
        try:
            found = element.find(tag)
            if found:
                return found.get(attr, "")
        except:
            pass
        return ""
    
    def scrape_all_pages(self, start_page: int = 1, end_page: int = 8, max_workers: int = 3) -> pd.DataFrame:
        """
        Scrape all pages from start to end using multithreading
        
        Args:
            start_page: Starting page number
            end_page: Ending page number
            max_workers: Maximum number of concurrent threads (default: 3)
            
        Returns:
            DataFrame with all scraped data
        """
        all_lots = []
        pages = list(range(start_page, end_page + 1))
        
        print(f"🚀 Starting parallel scraping with {max_workers} threads...")
        print("=" * 70)
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all page scraping tasks
            future_to_page = {executor.submit(self.scrape_page, page): page for page in pages}
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    lots = future.result()
                    with self.lock:  # Thread-safe append
                        all_lots.extend(lots)
                except Exception as e:
                    print(f"❌ Exception occurred for page {page}: {e}")
        
        elapsed_time = time.time() - start_time
        
        print("=" * 70)
        print(f"✅ Parallel scraping completed in {elapsed_time:.2f} seconds")
        
        df = pd.DataFrame(all_lots)
        
        # Sort by page number for consistent ordering
        if not df.empty and 'page' in df.columns:
            df = df.sort_values('page').reset_index(drop=True)
        
        print(f"\nTotal lots scraped: {len(df)}")
        
        return df
    
    def save_data(self, df: pd.DataFrame, format: str = 'both'):
        """
        Save scraped data to file
        
        Args:
            df: DataFrame with scraped data
            format: 'csv', 'json', or 'both'
        """
        os.makedirs('data', exist_ok=True)
        
        if format in ['csv', 'both']:
            csv_path = 'data/auction_data.csv'
            df.to_csv(csv_path, index=False)
            print(f"Data saved to {csv_path}")
        
        if format in ['json', 'both']:
            json_path = 'data/auction_data.json'
            # Remove raw_html before saving to JSON for cleaner output
            df_clean = df.drop(columns=['raw_html'], errors='ignore')
            df_clean.to_json(json_path, orient='records', indent=2)
            print(f"Data saved to {json_path}")
        
        # Also save as Excel for easier viewing
        excel_path = 'data/auction_data.xlsx'
        df_clean = df.drop(columns=['raw_html'], errors='ignore')
        df_clean.to_excel(excel_path, index=False)
        print(f"Data saved to {excel_path}")


def main():
    """Main function to run the scraper"""
    
    # Configuration
    BASE_URL = "https://bids.regalauctions.com"
    AUCTION_ID = "1778628"
    DATE = "2025-10-24"
    MAX_THREADS = 10  # Maximum concurrent threads
    
    # Create scraper instance
    print("Initializing auction scraper with multithreading support...")
    print(f"Using up to {MAX_THREADS} parallel threads for faster scraping")
    print("=" * 70)
    
    scraper = AuctionScraper(BASE_URL, AUCTION_ID, DATE, headless=True)
    
    # Scrape all pages (1-8) with multithreading
    print("\nStarting parallel auction data scraping...")
    print("=" * 70)
    
    df = scraper.scrape_all_pages(start_page=1, end_page=8, max_workers=MAX_THREADS)
    
    # Save the data
    if not df.empty:
        scraper.save_data(df, format='both')
        print("\n" + "=" * 70)
        print("Scraping completed successfully!")
        print(f"Total items scraped: {len(df)}")
        
        # Show available columns
        print(f"\nData columns: {', '.join(df.columns.tolist())}")
        
        print("\nData preview (first 3 rows):")
        print(df.head(3).to_string())
        
        print("\n" + "=" * 70)
        print("Next steps:")
        print("1. Check the 'debug' folder for rendered HTML files")
        print("2. Run 'python analyze.py' to query the scraped data")
        print("3. Open 'data/auction_data.xlsx' in Excel for easy viewing")
    else:
        print("\n" + "=" * 70)
        print("No data was scraped.")
        print("Please check the debug HTML files in the 'debug' folder")
        print("The HTML selectors may need to be adjusted based on the actual page structure")


if __name__ == "__main__":
    main()
