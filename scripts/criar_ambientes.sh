#!/bin/bash
# =====================================================================
# CRIACAO AUTOMATIZADA DA INFRAESTRUTURA
# Uso: ./scripts/criar_ambientes.sh [homolog|prod|todos]
#
# Cria (do zero) os conteineres, instala as ferramentas dentro deles,
# aplica as migrations e deixa a aplicacao no ar:
#   - NGINX (proxy reverso)
#   - Homolog: app-homolog + db-homolog (volume vol_hml)
#   - Prod:    app-prod    + db-prod    (volume vol_prod)
# =====================================================================
set -e
cd "$(dirname "$0")/.."
ALVO="${1:-todos}"

docker network inspect gcs_net >/dev/null 2>&1 || docker network create gcs_net
docker compose -f docker-compose.infra.yml up -d

case "$ALVO" in
  homolog)
    docker compose -f docker-compose.homolog.yml up -d --build
    echo ">>> HOMOLOG no ar: http://localhost/homolog/"
    ;;
  prod)
    docker compose -f docker-compose.prod.yml up -d --build
    echo ">>> PRODUCAO no ar: http://localhost/prod/"
    ;;
  todos)
    docker compose -f docker-compose.homolog.yml up -d --build
    docker compose -f docker-compose.prod.yml up -d --build
    echo ">>> HOMOLOG:  http://localhost/homolog/"
    echo ">>> PRODUCAO: http://localhost/prod/"
    ;;
  *)
    echo "Uso: $0 [homolog|prod|todos]"; exit 1 ;;
esac

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
