#!/bin/bash

# Exit on error
set -e

echo "🚀 Installing DexScreener MCP Server..."

# Install dependencies and build
echo "🔧 Installing dependencies..."
npm install

echo "🛠️ Building project..."
npm run build

# Run setup script
echo "⚙️ Configuring Claude Desktop..."
npm run setup

echo "✅ Installation complete! Please restart Claude Desktop to activate the server."
