#!/bin/bash

# Script para atualizar base.html no servidor Digital Ocean
# Execute: chmod +x ATUALIZAR_BASE_HTML_DO.sh && ./ATUALIZAR_BASE_HTML_DO.sh

echo "==============================================================="
echo "ATUALIZANDO base.html NO SERVIDOR DIGITAL OCEAN"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi/templates/base.html"
LOCAL_FILE="templates/base.html"

# Verificar se o arquivo local existe
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ ERRO: Arquivo local não encontrado: $LOCAL_FILE"
    echo "Certifique-se de estar no diretório do projeto."
    exit 1
fi

echo "📁 Arquivo local: $LOCAL_FILE"
echo "🖥️  Servidor: $USER@$SERVER"
echo "📂 Caminho remoto: $REMOTE_PATH"
echo ""
echo "Você será solicitado a inserir a senha do servidor..."
echo ""

# Fazer backup do arquivo remoto antes de atualizar
echo "💾 Fazendo backup do arquivo remoto..."
ssh $USER@$SERVER "cp $REMOTE_PATH ${REMOTE_PATH}.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo 'Backup criado'"

# Copiar arquivo
echo ""
echo "📤 Copiando arquivo para o servidor..."
scp "$LOCAL_FILE" "${USER}@${SERVER}:${REMOTE_PATH}"

if [ $? -eq 0 ]; then
    echo ""
    echo "==============================================================="
    echo "✅ OK: Arquivo copiado com sucesso!"
    echo "==============================================================="
    echo ""
    echo "==============================================================="
    echo "📋 PRÓXIMOS PASSOS NO SERVIDOR:"
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
    echo "   Ou usar modo anônimo (Ctrl+Shift+N)"
    echo ""
else
    echo ""
    echo "==============================================================="
    echo "❌ ERRO: Falha ao copiar arquivo!"
    echo "==============================================================="
    echo ""
    echo "Verifique:"
    echo "- A senha do servidor está correta?"
    echo "- A conexão com o servidor está ativa?"
    echo "- O caminho do arquivo está correto?"
    echo "- O arquivo local existe?"
    echo ""
    exit 1
fi

