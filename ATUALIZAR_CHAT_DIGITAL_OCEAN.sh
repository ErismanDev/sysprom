#!/bin/bash

# Script para atualizar arquivos JavaScript do chat no servidor Digital Ocean
# Execute este script no servidor após fazer upload dos arquivos atualizados

echo "=========================================="
echo "🔄 ATUALIZANDO ARQUIVOS DO CHAT"
echo "=========================================="
echo ""

# Caminho do projeto
PROJECT_DIR="/home/seprom/sepromcbmepi"

# Verificar se está no diretório correto
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Erro: Diretório do projeto não encontrado: $PROJECT_DIR"
    echo "   Execute: cd /home/seprom/sepromcbmepi"
    exit 1
fi

cd "$PROJECT_DIR"

echo "📁 Diretório atual: $(pwd)"
echo ""

# Verificar se os arquivos existem
echo "🔍 Verificando arquivos..."
FILES=(
    "static/js/chat-widget-ios.js"
    "static/js/chat-tempo-real.js"
    "static/js/chat-calls.js"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file existe"
    else
        echo "⚠️  $file não encontrado (será criado)"
    fi
done

echo ""
echo "=========================================="
echo "📤 INSTRUÇÕES PARA ATUALIZAR OS ARQUIVOS"
echo "=========================================="
echo ""
echo "Opção 1: Usar WinSCP/SCP para fazer upload"
echo "------------------------------------------"
echo "1. Conecte-se ao servidor via WinSCP ou SCP"
echo "2. Navegue até: /home/seprom/sepromcbmepi/static/js/"
echo "3. Faça upload dos seguintes arquivos:"
echo "   - chat-widget-ios.js"
echo "   - chat-tempo-real.js"
echo "   - chat-calls.js"
echo ""
echo "Opção 2: Usar Git (se o projeto estiver em um repositório)"
echo "------------------------------------------"
echo "cd /home/seprom/sepromcbmepi"
echo "git pull origin main  # ou master, conforme sua branch"
echo ""
echo "Opção 3: Copiar conteúdo manualmente"
echo "------------------------------------------"
echo "1. Abra os arquivos localmente"
echo "2. Copie o conteúdo completo"
echo "3. No servidor, edite os arquivos:"
echo "   nano static/js/chat-widget-ios.js"
echo "   nano static/js/chat-tempo-real.js"
echo "   nano static/js/chat-calls.js"
echo "4. Cole o conteúdo e salve (Ctrl+O, Enter, Ctrl+X)"
echo ""
echo "=========================================="
echo "🔧 APÓS ATUALIZAR OS ARQUIVOS"
echo "=========================================="
echo ""
echo "1. Coletar arquivos estáticos (se necessário):"
echo "   source venv/bin/activate"
echo "   python manage.py collectstatic --noinput"
echo ""
echo "2. Reiniciar o serviço Gunicorn:"
echo "   sudo systemctl restart gunicorn"
echo ""
echo "3. Verificar status:"
echo "   sudo systemctl status gunicorn"
echo ""
echo "4. Limpar cache do navegador (Ctrl+Shift+R ou Ctrl+F5)"
echo ""
echo "=========================================="
echo "✅ CONCLUÍDO"
echo "=========================================="

