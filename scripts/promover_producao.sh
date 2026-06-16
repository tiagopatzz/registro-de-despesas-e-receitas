#!/bin/bash
# =====================================================================
# PROMOCAO CONTROLADA PARA PRODUCAO
#
# O portao de qualidade (flake8 + 20 testes) roda no GITHUB ACTIONS.
# Este script faz a PROMOCAO da versao ja validada em Homologacao
# para Producao, sob seu controle (confirmacao manual).
#
# Pre-requisito: a branch 'homolog' precisa ter passado no Actions
# (commit verde). Se o ultimo commit da homolog falhou no Actions,
# NAO promova - corrija antes.
#
# Uso: ./scripts/promover_producao.sh
# =====================================================================
set -e
cd "$(dirname "$0")/.."

echo "============================================"
echo " PROMOCAO: Homologacao  ->  Producao"
echo "============================================"
echo ""
echo " Antes de continuar, confirme no GitHub Actions que o ultimo"
echo " commit da branch 'homolog' esta VERDE (Integracao aprovada)."
echo ""
echo " Ao promover:"
echo "   - merge da branch 'homolog' na 'main'"
echo "   - push na 'main' -> dispara o Actions -> deploy em Producao"
echo ""
read -p " Digite 'PROMOVER' para confirmar, ou ENTER para cancelar: " resposta

if [ "$resposta" != "PROMOVER" ]; then
    echo ">>> Promocao cancelada. Producao permanece inalterada."
    exit 0
fi

echo ""
echo ">>> Promovendo homolog -> main..."
git checkout main
git pull origin main
git merge homolog --no-edit
git push origin main
git checkout homolog

echo ""
echo "============================================"
echo " Push na 'main' realizado."
echo " O GitHub Actions vai rodar a Integracao e, passando,"
echo " atualizar o ambiente de PRODUCAO automaticamente."
echo " Acompanhe em: GitHub -> Actions"
echo "============================================"
