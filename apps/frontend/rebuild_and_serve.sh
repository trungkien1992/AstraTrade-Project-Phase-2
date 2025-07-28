#!/bin/bash

echo "🔧 Rebuilding Flutter Web App..."
cd /Users/admin/AstraTrade-Project/apps/astratrade-frontend

# Clean previous build
flutter clean

# Build for web
flutter build web

# Check if build was successful
if [ -f "build/web/index.html" ]; then
    echo "✅ Build successful, starting server..."
    cd build/web
    echo "🌐 Starting server at http://localhost:9001"
    python3 -m http.server 9001
else
    echo "❌ Build failed - no index.html found"
    exit 1
fi