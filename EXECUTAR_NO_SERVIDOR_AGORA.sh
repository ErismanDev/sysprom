#!/bin/bash
# Execute estes comandos diretamente no servidor
# Copie e cole tudo de uma vez no terminal SSH

echo "🔧 Corrigindo permissões do banco de dados..."

su - postgres << 'EOF'
psql sepromcbmepi << SQL
-- Alterar owner do banco
ALTER DATABASE sepromcbmepi OWNER TO seprom;

-- Alterar owner de todas as tabelas
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' OWNER TO seprom';
    END LOOP;
END
$$;

-- Alterar owner de todas as sequences
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
        EXECUTE 'ALTER SEQUENCE public.' || quote_ident(r.sequence_name) || ' OWNER TO seprom';
    END LOOP;
END
$$;

-- Conceder permissões
GRANT ALL PRIVILEGES ON SCHEMA public TO seprom;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO seprom;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO seprom;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO seprom;

-- Permissões padrão para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO seprom;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO seprom;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO seprom;
\q
SQL
EOF

echo "✅ Permissões corrigidas!"
echo "🔄 Reiniciando aplicação..."
systemctl restart seprom
echo "✅ Concluído! Teste: http://64.23.185.235/login/"

