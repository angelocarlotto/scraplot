# Using Automatic Page Discovery

## Quick Start Guide

### 1. Start the Application

```bash
cd /Users/angelocarlotto/Desktop/github2/scraplot
./start_app.sh
```

The script will:
- Start the API server on port 5001
- Start the web interface on port 8000
- Display URLs for both services

### 2. Open the Web Interface

Open your browser and navigate to:
```
http://localhost:8000
```

### 3. Use the Scraper

#### Default Settings (Recommended)
The interface opens with:
- **URL field**: Pre-filled with Regal Auctions URL
- **Checkbox**: "Automatically discover and scrape all pages" ✅ **CHECKED**

Simply click **"Scrape URL"** to:
1. Discover all available pages
2. Scrape them in parallel
3. Display combined results

#### Custom URL
To scrape a different website:
1. Replace the URL in the input field
2. Keep the checkbox checked for automatic page discovery
3. Click **"Scrape URL"**

#### Single Page Mode
To scrape only the specified page:
1. Uncheck "Automatically discover and scrape all pages"
2. Click **"Scrape URL"**

### 4. View Results

After scraping completes, you'll see:

**Success Message**
```
Successfully scraped 367 items from 8 page(s) in 7.85s!
```

**Data Table**
- Sortable columns (click headers)
- Filter inputs (lot number, title, price range)
- All data from all pages combined

**Statistics**
- Items displayed after filtering
- Total items scraped

## Using the API Directly

### Scrape All Pages
```bash
curl -X POST http://localhost:5001/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1",
    "wait_time": 5,
    "scrape_all_pages": true
  }'
```

### Scrape Single Page
```bash
curl -X POST http://localhost:5001/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1",
    "wait_time": 5,
    "scrape_all_pages": false
  }'
```

## Understanding the Response

### With scrape_all_pages=true
```json
{
  "success": true,
  "data": {
    "structured_data": {
      "type": "regal_auctions",
      "total_pages": 8,
      "total_lots": 367,
      "scraping_time": "7.85s",
      "lots": [
        {
          "page": 1,
          "lot_number": "001",
          "title": "2020 Honda Civic",
          "starting_bid": "$15,000",
          ...
        },
        ...
      ]
    }
  }
}
```

Key fields:
- `total_pages`: Number of pages discovered
- `total_lots`: Total items scraped
- `scraping_time`: How long it took
- `lots[].page`: Which page each item came from

### With scrape_all_pages=false
```json
{
  "success": true,
  "data": {
    "url": "...",
    "title": "...",
    "structured_data": {
      "type": "regal_auctions",
      "total_lots": 48,
      "lots": [...]
    }
  }
}
```

## Testing

### Quick Test
```bash
python test_quick_discovery.py
```

Shows:
- Pages discovered
- Total lots scraped
- Scraping time
- Distribution by page

### Full Test
```bash
python test_page_discovery.py
```

Saves full results to `data/page_discovery_test.json`

## Command Line Scraping

The command-line scraper (`scraper.py`) currently uses hardcoded page ranges:

```bash
python scraper.py
```

**Note**: The command-line version hasn't been updated with page discovery yet. Use the web interface or API for automatic page discovery.

## How It Works Behind the Scenes

### Page Discovery Algorithm

1. **Load First Page**
   ```python
   driver.get(base_url)
   time.sleep(wait_time)
   ```

2. **Parse Pagination**
   - Search for `?page=N` in all links
   - Look for "Page 1 of X" text
   - Analyze pagination navigation

3. **Find Maximum**
   ```python
   max_page = 1
   for each page link:
       if page_num > max_page:
           max_page = page_num
   return max_page
   ```

4. **Parallel Scraping**
   ```python
   with ThreadPoolExecutor(max_workers=10) as executor:
       futures = {executor.submit(scrape_page, i): i 
                  for i in range(1, total_pages + 1)}
   ```

5. **Combine Results**
   ```python
   all_lots = []
   for future in as_completed(futures):
       lots = future.result()
       all_lots.extend(lots)
   ```

## Troubleshooting

### API Not Responding
```bash
# Check if API is running
curl http://localhost:5001/health

# Restart the application
./start_app.sh
```

### Wrong Number of Pages Detected
The page discovery looks for:
- URL parameters: `?page=N`
- Pagination text: "Page 1 of 8"
- Navigation links with page numbers

If your site uses different pagination, you may need to adjust the `discover_total_pages()` function in `api.py`.

### Slow Scraping
Factors affecting speed:
- `wait_time`: Seconds to wait for JavaScript (default 5)
- `max_workers`: Number of parallel threads (default 10)
- Network speed
- Server response time

To adjust:
```json
{
  "url": "...",
  "wait_time": 3,  // Reduce for faster loading sites
  "scrape_all_pages": true
}
```

### Incomplete Results
If some pages fail:
- Check console logs for error messages
- Try reducing `max_workers` to avoid overwhelming the server
- Increase `wait_time` for slow-loading pages

## Tips for Best Results

1. **Default Settings Work Well**: The checkbox is enabled by default for good reason!

2. **Be Patient**: Scraping multiple pages takes time. 8 pages typically completes in 8-10 seconds.

3. **Check the Statistics**: After scraping, verify the number of items matches expectations.

4. **Use Filters**: With all pages scraped, use the filter inputs to find specific items quickly.

5. **Sort by Page**: Click the "Page" column header to see which page each item came from.

## Examples by Use Case

### "I want everything from this auction"
✅ Keep checkbox checked  
✅ Click "Scrape URL"  
✅ Get all pages automatically

### "I only want page 5"
❌ Uncheck the checkbox  
✅ Change URL to `...&page=5`  
✅ Click "Scrape URL"

### "I want to compare two auctions"
1. Scrape first auction (with checkbox checked)
2. Save or export the data
3. Change URL to second auction
4. Scrape again
5. Compare in your preferred tool

### "I want to analyze the data"
After scraping:
1. Data is saved to `data/` folder
2. Use `analyze.py` for interactive analysis
3. Or use `rank_vehicles.py` for scoring
4. Or open CSV in Excel/Google Sheets

## Next Steps

- **Analyze Data**: Use `analyze.py` for interactive queries
- **Rank Vehicles**: Use `rank_vehicles.py` for best deals
- **Export Data**: Files saved in `data/` folder (CSV, JSON, Excel)
- **Automate**: Use the API in your own scripts

## Support

For issues or questions:
1. Check this guide
2. Review `PAGE_DISCOVERY_IMPLEMENTATION.md` for technical details
3. Check console logs for error messages
4. Verify API and web server are running

---

**Enjoy automatic page discovery! No more manual page counting! 🚀**
