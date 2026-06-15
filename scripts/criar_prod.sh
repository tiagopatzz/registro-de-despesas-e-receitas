#!/bin/bash
# Sobe NGINX + Producao (app + banco). Aplica migrations automaticamente.
set -e
cd "$(dirname "$0")/.."
docker compose up -d --build nginx app-prod db-prod
echo ">>> PRODUCAO no ar: http://localhost/prod/"
docker ps --format "table {{.Names}}\t{{.Status}}"
