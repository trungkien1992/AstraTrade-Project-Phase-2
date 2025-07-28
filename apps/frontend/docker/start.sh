#!/bin/sh

# 🚀 AstraTrade Docker Startup Script
# Handles graceful startup and configuration

echo "🚀 Starting AstraTrade Flutter Web App..."

# Create necessary directories
mkdir -p /var/cache/nginx
mkdir -p /var/log/nginx

# Set proper permissions
chown -R nginx:nginx /var/cache/nginx /var/log/nginx

# Print environment information
echo "📊 Environment Information:"
echo "   Nginx version: $(nginx -v 2>&1)"
echo "   User: $(whoami)"
echo "   Working directory: $(pwd)"
echo "   Available files: $(ls -la /usr/share/nginx/html | wc -l) files"

# Test nginx configuration
echo "🔧 Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration has errors"
    exit 1
fi

# Start nginx in foreground
echo "🌐 Starting nginx server..."
exec nginx -g "daemon off;"