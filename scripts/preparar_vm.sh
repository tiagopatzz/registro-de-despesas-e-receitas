#!/bin/bash
# PREPARACAO DA VM (executar UMA vez na vida da VM).
# Instala Docker. NAO deixa nada rodando.
set -e
if ! command -v docker &> /dev/null; then
    echo ">>> Instalando Docker..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
    echo ">>> Docker instalado. Faca logout/login para usar sem sudo."
else
    echo ">>> Docker ja instalado."
fi
echo ">>> VM pronta. Proximo passo: instalar o runner self-hosted do GitHub."
