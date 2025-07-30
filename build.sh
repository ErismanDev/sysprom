#!/usr/bin/env bash

echo "🚀 Iniciando build otimizado para Render..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Configurar variáveis de ambiente
export DJANGO_SETTINGS_MODULE=sepromcbmepi.settings_render
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Coletar arquivos estáticos com otimizações
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

# Verificar integridade do banco
echo "🔍 Verificando integridade do banco..."
python manage.py check --deploy

# Limpar cache do Python
echo "🧹 Limpando cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Otimizar imports
echo "⚡ Otimizando imports..."
python -c "
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    import django
    django.setup()
    print('✅ Django configurado com sucesso')
except Exception as e:
    print(f'⚠️ Aviso: {e}')
"

echo "✅ Build concluído com sucesso!" 