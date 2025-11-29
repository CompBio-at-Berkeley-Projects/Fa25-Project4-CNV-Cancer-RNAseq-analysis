#!/bin/bash
# CopyKAT Analysis Pipeline - Stop Script
# This script stops the Docker containers

set -e

echo "Stopping CopyKAT containers..."

# Check for docker compose
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
else
    echo "ERROR: Docker Compose is not available."
    exit 1
fi

$COMPOSE_CMD down

echo ""
echo "✓ Containers stopped successfully"
echo ""
echo "Note: Your results data is preserved in Docker volumes."
echo "To remove all data: docker compose down -v"

