#!/bin/bash

echo "🚀 Deploying SkillBridge Backend..."

# Step 1: Commit changes
echo "📦 Committing backend changes..."
git add .
git commit -m "Deploy backend: $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"

# Step 2: Push to GitHub
echo "📡 Pushing backend to GitHub..."
git push origin main

# Step 3: Trigger Render deployment (if you have webhook URL)
echo "📡 Triggering Render deployment..."
# Replace with your actual Render webhook URL
# curl -X POST https://api.render.com/deploy/srv-xxxxxxxxxx

echo ""
echo "✅ Backend deployment complete!"
echo "📋 Next steps:"
echo "1. Go to https://render.com"
echo "2. Find your web service"
echo "3. Click 'Manual Deploy' → 'Deploy latest commit'"
