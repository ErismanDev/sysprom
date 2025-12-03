#!/bin/bash

# Script para atualizar correção de permissões do menu Configurações no Digital Ocean
# Execute no terminal do Cursor: ./atualizar_configuracoes_do.sh

echo "==============================================================="
echo "🚀 ATUALIZANDO CORREÇÃO DE PERMISSÕES - MENU CONFIGURAÇÕES"
echo "==============================================================="
echo ""

SERVER="164.92.118.212"
SSH_USER="${SSH_USER:-root}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_rsa}"
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
if [ ! -f "$SSH_KEY" ]; then
    echo "⚠️  Chave SSH não encontrada em: $SSH_KEY"
    echo "   Configure SSH keys ou informe o caminho da chave ao executar:"
    echo "   SSH_KEY=\\caminho\\para\\sua_chave SSH_USER=root ./atualizar_configuracoes_do.sh"
fi

if ! ssh -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 ${SSH_USER}@${SERVER} "echo 'Conexão OK'" 2>/dev/null; then
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
ssh -i "$SSH_KEY" -o BatchMode=yes -o StrictHostKeyChecking=accept-new ${SSH_USER}@${SERVER} << 'ENDSSH'
    echo "📦 Atualizando código do repositório..."
    cd /home/seprom/sepromcbmepi
    
    # Configurar exceção de propriedade para o Git (evita 'dubious ownership')
    echo "🔐 Configurando Git safe.directory..."
    git config --global --add safe.directory /home/seprom/sepromcbmepi || true
    sudo -u seprom -H bash -lc "git config --global --add safe.directory /home/seprom/sepromcbmepi" || true
    echo "✅ safe.directory configurado (root e seprom)"

    # Fazer backup antes de atualizar
    echo "💾 Criando backup rápido..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_configuracoes"
    mkdir -p "$BACKUP_DIR"
    cp militares/context_processors.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/models.py "$BACKUP_DIR/" 2>/dev/null
    echo "✅ Backup salvo em: $BACKUP_DIR"
    
    # Atualizar código do git como usuário seprom
    if [ -d ".git" ]; then
        echo "📥 Fazendo pull do repositório (usuário seprom)..."
        sudo -u seprom -H bash -lc "cd /home/seprom/sepromcbmepi && (git pull origin main 2>/dev/null || git pull origin master 2>/dev/null)" || {
            echo "⚠️  Não foi possível fazer pull do git"
            exit 1
        }
        echo "✅ Código atualizado!"
    else
        echo "❌ Repositório Git não encontrado"
        exit 1
    fi
    
    echo ""
    echo "🐍 Ativando ambiente virtual e aplicando migrações/estáticos (usuário seprom)..."
    sudo -u seprom -H bash -lc "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear" || {
        echo "❌ Erro ao executar migrações/coleta de estáticos"
        exit 1
    }
    
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
    echo "🌐 Acesse: http://164.92.118.212/login/"
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
