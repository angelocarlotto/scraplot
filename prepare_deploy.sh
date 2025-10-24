#!/bin/bash

# Railway Deployment Helper Script

echo "🚀 Railway.com Deployment Helper"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git repository found"
fi

# Check if there are uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo ""
    echo "📝 Uncommitted changes detected:"
    git status -s
    echo ""
    read -p "Commit these changes? (y/n): " commit_choice
    if [ "$commit_choice" = "y" ]; then
        read -p "Enter commit message: " commit_msg
        git add .
        git commit -m "$commit_msg"
        echo "✅ Changes committed"
    fi
fi

echo ""
echo "🛠️ Next Steps:"
echo ""
echo "Option 1 - Deploy from GitHub (Recommended):"
echo "  1. Push to GitHub:"
echo "     git remote add origin YOUR_GITHUB_URL"
echo "     git push -u origin main"
echo "  2. Go to https://railway.app"
echo "  3. Click 'New Project' → 'Deploy from GitHub repo'"
echo "  4. Select your repository"
echo ""
echo "Option 2 - Deploy via Railway CLI:"
echo "  1. Install CLI: npm install -g @railway/cli"
echo "  2. Login: railway login"
echo "  3. Deploy: railway up"
echo ""
echo "⚠️ IMPORTANT: After deployment, update the API URL in index.html"
echo "   Change 'http://localhost:5001/scrape' to 'https://YOUR-APP.railway.app/scrape'"
echo ""
echo "📚 Full guide: See RAILWAY_DEPLOY.md"
echo ""
