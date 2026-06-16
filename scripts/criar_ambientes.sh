#!/bin/bash
# Cria do ZERO TODA a infraestrutura: NGINX + Homolog + Prod.
set -e
cd "$(dirname "$0")/.."
echo ">>> [1/2] Construindo imagens da aplicacao (baixa base se preciso)..."
docker compose build --pull
echo ">>> [2/2] Subindo tudo (NGINX + Homolog + Prod)..."
docker compose up -d
echo ""
echo ">>> HOMOLOG:  http://localhost/homolog/"
echo ">>> PRODUCAO: http://localhost/prod/"
docker ps --format "table {{.Names}}\t{{.Status}}"
