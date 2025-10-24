# 🎉 Your Railway Deployment Configuration

## Production URL
**https://scraplot-production.up.railway.app/**

## What's Configured

✅ **`env.production.js`** - Manual production config with your Railway URL
✅ **`generate_env.py`** - Auto-generates config based on environment
✅ **`index.html`** - Reads API URL from environment config
✅ **Railway Domain** - Hardcoded as fallback in generate_env.py

## How It Works

### Local Development
```bash
./start_app.sh
```
- Generates: `window.ENV = { API_URL: 'http://localhost:5001' }`
- Uses: Local API server

### Railway Production
```bash
# When Railway deploys (PORT env variable is set)
python3 generate_env.py
```
- Generates: `window.ENV = { API_URL: 'https://scraplot-production.up.railway.app' }`
- Uses: Production Railway API

## Deployment Steps

1. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Update production Railway URL"
   git push origin main
   ```

2. **Railway auto-deploys** (if connected to GitHub)
   - Builds Docker image
   - Runs `generate_env.py` (creates production config)
   - Starts API and web servers
   - Available at: https://scraplot-production.up.railway.app/

3. **Test your deployment:**
   ```bash
   # Test API
   curl https://scraplot-production.up.railway.app/health
   
   # Test scraping
   curl -X POST https://scraplot-production.up.railway.app/scrape \
     -H "Content-Type: application/json" \
     -d '{"url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1", "scrape_all_pages": false}'
   ```

4. **Open in browser:**
   - https://scraplot-production.up.railway.app/
   - The interface will automatically use the production API URL

## Verification

### Check Current Config
```bash
cat env.js
```

### Test Production Mode Locally
```bash
PORT=8080 python3 generate_env.py
cat env.js
# Should show: https://scraplot-production.up.railway.app
```

### Reset to Development Mode
```bash
python3 generate_env.py
cat env.js
# Should show: http://localhost:5001
```

## Environment Variables on Railway

Railway automatically sets:
- **PORT** - Port number for the application (e.g., 8080)
- **RAILWAY_PUBLIC_DOMAIN** - Your public domain (optional)

Our script detects these and generates the correct config.

## If You Change Railway Domain

If Railway gives you a new domain, update `generate_env.py`:
```python
public_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'your-new-domain.railway.app')
```

Or set it as Railway environment variable:
```bash
# In Railway dashboard, add variable:
RAILWAY_PUBLIC_DOMAIN = your-new-domain.railway.app
```

## Status

✅ Production URL: https://scraplot-production.up.railway.app/
✅ Environment system: Configured
✅ Auto-detection: Working
✅ Local development: Ready
✅ Production deployment: Ready

## Next Steps

1. Push to GitHub (if not already)
2. Railway auto-deploys
3. Visit https://scraplot-production.up.railway.app/
4. Start scraping! 🚀

---

**Your app is ready for production!** 🎉
