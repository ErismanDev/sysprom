#!/bin/bash
# Script para atualizar chat-calls.js no servidor e VERIFICAR se foi atualizado

echo "═══════════════════════════════════════════════════════════════"
echo "📤 ATUALIZANDO chat-calls.js NO SERVIDOR DIGITAL OCEAN"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configurações
SERVER="root@64.23.185.235"
REMOTE_PATH="/home/seprom/sepromcbmepi/static/js/chat-calls.js"
LOCAL_FILE="static/js/chat-calls.js"

# Verificar se o arquivo local existe
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ Erro: Arquivo local não encontrado: $LOCAL_FILE"
    exit 1
fi

echo "📋 Verificando arquivo local..."
LOCAL_LINE=$(grep -n "Exibindo vídeo remoto (condições atendidas)" "$LOCAL_FILE" | cut -d: -f1)
if [ -z "$LOCAL_LINE" ]; then
    echo "❌ Erro: Arquivo local não contém a mensagem esperada!"
    exit 1
fi
echo "✅ Arquivo local OK (linha $LOCAL_LINE)"
echo ""

# Fazer backup do arquivo remoto
echo "💾 Fazendo backup do arquivo remoto..."
BACKUP_FILE="${REMOTE_PATH}.backup_$(date +%Y%m%d_%H%M%S)"
ssh $SERVER "cp $REMOTE_PATH $BACKUP_FILE 2>/dev/null && echo 'Backup criado: $BACKUP_FILE' || echo 'Aviso: Não foi possível criar backup'"
echo ""

# Verificar versão ANTES da atualização
echo "🔍 Verificando versão ANTES da atualização..."
REMOTE_LINE_BEFORE=$(ssh $SERVER "grep -n 'Exibindo vídeo remoto' $REMOTE_PATH 2>/dev/null | head -1 | cut -d: -f1")
if [ -z "$REMOTE_LINE_BEFORE" ]; then
    echo "⚠️ Mensagem não encontrada no arquivo remoto (pode estar desatualizado)"
else
    echo "📄 Linha atual no servidor: $REMOTE_LINE_BEFORE"
fi
echo ""

# Copiar arquivo
echo "📤 Copiando arquivo para o servidor..."
scp "$LOCAL_FILE" "$SERVER:$REMOTE_PATH"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao copiar arquivo!"
    exit 1
fi

echo "✅ Arquivo copiado com sucesso!"
echo ""

# Aguardar um pouco para garantir que o arquivo foi escrito
sleep 1

# Verificar versão DEPOIS da atualização
echo "🔍 Verificando versão DEPOIS da atualização..."
REMOTE_LINE_AFTER=$(ssh $SERVER "grep -n 'Exibindo vídeo remoto (condições atendidas)' $REMOTE_PATH 2>/dev/null | head -1 | cut -d: -f1")
REMOTE_LINE_OLD=$(ssh $SERVER "grep -n 'Exibindo vídeo remoto' $REMOTE_PATH 2>/dev/null | grep -v 'condições atendidas' | head -1 | cut -d: -f1")

if [ -n "$REMOTE_LINE_AFTER" ]; then
    echo "✅ ✅ ✅ ARQUIVO ATUALIZADO COM SUCESSO!"
    echo "📄 Nova linha no servidor: $REMOTE_LINE_AFTER"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ VERIFICAÇÃO: Arquivo contém 'Exibindo vídeo remoto (condições atendidas)'"
    echo "═══════════════════════════════════════════════════════════════"
elif [ -n "$REMOTE_LINE_OLD" ]; then
    echo "❌ ❌ ❌ ARQUIVO NÃO FOI ATUALIZADO!"
    echo "📄 Ainda contém versão antiga na linha: $REMOTE_LINE_OLD"
    echo ""
    echo "🔍 Verificando permissões..."
    ssh $SERVER "ls -la $REMOTE_PATH"
    echo ""
    echo "🔍 Verificando conteúdo (primeiras 10 linhas da mensagem)..."
    ssh $SERVER "grep -A 5 -B 5 'Exibindo vídeo remoto' $REMOTE_PATH | head -15"
    echo ""
    echo "⚠️ TENTE NOVAMENTE ou copie manualmente via SCP"
else
    echo "⚠️ Não foi possível verificar a atualização"
    echo "🔍 Verificando se o arquivo existe..."
    ssh $SERVER "ls -la $REMOTE_PATH"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 PRÓXIMOS PASSOS"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. ⚠️ LIMPAR CACHE DO NAVEGADOR (OBRIGATÓRIO):"
echo "   - Chrome/Edge: Ctrl+Shift+Delete → Limpar cache"
echo "   - Ou: Ctrl+Shift+R (hard refresh)"
echo "   - Ou: Abrir em modo anônimo (Ctrl+Shift+N)"
echo ""
echo "2. 🔍 Verificar no console (F12):"
echo "   - Procurar por 'Exibindo vídeo remoto (condições atendidas)'"
echo "   - Se aparecer apenas 'Exibindo vídeo remoto', o cache não foi limpo"
echo ""
echo "3. 🧪 Testar novamente com duas pessoas"
echo ""

