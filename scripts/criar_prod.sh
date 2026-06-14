#!/bin/bash
# Cria/sobe SOMENTE o ambiente de PRODUCAO (e o NGINX, se ainda nao estiver no ar).
set -e
cd "$(dirname "$0")/.."
docker network inspect gcs_net >/dev/null 2>&1 || docker network create gcs_net
docker compose -f docker-compose.infra.yml up -d
docker compose -f docker-compose.prod.yml up -d --build
echo ">>> PRODUCAO no ar: http://localhost/prod/"
docker ps --format "table {{.Names}}\t{{.Status}}"
