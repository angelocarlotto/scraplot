# Auction Data Scraper

Web scraping application to collect and analyze auction data from any website with **automatic page discovery**.

## Features

- 🔍 **Automatic Page Discovery** - Automatically detects total pages and scrapes all available pages
- 🚀 **Multi-threaded Scraping** - Uses 10 concurrent threads for fast parallel scraping
- 🌐 **Universal Scraper** - Works with any website, with specialized support for Regal Auctions
- 🎨 **Beautiful Web Interface** - Modern React UI with sortable/filterable tables
- 🔌 **REST API** - Flask API for programmatic access
- 💾 **Multiple Formats** - Saves data in CSV, JSON, and Excel formats
- 📊 **Vehicle Ranking** - Intelligent scoring system for vehicle comparison

## Quick Start

### Option 1: Use the Web Interface (Recommended)

1. Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the application:
```bash
./start_app.sh
```

3. Open your browser to `http://localhost:8000`

4. Enter a URL and click **Scrape URL**. The "Automatically discover and scrape all pages" checkbox is enabled by default!

### Option 2: Use the Command Line

```bash
python scraper.py
```

## Automatic Page Discovery

The scraper now automatically:
1. **Discovers** the total number of pages available on the website
2. **Generates** URLs for all pages
3. **Scrapes** all pages in parallel using 10 threads
4. **Combines** all results into a single dataset

### How It Works

For Regal Auctions URLs, the scraper:
- Analyzes pagination elements (page links, "Page X of Y" text, navigation)
- Detects the highest page number
- Scrapes all pages concurrently (up to 10 at a time)
- Returns combined results with timing information

### API Usage

```bash
curl -X POST http://localhost:5001/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1",
    "wait_time": 5,
    "scrape_all_pages": true
  }'
```

Response includes:
```json
{
  "success": true,
  "data": {
    "structured_data": {
      "type": "regal_auctions",
      "total_pages": 8,
      "total_lots": 367,
      "scraping_time": "7.85s",
      "lots": [...]
    }
  }
}
```

## Project Structure

```
scraplot/
├── scraper.py          # Main scraping script
├── analyze.py          # Data analysis script
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data/              # Output directory (created automatically)
│   ├── auction_data.csv
│   ├── auction_data.json
│   └── auction_data.xlsx
└── .github/
    └── copilot-instructions.md
```

## Configuration

Edit the following variables in `scraper.py` to customize:

```python
BASE_URL = "https://bids.regalauctions.com"
AUCTION_ID = "1778628"
DATE = "2025-10-24"
```

## Data Fields

The scraper collects the following information for each lot:
- Page number
- Lot number
- Title
- Description
- Current bid
- Estimate
- Number of bids
- Image URL
- Lot URL

## Notes

- The scraper includes a 1-second delay between page requests to be respectful to the server
- HTML selectors may need adjustment if the website structure changes
- Make sure you have permission to scrape the target website

## License

MIT License
