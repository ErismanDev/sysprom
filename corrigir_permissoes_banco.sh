#!/bin/bash
# Script para corrigir permissões do banco de dados após restauração
# Uso: ./corrigir_permissoes_banco.sh

set -e

DB_NAME="sepromcbmepi"
DB_USER="seprom"

echo "=========================================="
echo "🔧 CORRIGINDO PERMISSÕES DO BANCO"
echo "=========================================="
echo "📊 Banco: $DB_NAME"
echo "👤 Usuário: $DB_USER"
echo "=========================================="

# Corrigir permissões
su - postgres << EOF
psql $DB_NAME << SQL
-- Alterar owner do banco
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;

-- Alterar owner de todas as tabelas
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' OWNER TO $DB_USER';
    END LOOP;
END
\$\$;

-- Alterar owner de todas as sequences
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
        EXECUTE 'ALTER SEQUENCE public.' || quote_ident(r.sequence_name) || ' OWNER TO $DB_USER';
    END LOOP;
END
\$\$;

-- Conceder permissões no schema
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;

-- Conceder permissões em todas as tabelas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;

-- Conceder permissões em todas as sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- Conceder permissões em todas as functions
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $DB_USER;

-- Definir permissões padrão para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO $DB_USER;

\q
SQL
EOF

echo ""
echo "✅ Permissões corrigidas!"
echo ""
echo "🔍 Verificando permissões..."

# Verificar algumas tabelas importantes
TABLES=$(su - postgres -c "psql $DB_NAME -t -c \"SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND tableowner = '$DB_USER';\"")
echo "   Tabelas com owner correto: $TABLES"

# Reiniciar aplicação
echo ""
echo "🔄 Reiniciando aplicação..."
systemctl restart seprom || echo "⚠️  Serviço seprom não encontrado"

echo ""
echo "=========================================="
echo "✅ CONCLUÍDO!"
echo "=========================================="
echo "💡 Teste a aplicação: http://64.23.185.235/login/"
echo "=========================================="

