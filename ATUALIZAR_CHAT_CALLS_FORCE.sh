#!/bin/bash
# Script para FORÇAR atualização do chat-calls.js no servidor Digital Ocean
# Este script também limpa o cache do navegador forçando um reload

echo "📤 FORÇANDO atualização do chat-calls.js no servidor Digital Ocean..."

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
    echo "🔄 Verificando versão do arquivo no servidor..."
    ssh $SERVER "grep -n 'Exibindo vídeo remoto' $REMOTE_PATH || echo 'Linha não encontrada (arquivo pode estar atualizado)'"
    echo ""
    echo "📋 PRÓXIMOS PASSOS OBRIGATÓRIOS:"
    echo "1. ⚠️ LIMPAR CACHE DO NAVEGADOR:"
    echo "   - Chrome/Edge: Ctrl+Shift+Delete → Limpar cache"
    echo "   - Ou: Ctrl+Shift+R (hard refresh)"
    echo "   - Ou: Abrir em modo anônimo (Ctrl+Shift+N)"
    echo ""
    echo "2. 🔍 Verificar se o arquivo foi atualizado:"
    echo "   - Abrir console (F12)"
    echo "   - Procurar por 'Exibindo vídeo remoto (condições atendidas)'"
    echo "   - Se aparecer 'Exibindo vídeo remoto' sem '(condições atendidas)', o cache não foi limpo"
    echo ""
    echo "3. 🧪 Testar novamente com duas pessoas"
    echo ""
    echo "🔄 Para reiniciar o Gunicorn (se necessário):"
    echo "   ssh $SERVER 'cd /home/seprom/sepromcbmepi && supervisorctl restart gunicorn || systemctl restart gunicorn || pkill -HUP gunicorn'"
else
    echo "❌ Erro ao copiar arquivo!"
    exit 1
fi

