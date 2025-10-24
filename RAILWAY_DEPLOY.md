# Quick Deployment to Railway.com

## 🚀 Fast Track (5 minutes)

### 1. Prepare Your Code
```bash
# Make sure all files are saved
git init
git add .
git commit -m "Ready for Railway deployment"
```

### 2. Deploy to Railway

**Option A: From GitHub (Recommended)**
1. Push to GitHub first:
   ```bash
   git remote add origin YOUR_GITHUB_URL
   git push -u origin main
   ```
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Dockerfile and deploys!

**Option B: Railway CLI**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 3. Get Your URL
- Railway provides a URL like: `your-app.railway.app`
- Copy this URL

### 4. Update Frontend
Edit `index.html` around line 470:
```javascript
// Change this:
const response = await fetch('http://localhost:5001/scrape', {

// To this (replace with YOUR Railway URL):
const response = await fetch('https://your-app.railway.app/scrape', {
```

### 5. Redeploy
```bash
git add index.html
git commit -m "Update API URL for production"
git push
```

## ✅ Test Your Deployment

```bash
curl -X POST https://your-app.railway.app/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://bids.regalauctions.com/auctions/1778628/lots?date=2025-10-24&page=1", "scrape_all_pages": true}'
```

## 📊 What Gets Deployed

- ✅ Flask API with Selenium
- ✅ Chrome/Chromium browser
- ✅ React frontend interface
- ✅ Automatic page discovery
- ✅ Multi-threaded scraping

## 💰 Costs

- **Free Tier**: $5 credit/month
- Good for testing and light usage
- Upgrade to Pro ($20/mo) for production

## ⚠️ Important Notes

1. **First request is slow** (30-60s) - cold start
2. **5-minute timeout** on Railway
3. **Memory limits** on free tier
4. Consider reducing threads from 10 to 5 if memory issues

## 🐛 Troubleshooting

**"Out of memory"**: Edit `api.py`, change `max_workers=10` to `max_workers=5`

**"Timeout"**: Edit `index.html`, change `wait_time: 5` to `wait_time: 3`

**"Selenium error"**: Check Railway logs: `railway logs`

## 📚 Full Documentation

See `DEPLOYMENT.md` for complete details.

## 🎉 You're Done!

Visit your Railway URL and start scraping!
