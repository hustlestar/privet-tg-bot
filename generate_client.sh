#!/bin/bash

# Script to generate TypeScript client for React from FastAPI OpenAPI spec

set -e

echo "🎯 Generating TypeScript Client for React"
echo "========================================"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js and npm."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ] || [ ! -f "node_modules/@openapitools/openapi-generator-cli/package.json" ]; then
    echo "📦 Installing OpenAPI Generator CLI..."
    npm install --no-save @openapitools/openapi-generator-cli
fi

# Run the Python script
echo "🚀 Running client generator..."
python3 generate_api_client.py

echo ""
echo "✅ Done! Check the generated-client folder for your TypeScript client."