#!/bin/bash

# Script de Atualização para Servidor Digital Ocean
# Execute no terminal do Cursor: ./atualizar_servidor.sh

echo "==============================================================="
echo "🚀 ATUALIZANDO SISTEMA NO SERVIDOR"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi"
SERVICE_NAME="seprom"

# Verificar se está conectado ao servidor
echo "🔍 Verificando conexão com servidor..."
if ! ssh -o ConnectTimeout=5 ${USER}@${SERVER} "echo 'Conexão OK'" 2>/dev/null; then
    echo "❌ Erro: Não foi possível conectar ao servidor ${SERVER}"
    echo "   Verifique se:"
    echo "   1. O servidor está online"
    echo "   2. Você tem acesso SSH configurado"
    echo "   3. A chave SSH está correta"
    exit 1
fi

echo "✅ Conexão estabelecida!"
echo ""

# Executar comandos no servidor via SSH
echo "📦 Atualizando código no servidor..."

ssh ${USER}@${SERVER} << ENDSSH
    cd ${REMOTE_PATH}
    
    echo "💾 Criando backup rápido..."
    BACKUP_DIR="/home/seprom/backups/\$(date +%Y%m%d_%H%M%S)"
    mkdir -p "\$BACKUP_DIR"
    cp -r . "\$BACKUP_DIR/" 2>/dev/null || echo "⚠️  Backup criado com avisos"
    echo "✅ Backup salvo em: \$BACKUP_DIR"
    
    echo ""
    echo "📥 Fazendo pull do repositório..."
    git pull origin master || git pull origin main || {
        echo "⚠️  Erro ao fazer pull do git"
        exit 1
    }
    
    echo ""
    echo "🐍 Ativando ambiente virtual..."
    source venv/bin/activate || {
        echo "❌ Erro ao ativar venv"
        exit 1
    }
    
    echo ""
    echo "🗄️  Executando migrations..."
    python manage.py migrate --noinput
    
    echo ""
    echo "📁 Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput --clear
    
    echo ""
    echo "🔄 Reiniciando serviço Gunicorn..."
    sudo systemctl restart ${SERVICE_NAME}
    sleep 3
    
    echo ""
    echo "📊 Verificando status do serviço..."
    sudo systemctl status ${SERVICE_NAME} --no-pager -l | head -20
    
    echo ""
    echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
    echo "🌐 Acesse: http://${SERVER}/login/"
ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================================="
    echo "✅ Script executado com sucesso!"
    echo "==============================================================="
else
    echo ""
    echo "==============================================================="
    echo "❌ Erro durante a execução do script"
    echo "==============================================================="
    exit 1
fi

