# Page Discovery Fix - October 23, 2025

## Problem
The page discovery was only finding 2 pages instead of the expected 8 pages for the Regal Auctions URL.

## Root Cause
The original page discovery strategy prioritized looking for `?page=` URL parameters in links, which only found pages 1 and 2 on the initial load. The website uses a `<select>` dropdown and "of X" text pattern to indicate the total number of pages.

## Solution
Improved the `discover_total_pages()` function in `api.py` with 5 detection strategies in order of reliability:

### Strategy 1: "of X" Text Pattern (Most Reliable)
Searches for patterns like "of 8", "of 10", etc. in the page text content.
```python
of_pattern = re.search(r'of\s+(\d+)', text_content, re.IGNORECASE)
```

### Strategy 2: Page Select Dropdowns
Looks for `<select>` elements containing page numbers in `<option>` tags.
```python
select_elements = soup.find_all('select')
for select in select_elements:
    options = select.find_all('option')
```

### Strategy 3: "Page X of Y" Text
Searches for explicit "Page 1 of 8" style text.
```python
page_of_pattern = re.search(r'Page\s+\d+\s+of\s+(\d+)', text_content, re.IGNORECASE)
```

### Strategy 4: URL Parameters
Looks for `?page=N` or `&page=N` in link hrefs (original approach).
```python
match = re.search(r'[?&]page=(\d+)', href)
```

### Strategy 5: Pagination Navigation
Examines pagination nav elements for page numbers.
```python
pagination = soup.find('nav', {'class': re.compile('pagination', re.IGNORECASE)})
```

## Results
✅ **Successfully detecting all 8 pages with 367 total lots**
- Previous: Found 2 pages, 96 lots
- Fixed: Found 8 pages, 367 lots
- Scraping time: ~10-11 seconds (with 10 parallel threads)

## Key HTML Structure Found
```html
<select class="form-select form-select-sm">
  <option>1</option>
  <option>2</option>
  <option>3</option>
  <option>4</option>
  <option>5</option>
  <option>6</option>
  <option>7</option>
  <option>8</option>
</select>
<div style="white-space: nowrap;"> of 8</div>
```

Also found:
```html
<div>
  <small class="text-body-secondary fw-light">LOTS</small><br>
  <strong class="fs-4">367</strong>
</div>
```

## Testing
Test command:
```bash
curl -s -X POST http://localhost:5001/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1", "wait_time": 8, "scrape_all_pages": true}' \
  | python -c "import sys, json; d=json.load(sys.stdin); print(f\"total_pages: {d['data'].get('total_pages')}\"); print(f\"total_lots: {d['data'].get('total_lots')}\"); print(f\"scraping_time: {d['data'].get('scraping_time')}\")"
```

Output:
```
total_pages: 8
total_lots: 367
scraping_time: 10.77s
```

## Files Modified
1. **api.py** - Updated `discover_total_pages()` function with improved detection strategies
2. **test_quick_discovery.py** - Fixed response data access (removed 'structured_data' nesting)

## Impact
- **Accuracy**: 100% page detection (8/8 pages found)
- **Robustness**: Multiple fallback strategies ensure compatibility with various pagination patterns
- **Performance**: Maintained ~10 second scraping time for 8 pages with parallel execution
- **Completeness**: All 367 lots captured instead of only 96
