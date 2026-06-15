#!/bin/bash
# Remove TUDO: containers, volumes de dados, rede e NGINX.
# Apos rodar, "docker ps" fica VAZIO (nada rodando) - como o professor pediu.
set -e
cd "$(dirname "$0")/.."
docker compose down -v
echo ">>> Tudo removido. 'docker ps' deve estar vazio:"
docker ps
