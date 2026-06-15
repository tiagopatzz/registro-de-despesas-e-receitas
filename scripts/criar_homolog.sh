#!/bin/bash
# Sobe NGINX + Homologacao (app + banco). Aplica migrations automaticamente.
set -e
cd "$(dirname "$0")/.."
docker compose up -d --build nginx app-homolog db-homolog
echo ">>> HOMOLOG no ar: http://localhost/homolog/"
docker ps --format "table {{.Names}}\t{{.Status}}"
