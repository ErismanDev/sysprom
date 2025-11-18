#!/bin/bash
# Script para verificar se o arquivo foi atualizado no servidor

echo "Verificando se o arquivo foi atualizado no servidor..."
echo ""

# Verificar se contém a mensagem nova
echo "Procurando por 'Exibindo video remoto (condicoes atendidas)':"
ssh root@64.23.185.235 "grep -n 'Exibindo video remoto (condicoes atendidas)' /home/seprom/sepromcbmepi/static/js/chat-calls.js"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ARQUIVO FOI ATUALIZADO NO SERVIDOR!"
    echo ""
    echo "Se ainda aparece linha 221 no navegador, o problema é CACHE:"
    echo "1. Limpar cache: Ctrl+Shift+Delete"
    echo "2. Ou usar modo anonimo: Ctrl+Shift+N"
    echo "3. Ou hard refresh: Ctrl+Shift+R"
else
    echo ""
    echo "❌ ARQUIVO AINDA NÃO FOI ATUALIZADO NO SERVIDOR!"
    echo ""
    echo "Verificando versão antiga:"
    ssh root@64.23.185.235 "grep -n 'Exibindo video remoto' /home/seprom/sepromcbmepi/static/js/chat-calls.js | head -1"
    echo ""
    echo "Tente atualizar novamente usando WinSCP ou SCP"
fi

echo ""
echo "Verificando tamanho do arquivo:"
ssh root@64.23.185.235 "ls -lh /home/seprom/sepromcbmepi/static/js/chat-calls.js"

echo ""
echo "Verificando permissões:"
ssh root@64.23.185.235 "ls -la /home/seprom/sepromcbmepi/static/js/chat-calls.js"

