#!/bin/bash

# Script para atualizar correção de permissões no Digital Ocean
# Execute no terminal do Cursor: ./atualizar_do.sh

echo "==============================================================="
echo "🚀 ATUALIZANDO CORREÇÃO DE PERMISSÕES - MENU CONFIGURAÇÕES"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"

# Verificar conexão
echo "🔍 Verificando conexão..."
if ! ssh -o ConnectTimeout=5 ${USER}@${SERVER} "echo OK" 2>/dev/null; then
    echo "❌ Erro ao conectar ao servidor"
    exit 1
fi
echo "✅ Conexão OK!"
echo ""

# Executar no servidor
echo "📦 Atualizando servidor..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    cd /home/seprom/sepromcbmepi
    
    echo "💾 Criando backup..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_config"
    mkdir -p "$BACKUP_DIR"
    cp militares/context_processors.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/models.py "$BACKUP_DIR/" 2>/dev/null
    echo "✅ Backup: $BACKUP_DIR"
    
    echo "📥 Git pull..."
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null
    
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
    echo ""
    echo "📝 Alterações aplicadas:"
    echo "   - SUBMENU_USUARIOS → show_usuarios"
    echo "   - SUBMENU_PERMISSOES → show_permissoes"
    echo "   - SUBMENU_LOGS → show_logs"
    echo "   - SUBMENU_ADMINISTRACAO → show_administracao"
    echo "   - SUBMENU_TITULOS_PUBLICACAO → show_titulos_publicacao"
    echo "   - MENU_CONFIGURACOES → show_configuracoes + show_administracao"
ENDSSH

echo ""
echo "==============================================================="
echo "✅ Atualização concluída!"
echo "==============================================================="
