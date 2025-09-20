#!/bin/bash

echo "🚀 SEM Planning Engine - Quick Deploy Script"
echo "=============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy SEM Planning Engine - $(date)"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "🔗 Git remote not configured."
    echo "Please create a GitHub repository and run:"
    echo "git remote add origin https://github.com/yourusername/sem-planner.git"
    echo "git push -u origin main"
    echo ""
    echo "Then deploy on Railway:"
    echo "1. Go to https://railway.app"
    echo "2. Click 'Deploy from GitHub'"
    echo "3. Select your repository"
    echo "4. Add environment variables:"
    echo "   GROQ_API_KEY=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"
    echo "   GOOGLE_ADS_CUSTOMER_ID=7891406099"
    echo ""
else
    echo "🚀 Pushing to GitHub..."
    git push origin main
    echo ""
    echo "✅ Code pushed to GitHub!"
    echo ""
    echo "🌐 Next steps:"
    echo "1. Go to https://railway.app"
    echo "2. Click 'Deploy from GitHub'"
    echo "3. Select your repository"
    echo "4. Add environment variables in Railway dashboard"
    echo "5. Get your live URL!"
fi

echo ""
echo "🎉 Your SEM Planning Engine is ready for deployment!"
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
