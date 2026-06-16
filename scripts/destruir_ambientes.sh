#!/bin/bash
# =====================================================================
# DESTRUICAO TOTAL DOS AMBIENTES
# Remove TUDO do projeto: containers (inclusive orfaos antigos),
# volumes de dados, rede E imagens. Apos rodar, nem "docker ps" nem
# "docker images" mostram nada do projeto - tela limpa para o professor.
#
# NAO toca em imagens/volumes de OUTROS projetos da VM.
# Uso: ./scripts/destruir_ambientes.sh
# =====================================================================
set -e
cd "$(dirname "$0")/.."

echo ">>> [1/4] Derrubando ambientes (containers + volumes + rede)..."
docker compose down -v --remove-orphans 2>/dev/null || true

echo ">>> [2/4] Removendo containers orfaos antigos do projeto (se houver)..."
# Versao antiga do projeto (web_financas / registro-de-despesas-e-receitas-web)
for c in $(docker ps -a --filter "name=financas" --format "{{.ID}}") \
         $(docker ps -a --filter "name=web_financas" --format "{{.ID}}"); do
    docker rm -f "$c" 2>/dev/null || true
done

echo ">>> [3/4] Removendo imagens do projeto..."
# Imagens proprias (build) + bases que o projeto usa
for img in financas-app:homolog \
           financas-app:prod \
           registro-de-despesas-e-receitas-web:latest \
           nginx:1.27-alpine \
           python:3.12-slim \
           postgres:16-alpine; do
    docker rmi -f "$img" 2>/dev/null && echo "    removida: $img" || true
done

echo ">>> [4/4] Limpando cache de build do projeto..."
docker builder prune -f >/dev/null 2>&1 || true

echo ""
echo "============================================"
echo " AMBIENTE ZERADO"
echo "============================================"
echo ">>> docker ps (deve estar vazio):"
docker ps
echo ""
echo ">>> Imagens do projeto restantes (deve estar vazio):"
docker images | grep -E "financas|registro-de-despesas|nginx.*1.27|postgres.*16-alpine" || echo "    (nenhuma - limpo!)"
