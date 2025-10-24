# Deployment Guide - Railway.com

This guide will help you deploy the Auction Scraper to Railway.com.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your code to GitHub (recommended)
3. **Docker Support**: Railway uses the included Dockerfile

## Deployment Steps

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect Railway to GitHub**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect the Dockerfile

3. **Configure Environment**:
   - Railway will automatically use the Dockerfile
   - No additional environment variables needed
   - Railway will assign a PORT automatically

4. **Deploy**:
   - Railway will build and deploy automatically
   - Wait 5-10 minutes for first deployment
   - Get your public URL from Railway dashboard

### Option 2: Deploy from CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   # or
   brew install railway
   ```

2. **Login**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   railway init
   ```

4. **Deploy**:
   ```bash
   railway up
   ```

5. **Get URL**:
   ```bash
   railway domain
   ```

## Important Notes

### API Configuration
After deployment, you'll need to update the frontend API URL:

1. **Edit `index.html`** line ~470:
   ```javascript
   // Change from:
   const response = await fetch('http://localhost:5001/scrape', {
   
   // To:
   const response = await fetch('https://YOUR-RAILWAY-URL.railway.app/scrape', {
   ```

### Selenium Configuration
The Dockerfile includes Chromium and ChromeDriver. If you need to modify the Chrome options:

1. **Edit `api.py`** - `create_driver()` function is already configured for headless mode
2. Options like `--no-sandbox` and `--disable-dev-shm-usage` are essential for Railway

### Performance Considerations

- **Cold Starts**: First request may be slow (30-60 seconds)
- **Timeout**: Railway has a 5-minute timeout for requests
- **Memory**: Scraping 8 pages should work within Railway's free tier limits
- **Rate Limiting**: Consider implementing request throttling for production

### Costs

- **Free Tier**: $5 credit/month, suitable for testing
- **Pro Plan**: $20/month for production use
- **Resource Usage**: Monitor CPU/memory in Railway dashboard

### Alternative: Split Architecture

For better reliability, consider splitting into two Railway services:

1. **API Service** (api.py with Selenium)
2. **Frontend Service** (static HTML served by nginx)

This allows independent scaling and better resource allocation.

## Troubleshooting

### Selenium Fails
- Check Chrome/ChromeDriver versions match
- Ensure `--headless` flag is set
- Add `--disable-gpu` if needed

### Timeout Errors
- Reduce `wait_time` in scraper
- Implement pagination instead of scraping all at once
- Consider background jobs for large scrapes

### Memory Issues
- Reduce number of parallel threads
- Process pages sequentially instead
- Upgrade to Railway Pro plan

## Testing Deployment

After deployment, test with:
```bash
curl -X POST https://YOUR-RAILWAY-URL.railway.app/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1", "wait_time": 5, "scrape_all_pages": false}'
```

## Monitoring

- **Logs**: `railway logs`
- **Metrics**: Check Railway dashboard for CPU/memory usage
- **Health**: Implement `/health` endpoint for monitoring

## Next Steps

1. Set up custom domain (optional)
2. Add authentication for API (recommended)
3. Implement rate limiting
4. Set up monitoring/alerts
5. Consider CDN for static assets

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: Open issue on GitHub
