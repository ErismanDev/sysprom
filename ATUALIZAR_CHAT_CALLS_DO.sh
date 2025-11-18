#!/bin/bash
# Script para atualizar chat-calls.js no servidor Digital Ocean

echo "📤 Atualizando chat-calls.js no servidor Digital Ocean..."

# Configurações
SERVER="root@64.23.185.235"
REMOTE_PATH="/home/seprom/sepromcbmepi/static/js/chat-calls.js"
LOCAL_FILE="static/js/chat-calls.js"

# Verificar se o arquivo local existe
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ Erro: Arquivo local não encontrado: $LOCAL_FILE"
    exit 1
fi

# Fazer backup do arquivo remoto
echo "💾 Fazendo backup do arquivo remoto..."
ssh $SERVER "cp $REMOTE_PATH ${REMOTE_PATH}.backup_$(date +%Y%m%d_%H%M%S) 2>/dev/null || true"

# Copiar arquivo
echo "📤 Copiando arquivo para o servidor..."
scp "$LOCAL_FILE" "$SERVER:$REMOTE_PATH"

# Verificar se a cópia foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "✅ Arquivo atualizado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Limpar cache do navegador (Ctrl+Shift+R)"
    echo "2. Testar a chamada de vídeo novamente"
    echo "3. Verificar os logs no console (F12)"
    echo ""
    echo "🔄 Para reiniciar o Gunicorn (se necessário):"
    echo "   ssh $SERVER 'cd /home/seprom/sepromcbmepi && supervisorctl restart gunicorn || systemctl restart gunicorn || pkill -HUP gunicorn'"
else
    echo "❌ Erro ao copiar arquivo!"
    exit 1
fi

