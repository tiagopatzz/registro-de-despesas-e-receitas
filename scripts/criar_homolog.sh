#!/bin/bash
# Cria do ZERO o ambiente de HOMOLOGACAO (NGINX + app + banco).
# 1) build --pull: reconstroi a imagem da app baixando a base python:3.12-slim
# 2) up: sobe os conteineres, baixando nginx/postgres se necessario
# Migrations aplicam sozinhas na subida do app.
set -e
cd "$(dirname "$0")/.."
echo ">>> [1/2] Construindo imagem da aplicacao (baixa base se preciso)..."
docker compose build --pull app-homolog
echo ">>> [2/2] Subindo Homologacao (NGINX + app + banco)..."
docker compose up -d nginx app-homolog db-homolog
echo ""
echo ">>> HOMOLOG no ar: http://localhost/homolog/"
docker ps --format "table {{.Names}}\t{{.Status}}"
