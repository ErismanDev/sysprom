#!/bin/bash

# Script para atualizar base.html no Digital Ocean
# Execute: ./atualizar_base_html.sh

echo "==============================================================="
echo "ATUALIZANDO base.html NO SERVIDOR DIGITAL OCEAN"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi/templates/base.html"
LOCAL_FILE="templates/base.html"

# Verificar se o arquivo existe
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ ERRO: Arquivo não encontrado: $LOCAL_FILE"
    echo "Certifique-se de estar no diretório do projeto."
    exit 1
fi

echo "✅ Arquivo local encontrado: $LOCAL_FILE"
echo ""
echo "📤 Copiando arquivo para o servidor..."
echo "   Servidor: $SERVER"
echo "   Usuário: $USER"
echo "   Destino: $REMOTE_PATH"
echo ""
echo "🔑 Você será solicitado a inserir a senha: erismaN@193a"
echo ""

# Copiar arquivo
scp "$LOCAL_FILE" "${USER}@${SERVER}:${REMOTE_PATH}"

if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================================="
    echo "✅ OK: Arquivo copiado com sucesso!"
    echo "==============================================================="
    echo ""
    echo "Verificando se foi atualizado..."
    ssh "${USER}@${SERVER}" "grep -n 'RESPONSIVIDADE PARA SMARTPHONES' $REMOTE_PATH"
    echo ""
    echo "==============================================================="
    echo "📋 PRÓXIMOS PASSOS:"
    echo "==============================================================="
    echo ""
    echo "1. Conectar ao servidor:"
    echo "   ssh $USER@$SERVER"
    echo ""
    echo "2. Executar comandos de atualização:"
    echo "   cd /home/seprom/sepromcbmepi"
    echo "   source venv/bin/activate"
    echo "   python manage.py collectstatic --noinput"
    echo "   sudo systemctl restart seprom"
    echo "   sudo systemctl status seprom"
    echo ""
    echo "==============================================================="
    echo "⚡ COMANDO RÁPIDO (copie e cole no servidor):"
    echo "==============================================================="
    echo ""
    echo "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py collectstatic --noinput && sudo systemctl restart seprom && sudo systemctl status seprom"
    echo ""
    echo "3. Limpar cache do navegador (Ctrl+Shift+Delete)"
    echo "4. Ou usar modo anônimo (Ctrl+Shift+N)"
    echo "5. Testar em smartphone ou redimensionar janela"
    echo ""
else
    echo ""
    echo "==============================================================="
    echo "❌ ERRO: Falha ao copiar arquivo!"
    echo "==============================================================="
    echo ""
    echo "Possíveis causas:"
    echo "- Senha incorreta (senha: erismaN@193a)"
    echo "- Problema de conexão com o servidor"
    echo "- Firewall bloqueando a conexão"
    echo ""
    echo "==============================================================="
    echo "💡 SOLUÇÃO ALTERNATIVA: Usar WinSCP"
    echo "==============================================================="
    echo ""
    echo "1. Abra o WinSCP"
    echo "2. Conecte ao servidor: $SERVER (usuário: $USER)"
    echo "3. Navegue até: $REMOTE_PATH"
    echo "4. Arraste o arquivo $LOCAL_FILE para o servidor"
    echo ""
    exit 1
fi

