# 🌐 Web Scraper Application - React Interface

A modern React-based web interface for scraping and analyzing data from any URL.

## ✨ Features

- **Universal URL Scraping**: Scrape data from any website
- **Beautiful React Interface**: Modern, responsive UI
- **Sortable Table**: Click column headers to sort data
- **Real-time Filtering**: Filter by lot number, title, and price range
- **API Backend**: RESTful API with Flask
- **Multithreaded Scraping**: Fast parallel scraping with 10 threads
- **JavaScript Rendering**: Uses Selenium for dynamic content

## 🚀 Quick Start

### Option 1: Start Everything (Easiest)

```bash
./start_app.sh
```

Then open your browser to: **http://localhost:8000**

### Option 2: Manual Start

**Terminal 1 - Start API:**
```bash
python api.py
```

**Terminal 2 - Start Web Interface:**
```bash
python3 -m http.server 8000
```

Then open: **http://localhost:8000**

## 📋 Usage

1. **Open the Interface**: Navigate to http://localhost:8000 in your browser

2. **Enter URL**: Type or paste any URL in the input field
   - Example: `https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1`

3. **Click "Scrape URL"**: Wait for the data to load (5-10 seconds)

4. **View Results**: Data appears in a sortable, filterable table

5. **Sort Data**: Click any column header to sort

6. **Filter Data**: Use the filter inputs to narrow down results:
   - Filter by Lot Number
   - Filter by Title
   - Filter by Min/Max Price

## 🎨 Interface Features

### Top Section
- **URL Input**: Enter any URL to scrape
- **Scrape Button**: Triggers the scraping process
- **Loading Indicator**: Shows progress while scraping

### Filter Bar
- **Lot Number Filter**: Search by lot number
- **Title Filter**: Search by vehicle title
- **Min Price**: Filter by minimum price
- **Max Price**: Filter by maximum price

### Data Table
- **Sortable Columns**: Click headers to sort ascending/descending
- **Lot #**: Auction lot number
- **Title**: Vehicle or item title
- **Starting Bid**: Starting bid amount
- **Reserve Price**: Reserve price
- **Odometer**: Mileage reading
- **Engine**: Engine specifications
- **Link**: View details button (opens in new tab)

### Statistics Bar
- **Items Displayed**: Number of items after filtering
- **Total Items**: Total items scraped

## 🛠️ Technical Stack

### Frontend
- **React 18**: UI framework
- **Babel Standalone**: JSX transpilation
- **Modern CSS**: Gradient backgrounds, animations
- **Responsive Design**: Mobile-friendly

### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Selenium**: Browser automation
- **BeautifulSoup4**: HTML parsing
- **ThreadPoolExecutor**: Parallel scraping (10 threads)

## 📁 Project Structure

```
scraplot/
├── index.html           # React interface (single-page app)
├── api.py              # Flask API server
├── scraper.py          # Multithreaded scraper
├── start_app.sh        # Startup script
├── run_api_test.sh     # API test script
├── quick_test.py       # Quick API test
├── test_api.py         # Full API test suite
├── rank_vehicles.py    # Vehicle ranking script
├── analyze.py          # Data analysis tool
├── requirements.txt    # Python dependencies
└── data/              # Scraped data storage
    ├── auction_data.csv
    ├── auction_data.json
    └── auction_data.xlsx
```

## 🔧 API Endpoints

### POST /scrape
Scrape a URL and return JSON data

**Request:**
```json
{
  "url": "https://example.com",
  "wait_time": 5
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Page Title",
    "structured_data": {
      "type": "regal_auctions",
      "total_lots": 48,
      "lots": [...]
    }
  }
}
```

### GET /health
Health check endpoint

### GET /
API documentation

## 🎯 Example Use Cases

1. **Auction Scraping**: Monitor auction listings
2. **Price Comparison**: Compare prices across pages
3. **Inventory Tracking**: Track vehicle inventory
4. **Data Analysis**: Export data for analysis

## 💡 Tips

- **Better Results**: Increase `wait_time` for slower sites
- **Multiple Pages**: Scrape multiple pages and combine results
- **Export Data**: Use browser's export feature to save filtered data
- **Mobile Access**: Works on mobile browsers too!

## 🐛 Troubleshooting

**API Not Connecting?**
- Make sure API is running on port 5001
- Check if port 5001 is available: `lsof -i:5001`
- Kill process if needed: `lsof -ti:5001 | xargs kill -9`

**Web Interface Not Loading?**
- Ensure port 8000 is available
- Try a different port: `python3 -m http.server 8080`
- Clear browser cache

**Scraping Fails?**
- Check if URL is accessible
- Increase wait time for slow sites
- Check browser console for errors

## 📊 Performance

- **Single Page Scraping**: ~8 seconds (with 10 threads)
- **Data Processing**: Real-time filtering/sorting
- **Memory Efficient**: Handles 1000+ items smoothly

## 🔒 Security Note

This is a development tool. For production use:
- Add authentication
- Rate limiting
- Input validation
- Use production WSGI server (gunicorn)
- Add HTTPS

## 📝 License

MIT License - Feel free to use and modify!

---

**Made with ❤️ using React, Flask, and Selenium**
