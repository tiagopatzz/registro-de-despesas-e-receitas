#!/bin/bash
# Cria do ZERO o ambiente de PRODUCAO (NGINX + app + banco).
set -e
cd "$(dirname "$0")/.."
echo ">>> [1/2] Construindo imagem da aplicacao (baixa base se preciso)..."
docker compose build --pull app-prod
echo ">>> [2/2] Subindo Producao (NGINX + app + banco)..."
docker compose up -d nginx app-prod db-prod
echo ""
echo ">>> PRODUCAO no ar: http://localhost/prod/"
docker ps --format "table {{.Names}}\t{{.Status}}"
