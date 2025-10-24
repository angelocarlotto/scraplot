"""
Web API for scraping any URL
Accepts a URL and returns scraped data in JSON format
Also serves static files for the web interface
"""

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import os
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes

# Global progress tracker
progress_queues = {}
progress_lock = threading.Lock()


def create_driver(headless=True):
    """Create a new Selenium WebDriver instance"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    # Check if running in production (Railway) or locally
    chrome_bin = os.environ.get('CHROME_BIN')
    if chrome_bin:
        # Production: use system Chrome and let webdriver-manager handle driver
        chrome_options.binary_location = chrome_bin
    
    try:
        # Let webdriver-manager download and manage the correct ChromeDriver version
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error creating Chrome driver: {e}")
        raise


def scrape_generic_url(url: str, wait_time: int = 5, scrape_all_pages: bool = False, max_workers: int = 1) -> dict:
    """
    Scrape any URL and return structured data
    
    Args:
        url: URL to scrape
        wait_time: Time to wait for JavaScript rendering (seconds)
        scrape_all_pages: If True, automatically discover and scrape all pages
        max_workers: Number of parallel threads for scraping multiple pages (default: 1)
        
    Returns:
        Dictionary with scraped data
    """
    # Check if it's the Regal Auctions site and scrape_all_pages is True
    if 'regalauctions.com' in url and scrape_all_pages:
        return scrape_all_auction_pages(url, wait_time, max_workers)
    
    driver = create_driver()
    
    try:
        driver.get(url)
        time.sleep(wait_time)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')
        
        # Extract basic page information
        result = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'meta_description': '',
            'raw_html': page_source,
            'text_content': soup.get_text(separator=' ', strip=True)[:5000],  # First 5000 chars
            'links': [],
            'images': [],
            'structured_data': {}
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            result['meta_description'] = meta_desc.get('content', '')
        
        # Extract all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            if href:
                result['links'].append({'url': href, 'text': text})
        
        # Extract all images
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                result['images'].append({'src': src, 'alt': alt})
        
        # Check if it's the Regal Auctions site and extract lot data
        if 'regalauctions.com' in url:
            result['structured_data'] = scrape_regal_auctions(soup, url)
        
        return result
        
    except Exception as e:
        return {
            'url': url,
            'error': str(e),
            'success': False
        }
    finally:
        driver.quit()


def discover_total_pages(base_url, wait_time=5):
    """
    Discover the total number of pages available on a website.
    Returns the total number of pages found.
    """
    print(f"\n🔍 Discovering total pages for: {base_url}")
    
    driver = create_driver()
    max_page = 1
    
    try:
        driver.get(base_url)
        time.sleep(wait_time)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Strategy 1: Look for "of X" text patterns (most reliable)
        text_content = soup.get_text()
        of_pattern = re.search(r'of\s+(\d+)', text_content, re.IGNORECASE)
        if of_pattern:
            total_pages = int(of_pattern.group(1))
            max_page = max(max_page, total_pages)
            print(f"   Strategy 1 ('of X' pattern): Found {total_pages} pages")
        
        # Strategy 2: Look for page select dropdowns
        select_elements = soup.find_all('select')
        for select in select_elements:
            options = select.find_all('option')
            for option in options:
                try:
                    page_num = int(option.get_text().strip())
                    max_page = max(max_page, page_num)
                except:
                    pass
        
        if max_page > 1:
            print(f"   Strategy 2 (select dropdown): Found {max_page} pages")
        
        # Strategy 3: Look for "Page X of Y" text
        page_of_pattern = re.search(r'Page\s+\d+\s+of\s+(\d+)', text_content, re.IGNORECASE)
        if page_of_pattern:
            total_pages = int(page_of_pattern.group(1))
            max_page = max(max_page, total_pages)
            print(f"   Strategy 3 ('Page X of Y'): Found {total_pages} pages")
        
        # Strategy 4: Look for page links with ?page= parameter
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            match = re.search(r'[?&]page=(\d+)', href)
            if match:
                page_num = int(match.group(1))
                max_page = max(max_page, page_num)
        
        if max_page > 1:
            print(f"   Strategy 4 (URL params): Found max page {max_page}")
        
        # Strategy 5: Look for pagination navigation elements
        pagination = soup.find('nav', {'class': re.compile('pagination', re.IGNORECASE)})
        if not pagination:
            pagination = soup.find('div', {'class': re.compile('pagination', re.IGNORECASE)})
        
        if pagination:
            page_links = pagination.find_all('a')
            for link in page_links:
                try:
                    page_num = int(link.get_text().strip())
                    max_page = max(max_page, page_num)
                except:
                    pass
            if max_page > 1:
                print(f"   Strategy 5 (pagination nav): Found max page {max_page}")
        
        print(f"✅ Total pages discovered: {max_page}\n")
        return max_page
        
    except Exception as e:
        print(f"❌ Error discovering pages: {str(e)}")
        return 1
    finally:
        driver.quit()


def scrape_single_page(url: str, page_num: int, wait_time: int, lock: threading.Lock, progress_queue=None) -> list:
    """
    Scrape a single page in a thread
    
    Args:
        url: Base URL
        page_num: Page number to scrape
        wait_time: Wait time for JavaScript
        lock: Thread lock for printing
        progress_queue: Queue for sending progress updates
        
    Returns:
        List of lots from this page
    """
    # Modify URL to include page number
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    query_params['page'] = [str(page_num)]
    new_query = urlencode(query_params, doseq=True)
    page_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    
    if progress_queue:
        progress_queue.put({
            'type': 'page_start',
            'page': page_num,
            'message': f'Starting page {page_num}...'
        })
    
    driver = create_driver()
    
    try:
        driver.get(page_url)
        time.sleep(wait_time)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        lot_items = soup.find_all('div', class_='lot-card')
        
        lots = []
        
        for item in lot_items:
            lot_data = extract_lot_from_element(item)
            if lot_data and (lot_data.get('lot_number') or lot_data.get('title')):
                lot_data['page'] = page_num
                lots.append(lot_data)
        
        with lock:
            print(f"[Thread] Page {page_num}: Found {len(lots)} lots")
        
        if progress_queue:
            progress_queue.put({
                'type': 'page_complete',
                'page': page_num,
                'lots_found': len(lots),
                'message': f'Page {page_num}: Found {len(lots)} lots'
            })
        
        return lots
        
    except Exception as e:
        with lock:
            print(f"[Thread] Error on page {page_num}: {e}")
        
        if progress_queue:
            progress_queue.put({
                'type': 'page_error',
                'page': page_num,
                'error': str(e),
                'message': f'Error on page {page_num}: {str(e)}'
            })
        
        return []
    finally:
        driver.quit()


def scrape_all_auction_pages(url: str, wait_time: int = 30, max_workers: int = 1, progress_queue=None) -> dict:
    """
    Automatically discover total pages and scrape all of them
    
    Args:
        url: Base URL to scrape
        wait_time: Wait time for JavaScript
        max_workers: Maximum concurrent threads
        progress_queue: Queue for sending progress updates
        
    Returns:
        Dictionary with all scraped data
    """
    if progress_queue:
        progress_queue.put({
            'type': 'discovery_start',
            'message': 'Discovering total pages...'
        })
    
    print(f"Discovering total pages for: {url}")
    total_pages = discover_total_pages(url, wait_time)
    print(f"Found {total_pages} pages to scrape")
    
    if progress_queue:
        progress_queue.put({
            'type': 'discovery_complete',
            'total_pages': total_pages,
            'message': f'Found {total_pages} pages to scrape'
        })
    
    all_lots = []
    lock = threading.Lock()
    
    print(f"Starting parallel scraping with {max_workers} threads...")
    
    if progress_queue:
        progress_queue.put({
            'type': 'scraping_start',
            'total_pages': total_pages,
            'max_workers': max_workers,
            'message': f'Starting parallel scraping with {max_workers} threads...'
        })
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor for parallel scraping
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scrape_single_page, url, page, wait_time, lock, progress_queue): page 
            for page in range(1, total_pages + 1)
        }
        
        for future in as_completed(futures):
            page = futures[future]
            try:
                lots = future.result()
                with lock:
                    all_lots.extend(lots)
            except Exception as e:
                print(f"Exception for page {page}: {e}")
    
    elapsed_time = time.time() - start_time
    
    print(f"Scraping completed in {elapsed_time:.2f} seconds")
    print(f"Total lots scraped: {len(all_lots)}")
    
    if progress_queue:
        progress_queue.put({
            'type': 'scraping_complete',
            'total_lots': len(all_lots),
            'elapsed_time': elapsed_time,
            'message': f'Scraping completed! Found {len(all_lots)} lots in {elapsed_time:.2f}s'
        })
    
    return {
        'type': 'regal_auctions',
        'total_pages': total_pages,
        'total_lots': len(all_lots),
        'scraping_time': f"{elapsed_time:.2f}s",
        'lots': all_lots
    }


def extract_lot_from_element(item) -> dict:
    """Extract lot data from a BeautifulSoup element"""
    try:
        # Extract lot number
        lot_number_elem = item.find('div', class_='lot-number')
        lot_number = lot_number_elem.find('strong').get_text(strip=True) if lot_number_elem and lot_number_elem.find('strong') else ""
        
        # Extract title
        title_elem = item.find('div', class_='lot__name')
        title = title_elem.get_text(strip=True) if title_elem else ""
        
        # Extract description
        desc_elem = item.find('div', class_='lot__description')
        description = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # Extract image
        img_elem = item.find('img')
        image_url = img_elem.get('src', '') if img_elem else ""
        
        # Extract link
        link_elem = desc_elem.find('a') if desc_elem else None
        lot_url = link_elem.get('href', '') if link_elem else ""
        
        # Extract bidding info
        bid_elem = item.find('div', class_='lot__bidding')
        starting_bid = ""
        if bid_elem:
            bid_match = bid_elem.find('span', class_='fs-4')
            if bid_match:
                starting_bid = bid_match.get_text(strip=True)
        
        # Extract table data
        odometer = ""
        engine = ""
        declarations = ""
        options = ""
        reserve_price = ""
        
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
        
        return {
            'lot_number': lot_number,
            'title': title,
            'description': description[:500],
            'image_url': image_url,
            'lot_url': lot_url,
            'starting_bid': starting_bid,
            'reserve_price': reserve_price,
            'odometer': odometer,
            'engine': engine,
            'declarations': declarations,
            'options': options,
        }
    except Exception as e:
        return {}


def scrape_regal_auctions(soup: BeautifulSoup, url: str) -> dict:
    """Extract structured data from Regal Auctions pages"""
    lots = []
    
    # Find all lot cards
    lot_items = soup.find_all('div', class_='lot-card')
    
    for item in lot_items:
        try:
            # Extract lot number
            lot_number_elem = item.find('div', class_='lot-number')
            lot_number = lot_number_elem.find('strong').get_text(strip=True) if lot_number_elem and lot_number_elem.find('strong') else ""
            
            # Extract title
            title_elem = item.find('div', class_='lot__name')
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            # Extract description
            desc_elem = item.find('div', class_='lot__description')
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract image
            img_elem = item.find('img')
            image_url = img_elem.get('src', '') if img_elem else ""
            
            # Extract link
            link_elem = desc_elem.find('a') if desc_elem else None
            lot_url = link_elem.get('href', '') if link_elem else ""
            
            # Extract bidding info
            bid_elem = item.find('div', class_='lot__bidding')
            starting_bid = ""
            if bid_elem:
                bid_match = bid_elem.find('span', class_='fs-4')
                if bid_match:
                    starting_bid = bid_match.get_text(strip=True)
            
            # Extract table data
            odometer = ""
            engine = ""
            declarations = ""
            options = ""
            reserve_price = ""
            
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
                'lot_number': lot_number,
                'title': title,
                'description': description[:500],
                'image_url': image_url,
                'lot_url': lot_url,
                'starting_bid': starting_bid,
                'reserve_price': reserve_price,
                'odometer': odometer,
                'engine': engine,
                'declarations': declarations,
                'options': options,
            }
            
            if lot_data['lot_number'] or lot_data['title']:
                lots.append(lot_data)
                
        except Exception as e:
            continue
    
    return {
        'type': 'regal_auctions',
        'total_lots': len(lots),
        'lots': lots
    }


@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    """
    Scrape a URL and return structured data
    
    Request body:
    {
        "url": "https://example.com",
        "wait_time": 5,  # optional, default is 5 seconds
        "scrape_all_pages": true,  # optional, default is false, auto-discovers and scrapes all pages
        "max_workers": 1  # optional, default is 1, number of parallel threads for scraping
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required in request body'
            }), 400
        
        url = data['url']
        wait_time = data.get('wait_time', 5)
        scrape_all_pages = data.get('scrape_all_pages', False)
        max_workers = data.get('max_workers', 1)
        
        # Scrape the URL
        result = scrape_generic_url(url, wait_time, scrape_all_pages, max_workers)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/scrape-stream', methods=['POST'])
