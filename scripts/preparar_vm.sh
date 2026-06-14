#!/bin/bash
# =====================================================================
# PREPARACAO DA VM DA UNIVATES (executar UMA vez)
# Instala Docker + Docker Compose e cria a rede compartilhada.
# Depois disso, instale o runner self-hosted (ver ARQUITETURA.md).
# =====================================================================
set -e

if ! command -v docker &> /dev/null; then
    echo ">>> Instalando Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo ">>> Docker instalado. Faca logout/login para usar sem sudo."
else
    echo ">>> Docker ja instalado."
fi

docker network inspect gcs_net >/dev/null 2>&1 || docker network create gcs_net
echo ">>> Rede 'gcs_net' pronta."
echo ">>> VM preparada. Proximo passo: instalar o runner self-hosted do GitHub."
