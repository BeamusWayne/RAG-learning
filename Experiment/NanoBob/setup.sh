#!/bin/bash
set -e

echo "NanoBob Setup"
echo "==============="

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d. -f1 | tr -d v)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "Error: Node.js 20+ is required"
    exit 1
fi

echo "Node.js version: $(node -v)"

# Install dependencies
echo "Installing dependencies..."
npm install

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# Build TypeScript
echo "Building TypeScript..."
npm run build

# Create directories
echo "Creating directories..."
mkdir -p groups/global groups/qwen_main/logs
mkdir -p store data/sessions data/env data/ipc/{messages,tasks,input} logs

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and set your DASHSCOPE_API_KEY"
echo "2. Build the container: ./container/build.sh"
echo "3. Run NanoBob: npm start"