def scrape_stream():
    """
    Scrape with real-time progress updates via Server-Sent Events (SSE)
    
    Request body:
    {
        "url": "https://example.com",
        "wait_time": 5,
        "scrape_all_pages": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required in request body'
            }), 400
        
        url = data['url']
        wait_time = data.get('wait_time', 5)
        scrape_all_pages = data.get('scrape_all_pages', False)
        max_workers = data.get('max_workers', 1)
        
        # Create a unique queue for this request
        progress_queue = queue.Queue()
        
        def generate():
            # Start scraping in a background thread
            result_container = {}
            
            def scrape_task():
                try:
                    if 'regalauctions.com' in url and scrape_all_pages:
                        result = scrape_all_auction_pages(url, wait_time, max_workers, progress_queue=progress_queue)
                    else:
                        result = scrape_generic_url(url, wait_time, scrape_all_pages, max_workers)
                    result_container['data'] = result
                    result_container['success'] = True
                except Exception as e:
                    result_container['error'] = str(e)
                    result_container['success'] = False
                finally:
                    progress_queue.put({'type': 'done'})
            
            # Start the scraping thread
            thread = threading.Thread(target=scrape_task)
            thread.start()
            
            # Stream progress updates
            while True:
                try:
                    update = progress_queue.get(timeout=30)
                    
                    if update['type'] == 'done':
                        # Send final result
                        if result_container.get('success'):
                            yield f"data: {json.dumps({'type': 'result', 'success': True, 'data': result_container['data']})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'error', 'success': False, 'error': result_container.get('error', 'Unknown error')})}\n\n"
                        break
                    else:
                        # Send progress update
                        yield f"data: {json.dumps(update)}\n\n"
                        
                except queue.Empty:
                    # Send keepalive
                    yield f"data: {json.dumps({'type': 'keepalive'})}\n\n"
            
            thread.join()
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Web Scraper API',
        'version': '1.0.0'
    })


@app.route('/')
def home():
    """Serve the main web interface"""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS, images, etc.)"""
    if os.path.exists(path):
        return send_from_directory('.', path)
    return jsonify({'error': 'File not found'}), 404


