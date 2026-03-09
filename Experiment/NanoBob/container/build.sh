#!/bin/bash
set -e

echo "Building NanoBob agent container..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Build the container image
docker build -t nanobob-agent:latest "$SCRIPT_DIR"

echo "Container built successfully!"
echo "Image: nanobob-agent:latest"
