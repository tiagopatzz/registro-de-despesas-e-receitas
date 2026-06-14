#!/bin/sh
# Sobe o ambiente: 1) aplica migrations pendentes  2) inicia a aplicacao
set -e
echo ">>> Aplicando migrations do banco de dados..."
python migrate.py
echo ">>> Iniciando aplicacao (gunicorn)..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
