# Environment Configuration Guide

## Overview

The application now uses environment variables to configure the API URL, making it easy to switch between local development and production without changing code.

## How It Works

### 1. Configuration Files

- **`generate_env.py`** - Python script that generates the environment config
- **`env.js`** - Auto-generated JavaScript config (created by generate_env.py)
- **`index.html`** - Frontend loads env.js to get API_URL

### 2. Environment Detection

The `generate_env.py` script automatically detects:
- **Local Development**: No PORT env variable → uses `http://localhost:5001`
- **Production (Railway)**: PORT env variable exists → uses Railway's public domain

### 3. Frontend Usage

In `index.html`, the React app reads the config:
```javascript
const API_URL = window.ENV?.API_URL || 'http://localhost:5001';
```

Then uses it for API calls:
```javascript
fetch(`${API_URL}/scrape`, {...})
```

## Local Development

### Automatic (Recommended)
Just run the start script - it generates the config automatically:
```bash
./start_app.sh
```

### Manual
If you need to regenerate the config:
```bash
python3 generate_env.py
```

This creates `env.js` with:
```javascript
window.ENV = {
    API_URL: 'http://localhost:5001'
};
```

## Production Deployment

### Railway.com

**No configuration needed!** Railway automatically:
1. Sets the `PORT` environment variable
2. Runs `generate_env.py` during startup (via Dockerfile)
3. Generates `env.js` with the correct production URL
4. Uses the Railway public domain for API calls

The Dockerfile handles everything:
```dockerfile
# In start script:
python3 generate_env.py  # Generates production config
python api.py &          # Starts API
python -m http.server    # Starts web server
```

### Manual Production Setup

If deploying elsewhere, set the `RAILWAY_PUBLIC_DOMAIN` variable:
```bash
export RAILWAY_PUBLIC_DOMAIN="your-domain.com"
python3 generate_env.py
```

## Environment Variables

### Development
- **PORT** - Not set (API runs on 5001, web on 8000)

### Production (Railway)
- **PORT** - Set by Railway (e.g., 8080)
- **RAILWAY_PUBLIC_DOMAIN** - Optional: Your public domain

## Troubleshooting

### "Failed to connect to API"
1. Check if `env.js` exists:
   ```bash
   cat env.js
   ```

2. Regenerate it:
   ```bash
   python3 generate_env.py
   ```

3. Check the API_URL in browser console:
   ```javascript
   console.log(window.ENV)
   ```

### Wrong API URL
1. Check environment:
   ```bash
   echo $PORT
   echo $RAILWAY_PUBLIC_DOMAIN
   ```

2. Regenerate config:
   ```bash
   python3 generate_env.py
   ```

3. Restart servers

### API and Web on Different Domains

If you deploy API and frontend separately:

1. **Edit `generate_env.py`**:
   ```python
   api_url = 'https://your-api-domain.com'
   ```

2. **Regenerate**:
   ```bash
   python3 generate_env.py
   ```

3. **Enable CORS** in `api.py` (already configured)

## Advanced: Custom Configuration

### Option 1: Environment Variable
Set a custom API URL:
```bash
export CUSTOM_API_URL="https://custom-api.com"
```

Then modify `generate_env.py`:
```python
api_url = os.environ.get('CUSTOM_API_URL', 'http://localhost:5001')
```

### Option 2: Manual env.js
Create `env.js` manually:
```javascript
window.ENV = {
    API_URL: 'https://your-custom-api.com'
};
```

### Option 3: Multiple Environments
Create different config files:
- `env.dev.js` - Development
- `env.staging.js` - Staging
- `env.prod.js` - Production

Then modify `index.html` to load the appropriate file.

## Summary

✅ **Local Development**: Run `./start_app.sh` - config auto-generated
✅ **Railway Deployment**: Zero config - works automatically
✅ **Custom Deployment**: Set environment variables or edit generate_env.py

No more hardcoded URLs! 🎉
