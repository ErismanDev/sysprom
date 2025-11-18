#!/bin/bash
# Script para restaurar backup no servidor Digital Ocean
# IP: 64.23.185.235
# Gerado em: 2025-11-16 11:41:38

set -e  # Parar em caso de erro

BACKUP_FILE="backup_sepromcbmepi_completo_20251116_114134.sql"
DB_NAME="sepromcbmepi"
DB_USER="seprom"

echo "=========================================="
echo "🔄 RESTAURANDO BACKUP NO DIGITAL OCEAN"
echo "=========================================="
echo "📁 Arquivo: $BACKUP_FILE"
echo "📊 Banco: $DB_NAME"
echo "=========================================="

# Verificar se o arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ ERRO: Arquivo de backup não encontrado: $BACKUP_FILE"
    echo "💡 Certifique-se de que o arquivo foi enviado para o servidor"
    exit 1
fi

# Parar aplicação
echo ""
echo "⏸️  Parando aplicação..."
systemctl stop seprom || echo "⚠️  Serviço seprom não encontrado ou já parado"

# Fazer backup de segurança do banco atual
echo ""
echo "💾 Fazendo backup de segurança do banco atual..."
BACKUP_SEGURANCA="/tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"
su - postgres -c "pg_dump $DB_NAME > $BACKUP_SEGURANCA" || echo "⚠️  Não foi possível fazer backup de segurança"
if [ -f "$BACKUP_SEGURANCA" ]; then
    echo "✅ Backup de segurança criado: $BACKUP_SEGURANCA"
fi

# Limpar banco atual
echo ""
echo "🧹 Limpando banco atual..."
su - postgres << 'EOF'
psql << SQL
-- Terminar conexões ativas
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'sepromcbmepi' AND pid <> pg_backend_pid();

-- Dropar e recriar banco
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Restaurar backup
echo ""
echo "📥 Restaurando backup..."
echo "   Isso pode levar alguns minutos dependendo do tamanho do banco..."

# Verificar se o arquivo está comprimido
if [ -f "$BACKUP_FILE.gz" ]; then
    echo "   Descomprimindo arquivo..."
    gunzip -c "$BACKUP_FILE.gz" | su - postgres -c "psql $DB_NAME"
elif [ -f "$BACKUP_FILE" ]; then
    su - postgres -c "psql $DB_NAME < $BACKUP_FILE"
else
    echo "❌ ERRO: Arquivo de backup não encontrado!"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "✅ Backup restaurado com sucesso!"
else
    echo "❌ ERRO ao restaurar backup!"
    exit 1
fi

# Verificar restauração
echo ""
echo "🔍 Verificando restauração..."
TABLES_COUNT=$(su - postgres -c "psql $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"")
echo "   Tabelas encontradas: $TABLES_COUNT"

# Reiniciar aplicação
echo ""
echo "▶️  Reiniciando aplicação..."
systemctl start seprom || echo "⚠️  Serviço seprom não encontrado"

echo ""
echo "=========================================="
echo "✅ RESTAURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo "💡 Próximos passos:"
echo "   1. Verificar logs: journalctl -u seprom -f"
echo "   2. Testar aplicação: curl http://localhost/"
echo "   3. Verificar banco: su - postgres -c 'psql $DB_NAME -c "\dt"'"
echo "=========================================="
