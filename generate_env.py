#!/usr/bin/env python3
"""
Generate environment configuration for the frontend
"""
import os
import sys

def generate_env_config():
    # Check if we're in production (Railway sets PORT env variable)
    is_production = 'PORT' in os.environ
    
    if is_production:
        # In production, use Railway's public domain
        port = os.environ.get('PORT', '8080')
        # Railway provides RAILWAY_PUBLIC_DOMAIN or use hardcoded URL
        public_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'scraplot-production.up.railway.app')
        
        if public_domain:
            api_url = f'https://{public_domain}'
        else:
            # Fallback: use known Railway URL
            api_url = 'https://scraplot-production.up.railway.app'
        
        print(f"Production mode: API_URL = {api_url}")
    else:
        # Local development
        api_url = 'http://localhost:5001'
        print(f"Development mode: API_URL = {api_url}")
    
    # Generate the JavaScript config file
    config_content = f"""// Auto-generated environment configuration
// Generated at build time - do not edit manually
window.ENV = {{
    API_URL: '{api_url}'
}};
"""
    
    # Write to env.js
    with open('env.js', 'w') as f:
        f.write(config_content)
    
    print("✅ Environment configuration written to env.js")

if __name__ == '__main__':
    generate_env_config()