@app.route('/api', methods=['GET'])
def api_docs():
    """API documentation"""
    return jsonify({
        'name': 'Web Scraper API',
        'version': '1.0.0',
        'description': 'API to scrape any URL and return structured data',
        'endpoints': {
            'POST /scrape': {
                'description': 'Scrape a URL and return data in JSON format',
                'request_body': {
                    'url': 'string (required) - URL to scrape',
                    'wait_time': 'integer (optional) - Seconds to wait for JS rendering (default: 5)',
                    'scrape_all_pages': 'boolean (optional) - Automatically discover and scrape all pages (default: false)'
                },
                'example': {
                    'url': 'https://example.com',
                    'wait_time': 5,
                    'scrape_all_pages': True
                }
            },
            'GET /health': {
                'description': 'Health check endpoint'
            },
            'GET /api': {
                'description': 'API documentation (this page)'
            }
        }
    })


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    
    print("="*70)
    print("Starting Web Scraper API...")
    print("="*70)
    print("API Endpoints:")
    print("  GET  /         - API documentation")
    print("  GET  /health   - Health check")
    print("  POST /scrape   - Scrape a URL")
    print("="*70)
    print(f"\nRunning on port: {port}")
    print("\nExample usage:")
    print(f'  curl -X POST http://localhost:{port}/scrape \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"url": "https://example.com"}\'')
    print("="*70)
    app.run(debug=False, host='0.0.0.0', port=port)
