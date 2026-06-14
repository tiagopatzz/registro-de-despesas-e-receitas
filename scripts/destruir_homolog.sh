#!/bin/bash
# Remove SOMENTE o ambiente de Homologacao (containers + volume de dados).
set -e
cd "$(dirname "$0")/.."
docker compose -f docker-compose.homolog.yml down -v
echo ">>> Homolog removido."
docker ps --format "table {{.Names}}\t{{.Status}}"
