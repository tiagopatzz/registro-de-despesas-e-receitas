#!/bin/bash
# Remove SOMENTE o ambiente de Producao (containers + volume de dados).
set -e
cd "$(dirname "$0")/.."
docker compose -f docker-compose.prod.yml down -v
echo ">>> Producao removida."
docker ps --format "table {{.Names}}\t{{.Status}}"
