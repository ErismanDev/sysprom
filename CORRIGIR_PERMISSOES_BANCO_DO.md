# 🔧 Corrigir Permissões do Banco de Dados no Digital Ocean

## ⚠️ Problema

Após restaurar o backup, o erro "Permissão negada para a tabela django_session" ocorre porque as tabelas foram criadas com o usuário `postgres` como owner, mas a aplicação Django usa o usuário `seprom`.

---

## ✅ SOLUÇÃO: Corrigir Permissões

Execute estes comandos **no servidor Digital Ocean**:

### Opção 1: Comandos Manuais (Recomendado)

```bash
# Conectar ao servidor
ssh root@64.23.185.235

# Corrigir permissões de todas as tabelas
su - postgres << 'EOF'
psql sepromcbmepi << SQL
-- Alterar owner de todas as tabelas para seprom
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' OWNER TO seprom';
    END LOOP;
END
\$\$;

-- Alterar owner de todas as sequences para seprom
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
        EXECUTE 'ALTER SEQUENCE public.' || quote_ident(r.sequence_name) || ' OWNER TO seprom';
    END LOOP;
END
\$\$;

-- Conceder todas as permissões necessárias
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
GRANT ALL PRIVILEGES ON SCHEMA public TO seprom;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO seprom;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO seprom;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO seprom;

-- Definir permissões padrão para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO seprom;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO seprom;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO seprom;

\q
SQL
EOF
```

### Opção 2: Comando Único Simplificado

```bash
su - postgres -c "psql sepromcbmepi -c \"ALTER DATABASE sepromcbmepi OWNER TO seprom;\""
su - postgres -c "psql sepromcbmepi -c \"GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;\""
su - postgres -c "psql sepromcbmepi -c \"GRANT ALL PRIVILEGES ON SCHEMA public TO seprom;\""
su - postgres -c "psql sepromcbmepi -c \"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO seprom;\""
su - postgres -c "psql sepromcbmepi -c \"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO seprom;\""
su - postgres -c "psql sepromcbmepi -c \"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO seprom;\""
su - postgres -c "psql sepromcbmepi -c \"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO seprom;\""
```

### Opção 3: Script Completo (Copiar e Colar)

```bash
#!/bin/bash
# Script para corrigir permissões do banco de dados

echo "🔧 Corrigindo permissões do banco de dados..."

su - postgres << 'EOF'
psql sepromcbmepi << SQL
-- Alterar owner do banco
ALTER DATABASE sepromcbmepi OWNER TO seprom;

-- Alterar owner de todas as tabelas
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' OWNER TO seprom';
    END LOOP;
END
\$\$;

-- Alterar owner de todas as sequences
DO \$\$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
        EXECUTE 'ALTER SEQUENCE public.' || quote_ident(r.sequence_name) || ' OWNER TO seprom';
    END LOOP;
END
\$\$;

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
```

---

## 🔍 Verificar Permissões

Após executar os comandos, verifique se as permissões estão corretas:

```bash
# Verificar owner das tabelas
su - postgres -c "psql sepromcbmepi -c \"SELECT tablename, tableowner FROM pg_tables WHERE schemaname = 'public' LIMIT 10;\""

# Verificar permissões do usuário seprom
su - postgres -c "psql sepromcbmepi -c \"SELECT grantee, privilege_type FROM information_schema.table_privileges WHERE grantee = 'seprom' LIMIT 10;\""
```

---

## 🔄 Reiniciar Aplicação

Após corrigir as permissões, reinicie a aplicação:

```bash
systemctl restart seprom
systemctl status seprom
```

---

## ✅ Testar

Acesse a aplicação no navegador:
- http://64.23.185.235/login/

O erro de permissão deve estar resolvido.

---

## 🆘 Se Ainda Der Erro

Se ainda houver problemas, verifique:

1. **Usuário do banco existe:**
```bash
su - postgres -c "psql -c '\du' | grep seprom"
```

2. **Conexão do Django:**
```bash
# Verificar configuração do banco
grep -A 10 "DATABASES" /home/seprom/sepromcbmepi/sepromcbmepi/settings.py
```

3. **Testar conexão manual:**
```bash
su - seprom -c "psql -U seprom -d sepromcbmepi -c 'SELECT COUNT(*) FROM django_session;'"
```

---

**Última atualização**: 2024-11-16

