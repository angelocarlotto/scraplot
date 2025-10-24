# Railway Deployment Fix

## Problem Identified

Railway only exposes **ONE PORT** per service. Our previous setup had:
- API server on internal port 5001 (not accessible)
- Web server on $PORT (accessible)

This caused the error: "Failed to connect to API"

## Solution

Merge both servers into one Flask application that:
1. Serves the web interface (HTML, CSS, JS)
2. Handles API requests (/scrape, /health, etc.)
3. Runs on a single port ($PORT)

## Changes Made

### 1. Updated `api.py`
Added static file serving:
```python
from flask import send_from_directory

# Serve main HTML
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Serve all static files (CSS, JS, etc.)
@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory('.', path)
    return jsonify({'error': 'File not found'}), 404

# API docs moved to /api
@app.route('/api', methods=['GET'])
def api_docs():
    ...
```

### 2. Updated `Dockerfile`
Simplified to run only Flask:
```dockerfile
# Old (TWO servers - doesn't work on Railway)
python api.py &
python -m http.server ${PORT} &

# New (ONE server - works on Railway)
python api.py  # Serves both API and static files
```

### 3. Environment Configuration
No changes needed - still auto-detects:
- Local: `http://localhost:5001`
- Production: `https://scraplot-production.up.railway.app`

## Testing

### Local Development
The local setup still uses two separate servers (for development convenience):
```bash
./start_app.sh
# API: http://localhost:5001
# Web: http://localhost:8000
```

### Production (Railway)
Single Flask server handles everything:
```bash
# Deploy to Railway
git add .
git commit -m "Fix Railway deployment - single port"
git push origin main
```

### Verify Deployment
```bash
# Test health endpoint
curl https://scraplot-production.up.railway.app/health

# Test API docs
curl https://scraplot-production.up.railway.app/api

# Test web interface
curl https://scraplot-production.up.railway.app/ | head -10

# Test scraping
curl -X POST https://scraplot-production.up.railway.app/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1", "scrape_all_pages": false}'
```

## Deployment Checklist

- [x] API serves static files
- [x] Dockerfile uses single server
- [x] Routes configured correctly
- [x] Environment config works
- [ ] Push to GitHub
- [ ] Railway redeploys automatically
- [ ] Test production URL

## Next Steps

1. **Commit changes:**
   ```bash
   git add api.py Dockerfile
   git commit -m "Fix: Single-port deployment for Railway"
   git push origin main
   ```

2. **Wait for Railway to redeploy** (2-5 minutes)

3. **Test the deployment:**
   - Open: https://scraplot-production.up.railway.app/
   - Should see the web interface
   - Try scraping - should work!

4. **If still having issues:**
   - Check Railway logs
   - Verify PORT environment variable is set
   - Ensure Dockerfile builds successfully

## Why This Works

Railway assigns a single public port (via $PORT env variable):
- External requests → Railway proxy → Your app on $PORT
- Flask handles ALL routes:
  - `/` → index.html
  - `/scrape` → API endpoint
  - `/health` → Health check
  - `/env.js` → Environment config
  - etc.

Everything runs on one port, so everything is accessible! ✅
