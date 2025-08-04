#!/usr/bin/env bash
# Script de build para deploy automático

echo "🚀 Iniciando build do SEPROM CBMEPI..."

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar migrações
python manage.py migrate

echo "✅ Build concluído com sucesso!" 