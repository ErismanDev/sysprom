#!/bin/bash
# Script para atualizar o arquivo em TODOS os locais possíveis

SERVER="root@64.23.185.235"
REMOTE_BASE="/home/seprom/sepromcbmepi"
LOCAL_FILE="static/js/chat-calls.js"

echo "==============================================================="
echo "ATUALIZANDO chat-calls.js EM TODOS OS LOCAIS"
echo "==============================================================="
echo ""

# 1. Atualizar arquivo principal
echo "1. Atualizando arquivo principal..."
scp "$LOCAL_FILE" "${SERVER}:${REMOTE_BASE}/static/js/chat-calls.js"
echo ""

# 2. Verificar se foi atualizado
echo "2. Verificando se foi atualizado..."
ssh $SERVER "grep -n 'Exibindo video remoto (condicoes atendidas)' ${REMOTE_BASE}/static/js/chat-calls.js"
echo ""

# 3. Verificar se existe staticfiles
echo "3. Verificando se existe staticfiles..."
ssh $SERVER "if [ -f '${REMOTE_BASE}/staticfiles/js/chat-calls.js' ]; then echo 'EXISTE - Atualizando...'; cp ${REMOTE_BASE}/static/js/chat-calls.js ${REMOTE_BASE}/staticfiles/js/chat-calls.js; echo 'Atualizado em staticfiles'; else echo 'NAO EXISTE'; fi"
echo ""

# 4. Recarregar Nginx
echo "4. Recarregando Nginx..."
ssh $SERVER "systemctl reload nginx"
echo ""

# 5. Verificar permissões
echo "5. Verificando permissões..."
ssh $SERVER "chmod 644 ${REMOTE_BASE}/static/js/chat-calls.js && ls -la ${REMOTE_BASE}/static/js/chat-calls.js"
echo ""

echo "==============================================================="
echo "PRONTO! Agora limpe o cache do navegador e teste novamente"
echo "==============================================================="

