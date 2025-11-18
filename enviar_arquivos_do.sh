#!/bin/bash
# Script para enviar arquivos diretamente para o servidor Digital Ocean
# Execute: ./enviar_arquivos_do.sh

echo "==============================================================="
echo "📤 ENVIANDO ARQUIVOS PARA O SERVIDOR"
echo "==============================================================="
echo ""

SERVER="64.23.185.235"
USER="root"
REMOTE_PATH="/home/seprom/sepromcbmepi"

# Arquivos a serem enviados
FILES=(
    "militares/context_processors.py"
    "militares/models.py"
    "militares/views_configuracoes.py"
)

echo "📦 Enviando arquivos..."
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   Enviando: $file"
        scp "$file" ${USER}@${SERVER}:${REMOTE_PATH}/$file
        if [ $? -eq 0 ]; then
            echo "   ✅ $file enviado com sucesso"
        else
            echo "   ❌ Erro ao enviar $file"
        fi
    else
        echo "   ⚠️  Arquivo não encontrado: $file"
    fi
done

echo ""
echo "🔄 Executando comandos no servidor..."
ssh ${USER}@${SERVER} << 'ENDSSH'
    cd /home/seprom/sepromcbmepi
    
    echo "💾 Backup rápido..."
    BACKUP_DIR="/home/seprom/backups/$(date +%Y%m%d_%H%M%S)_config"
    mkdir -p "$BACKUP_DIR"
    cp militares/context_processors.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/models.py "$BACKUP_DIR/" 2>/dev/null
    cp militares/views_configuracoes.py "$BACKUP_DIR/" 2>/dev/null
    echo "✅ Backup: $BACKUP_DIR"
    
    echo ""
    echo "🐍 Ativando venv..."
    source venv/bin/activate
    
    echo ""
    echo "🗄️  Migrations..."
    python manage.py migrate --noinput
    
    echo ""
    echo "📁 Static files..."
    python manage.py collectstatic --noinput --clear
    
    echo ""
    echo "🔄 Reiniciando serviço..."
    sudo systemctl restart seprom
    sleep 3
    
    echo ""
    echo "📊 Status:"
    sudo systemctl status seprom --no-pager -l | head -15
    
    echo ""
    echo "✅ CONCLUÍDO!"
ENDSSH

echo ""
echo "==============================================================="
echo "✅ Arquivos enviados e servidor atualizado!"
echo "==============================================================="

