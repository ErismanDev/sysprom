#!/bin/bash

# Script de Atualização para Servidor Digital Ocean
# IP: 64.23.185.235
# Execute no terminal do Cursor: ./atualizar_servidor_do.sh

echo "==============================================================="
echo "🚀 ATUALIZANDO SISTEMA NO DIGITAL OCEAN"
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
ssh ${USER}@${SERVER} << 'ENDSSH'
    echo "📦 Atualizando código do repositório..."
    cd /home/seprom/sepromcbmepi
    
    # Fazer backup antes de atualizar
    echo "💾 Criando backup..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r . "$BACKUP_DIR/" 2>/dev/null || echo "⚠️  Backup criado com avisos"
    echo "✅ Backup salvo em: $BACKUP_DIR"
    
    # Atualizar código do git (se houver repositório)
    if [ -d ".git" ]; then
        echo "📥 Fazendo pull do repositório..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "⚠️  Não foi possível fazer pull do git"
    else
        echo "ℹ️  Repositório Git não encontrado - pulando atualização de código"
    fi
    
    echo ""
    echo "🐍 Ativando ambiente virtual..."
    source venv/bin/activate || {
        echo "❌ Erro ao ativar venv"
        exit 1
    }
    
    echo ""
    echo "📦 Atualizando dependências Python..."
    pip install --upgrade pip --quiet
    pip install -r requirements_production.txt --quiet || pip install -r requirements.txt --quiet
    
    echo ""
    echo "🗄️  Executando migrations..."
    python manage.py migrate --noinput
    
    echo ""
    echo "📁 Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput --clear
    
    echo ""
    echo "🔄 Reiniciando serviço Gunicorn..."
    sudo systemctl restart seprom
    sleep 3
    
    echo ""
    echo "📊 Verificando status do serviço..."
    sudo systemctl status seprom --no-pager -l | head -20
    
    echo ""
    echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
    echo "🌐 Acesse: http://64.23.185.235/login/"
ENDSSH

echo ""
echo "==============================================================="
echo "✅ Script executado com sucesso!"
echo "==============================================================="

