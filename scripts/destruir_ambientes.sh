#!/bin/bash
# =====================================================================
# DESTRUICAO DOS AMBIENTES (para o passo 1 da validacao:
# "apresentar ambientes com a estrutura NAO existente")
# Remove conteineres E volumes de dados de Homolog e Prod.
# Uso: ./scripts/destruir_ambientes.sh [homolog|prod|todos]
# =====================================================================
set -e
cd "$(dirname "$0")/.."
ALVO="${1:-todos}"

case "$ALVO" in
  homolog) docker compose -f docker-compose.homolog.yml down -v ;;
  prod)    docker compose -f docker-compose.prod.yml down -v ;;
  todos)
    docker compose -f docker-compose.homolog.yml down -v || true
    docker compose -f docker-compose.prod.yml down -v || true
    ;;
  *) echo "Uso: $0 [homolog|prod|todos]"; exit 1 ;;
esac

echo ">>> Estrutura removida. Conteineres atuais:"
docker ps --format "table {{.Names}}\t{{.Status}}"
