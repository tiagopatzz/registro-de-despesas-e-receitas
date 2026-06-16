#!/bin/bash
# =====================================================================
# DESTRUICAO TOTAL DOS AMBIENTES
# Remove TUDO do projeto: containers, volumes, rede E imagens.
# Apos rodar, "docker ps" e "docker images" ficam sem nada do projeto.
# NAO toca em imagens/volumes de OUTROS projetos (jupyter, postgres:15, etc).
# =====================================================================
cd "$(dirname "$0")/.."

echo ">>> [1/4] Derrubando ambientes (containers + volumes + rede)..."
docker compose down -v --remove-orphans 2>/dev/null || true

echo ">>> [2/4] Removendo containers do projeto (inclusive orfaos antigos)..."
docker ps -a --filter "name=financas" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=web_financas" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true

echo ">>> [3/4] Removendo imagens do projeto..."
# Imagens proprias do build (financas-app) - sempre seguras de remover
docker images "financas-app" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi -f 2>/dev/null || true
docker images "registro-de-despesas-e-receitas-web" --format "{{.Repository}}:{{.Tag}}" | xargs -r docker rmi -f 2>/dev/null || true
# Bases que o projeto usa (so as versoes exatas; nao mexe em postgres:15 etc.)
for img in nginx:1.27-alpine postgres:16-alpine python:3.12-slim; do
    if docker image inspect "$img" >/dev/null 2>&1; then
        if docker rmi "$img" >/dev/null 2>&1; then
            echo "    removida: $img"
        else
            echo "    AVISO: $img esta em uso por outro projeto - mantida"
        fi
    fi
done

echo ">>> [4/4] Limpando cache de build do projeto..."
docker builder prune -f >/dev/null 2>&1 || true

echo ""
echo "============================================"
echo " VERIFICACAO FINAL"
echo "============================================"
echo ">>> docker ps:"
docker ps
echo ""
echo ">>> Imagens do projeto que ainda restam (ideal: nenhuma):"
if docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "^financas-app|registro-de-despesas|^nginx:1.27-alpine|^postgres:16-alpine"; then
    echo "    ^ ainda ha imagens acima. Se estiverem 'em uso', algum container nao foi removido."
else
    echo "    (nenhuma - tudo limpo!)"
fi
