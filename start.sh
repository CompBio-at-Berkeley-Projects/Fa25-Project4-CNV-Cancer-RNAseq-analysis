#!/bin/bash
# CopyKAT Analysis Pipeline - Quick Start Script
# This script builds and starts the Docker containers

set -e

echo "=============================================="
echo "  CopyKAT CNV Analysis Pipeline"
echo "  Docker Quick Start"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed."
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running."
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is installed and running"
echo ""

# Check for docker compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "ERROR: Docker Compose is not available."
    echo "Please install Docker Desktop which includes Docker Compose."
    exit 1
fi

echo "✓ Docker Compose is available"
echo ""

# Build and start
echo "Building and starting containers..."
echo "This may take 15-30 minutes on first run."
echo ""

$COMPOSE_CMD up --build -d

echo ""
echo "=============================================="
echo "  Startup Complete!"
echo "=============================================="
echo ""
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000/api"
echo ""
echo "  To view logs:    docker compose logs -f"
echo "  To stop:         docker compose down"
echo ""
echo "  For help, see DOCKER_DEPLOYMENT.md"
echo "=============================================="

