#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose -f infra/docker-compose.yml up -d
echo "Waiting for services..."
sleep 10
echo "Services started."


