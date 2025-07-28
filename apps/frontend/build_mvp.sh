#!/bin/bash

echo "🚀 Building Trading Practice MVP..."

# Backup original files
echo "📦 Backing up original files..."
cp pubspec.yaml pubspec_original.yaml
cp lib/main.dart lib/main_original.dart

# Switch to MVP configuration
echo "🔄 Switching to MVP configuration..."
cp pubspec_mvp.yaml pubspec.yaml
cp lib/main_mvp.dart lib/main.dart

# Clean and get dependencies
echo "🧹 Cleaning and getting dependencies..."
flutter clean
flutter pub get

# Try to build
echo "🔨 Building MVP..."
flutter build apk --debug

# Check if build succeeded
if [ $? -eq 0 ]; then
    echo "✅ MVP build successful!"
    echo "📱 APK location: build/app/outputs/flutter-apk/app-debug.apk"
else
    echo "❌ MVP build failed!"
    echo "🔄 Restoring original files..."
    cp pubspec_original.yaml pubspec.yaml
    cp lib/main_original.dart lib/main.dart
    flutter pub get
fi

echo "🏁 MVP build process complete!"