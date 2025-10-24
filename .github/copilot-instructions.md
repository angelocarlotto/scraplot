# Copilot Instructions for Auction Scraper Project

## Project Overview
Python web scraping application with automatic page discovery to collect auction data from any website.

## Progress Tracking

- [x] Verify that the copilot-instructions.md file in the .github directory is created.
- [x] Clarify Project Requirements - Web scraping project for auction data
- [x] Scaffold the Project - Created scraper.py, analyze.py, requirements.txt, README.md
- [x] Customize the Project - Configured for Regal Auctions URL structure
- [x] Install Required Extensions - Not required for Python project
- [x] Compile the Project - Dependencies installed successfully
- [x] Create and Run Task - Scraper successfully ran and collected 367 lots
- [x] Launch the Project - Scraper working with Selenium
- [x] Multithreading Implementation - 10 parallel threads for fast scraping
- [x] Web API Creation - Flask REST API with CORS support
- [x] React Interface - Beautiful UI with sortable/filterable tables
- [x] Automatic Page Discovery - Detects and scrapes all pages automatically
- [x] Ensure Documentation is Complete - README and instructions updated

## Key Features

### Automatic Page Discovery
- Automatically detects total number of pages on any website
- Parses pagination elements (page links, "Page X of Y" text, navigation)
- Scrapes all pages in parallel using ThreadPoolExecutor
- No hardcoded page limits

### Architecture
- **Backend**: Flask REST API on port 5001
- **Frontend**: React SPA served on port 8000
- **Scraping**: Selenium WebDriver with Chrome headless
- **Threading**: 10 concurrent workers for parallel page scraping

### API Endpoint
POST /scrape
- url (required): URL to scrape
- wait_time (optional, default: 5): Seconds to wait for JavaScript
- scrape_all_pages (optional, default: false): Auto-discover and scrape all pages

### Files
- api.py: Flask API with page discovery logic
- index.html: React interface with checkbox for "scrape all pages"
- scraper.py: Command-line scraper (needs update for page discovery)
- test_quick_discovery.py: Quick test script for page discovery

## Project Details
- Language: Python 3.14.0t
- Main Libraries: Selenium 4.25.0, Flask 3.1.2, BeautifulSoup4, Pandas
- Threading: ThreadPoolExecutor with 10 max workers
- Performance: ~8 seconds for 8 pages (367 lots)
