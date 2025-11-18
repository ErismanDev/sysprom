#!/bin/bash

# Script para atualizar correção de permissões do menu Configurações no Digital Ocean
# Execute no terminal do Cursor: ./atualizar_configuracoes_do.sh

echo "==============================================================="
echo "🚀 ATUALIZANDO CORREÇÃO DE PERMISSÕES - MENU CONFIGURAÇÕES"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi"

# Passo 1: Fazer push das alterações (se necessário)
echo "📤 Verificando se há alterações para fazer push..."
if git diff --quiet HEAD origin/master 2>/dev/null || git diff --quiet HEAD origin/main 2>/dev/null; then
    echo "✅ Código já está sincronizado com o repositório remoto"
else
    echo "📤 Fazendo push das alterações..."
    git push origin master 2>/dev/null || git push origin main 2>/dev/null || {
        echo "⚠️  Não foi possível fazer push automaticamente"
        echo "   Execute manualmente: git push"
    }
fi

echo ""
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
    echo "💾 Criando backup rápido..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_configuracoes"
    mkdir -p "$BACKUP_DIR"
    cp militares/context_processors.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/models.py "$BACKUP_DIR/" 2>/dev/null
    echo "✅ Backup salvo em: $BACKUP_DIR"
    
    # Atualizar código do git
    if [ -d ".git" ]; then
        echo "📥 Fazendo pull do repositório..."
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || {
            echo "⚠️  Não foi possível fazer pull do git"
            exit 1
        }
        echo "✅ Código atualizado!"
    else
        echo "❌ Repositório Git não encontrado"
        exit 1
    fi
    
    echo ""
    echo "🐍 Ativando ambiente virtual..."
    source venv/bin/activate || {
        echo "❌ Erro ao ativar venv"
        exit 1
    }
    
    echo ""
    echo "🗄️  Executando migrations (se houver)..."
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
    if sudo systemctl is-active --quiet seprom; then
        echo "✅ Serviço está rodando corretamente!"
    else
        echo "⚠️  Serviço pode ter problemas. Verificando logs..."
        sudo systemctl status seprom --no-pager -l | head -30
    fi
    
    echo ""
    echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
    echo "🌐 Acesse: http://64.23.185.235/login/"
    echo ""
    echo "📝 Alterações aplicadas:"
    echo "   - Mapeamento de SUBMENU_USUARIOS → show_usuarios"
    echo "   - Mapeamento de SUBMENU_PERMISSOES → show_permissoes"
    echo "   - Mapeamento de SUBMENU_LOGS → show_logs"
    echo "   - Mapeamento de SUBMENU_ADMINISTRACAO → show_administracao"
    echo "   - Mapeamento de SUBMENU_TITULOS_PUBLICACAO → show_titulos_publicacao"
    echo "   - MENU_CONFIGURACOES agora ativa show_configuracoes e show_administracao"
ENDSSH

echo ""
echo "==============================================================="
echo "✅ Script executado com sucesso!"
echo "==============================================================="

