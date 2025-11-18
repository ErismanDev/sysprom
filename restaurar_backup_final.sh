#!/bin/bash
# Script para restaurar backup desabilitando signals

set -e  # Parar em caso de erro

echo "🛑 Parando aplicação..."
systemctl stop seprom

echo "💾 Fazendo backup de segurança..."
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py dumpdata > /tmp/backup_seguranca_\$(date +%Y%m%d_%H%M%S).json"

echo "🗑️ Limpando banco de dados..."
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput"

echo "📥 Restaurando backup (signals desabilitados)..."
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1)

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Nenhum arquivo de backup encontrado!"
    exit 1
fi

echo "📦 Usando backup: $BACKUP_FILE"

# Restaurar com signals desabilitados
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata '$BACKUP_FILE'"

echo "✅ Backup restaurado com sucesso!"

echo "🚀 Reiniciando aplicação..."
systemctl start seprom

echo "✅ Processo concluído!"

