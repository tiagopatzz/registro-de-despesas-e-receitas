#!/bin/bash
# Sobe TUDO de uma vez: NGINX + Homolog + Prod.
set -e
cd "$(dirname "$0")/.."
docker compose up -d --build
echo ">>> HOMOLOG:  http://localhost/homolog/"
echo ">>> PRODUCAO: http://localhost/prod/"
docker ps --format "table {{.Names}}\t{{.Status}}"
