#!/bin/bash
# Script para atualizar correção de permissões no servidor
# Execute: ./atualizar.sh

echo "==============================================================="
echo "🚀 ATUALIZANDO CORREÇÃO DE PERMISSÕES - MENU CONFIGURAÇÕES"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi"

# Verificar conexão
echo "🔍 Verificando conexão..."
if ! ssh -o ConnectTimeout=5 ${USER}@${SERVER} "echo OK" 2>/dev/null; then
    echo "❌ Erro ao conectar ao servidor"
    exit 1
fi
echo "✅ Conexão OK!"
echo ""

# Enviar arquivos
echo "📤 Enviando arquivos..."
scp militares/context_processors.py ${USER}@${SERVER}:${REMOTE_PATH}/militares/ 2>/dev/null && echo "✅ context_processors.py enviado" || echo "⚠️  Erro ao enviar context_processors.py"
scp militares/models.py ${USER}@${SERVER}:${REMOTE_PATH}/militares/ 2>/dev/null && echo "✅ models.py enviado" || echo "⚠️  Erro ao enviar models.py"
scp militares/views_configuracoes.py ${USER}@${SERVER}:${REMOTE_PATH}/militares/ 2>/dev/null && echo "✅ views_configuracoes.py enviado" || echo "⚠️  Erro ao enviar views_configuracoes.py"

echo ""
echo "🔄 Atualizando servidor..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    cd /home/seprom/sepromcbmepi
    
    echo "💾 Backup rápido..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_config"
    mkdir -p "$BACKUP_DIR"
    cp militares/context_processors.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/models.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/views_configuracoes.py "$BACKUP_DIR/" 2>/dev/null
    
    echo "🐍 Ativando venv..."
    source venv/bin/activate
    
    echo "🗄️  Migrations..."
    python manage.py migrate --noinput
    
    echo "📁 Static files..."
    python manage.py collectstatic --noinput --clear
    
    echo "🔄 Reiniciando serviço..."
    sudo systemctl restart seprom
    sleep 3
    
    echo ""
    echo "✅ CONCLUÍDO!"
    echo "🌐 http://64.23.185.235/login/"
ENDSSH

echo ""
echo "==============================================================="
echo "✅ Atualização concluída!"
echo "==============================================================="
