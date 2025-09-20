#!/bin/bash

# Build script for SEM Planning Engine
echo "🚀 Building SEM Planning Engine..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies and build frontend
echo "🎨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

echo "✅ Build complete!"
echo "🌐 Ready for deployment!"
