# 📥 Restaurar Backup PostgreSQL no Servidor

## ✅ Backup Criado

- **Formato**: PostgreSQL SQL (pg_dump)
- **Arquivo**: `backup_sepromcbmepi_YYYYMMDD_HHMMSS.sql`
- **Vantagens**:
  - ✅ Mais rápido que JSON
  - ✅ Preserva estrutura completa do banco
  - ✅ Mantém constraints, índices, triggers
  - ✅ Mais confiável para restauração

---

## 📤 PASSO 1: Enviar Backup via WinSCP

1. Abra o WinSCP
2. Conecte ao servidor: `64.23.185.235` (usuário: `root`)
3. Navegue até: `/home/seprom/sepromcbmepi/`
4. Arraste o arquivo `.sql` para lá
5. Aguarde o upload terminar

---

## 🔧 PASSO 2: Restaurar Backup no Servidor

### Opção A: Restaurar Substituindo Banco Existente

```bash
# Parar aplicação
systemctl stop seprom

# Fazer backup de segurança do banco atual
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# Deletar banco atual
su - postgres -c "psql -c 'DROP DATABASE IF EXISTS sepromcbmepi;'"

# Criar banco vazio
su - postgres -c "psql -c 'CREATE DATABASE sepromcbmepi OWNER seprom;'"
su - postgres -c "psql -c 'GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;'"

# Restaurar backup
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql 2>/dev/null | head -1)
if [ -n "$BACKUP_FILE" ]; then
    echo "Restaurando: $BACKUP_FILE"
    su - postgres -c "psql sepromcbmepi < $BACKUP_FILE"
    echo "✅ Backup restaurado!"
else
    echo "❌ Nenhum arquivo de backup encontrado!"
fi

# Reiniciar aplicação
systemctl start seprom
```

### Opção B: Restaurar Diretamente (Mais Simples)

```bash
# Parar aplicação
systemctl stop seprom

# Backup de segurança
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# Encontrar arquivo de backup
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql 2>/dev/null | head -1)

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Nenhum arquivo de backup encontrado!"
    exit 1
fi

echo "📦 Restaurando: $BACKUP_FILE"

# Deletar e recriar banco
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Restaurar backup
su - postgres -c "psql sepromcbmepi < $BACKUP_FILE"

# Reiniciar aplicação
systemctl start seprom

echo "✅ Restauração concluída!"
```

---

## 🚀 COMANDO ÚNICO (Copie e Cole Tudo)

```bash
systemctl stop seprom && \
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_\$(date +%Y%m%d_%H%M%S).sql" && \
BACKUP_FILE=\$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql 2>/dev/null | head -1) && \
if [ -z "\$BACKUP_FILE" ]; then echo "❌ Nenhum backup encontrado!"; exit 1; fi && \
echo "📦 Restaurando: \$BACKUP_FILE" && \
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
&& \
su - postgres -c "psql sepromcbmepi < \$BACKUP_FILE" && \
systemctl start seprom && \
echo "✅ Restauração concluída!"
```

---

## ✅ Verificar Restauração

```bash
# Verificar dados
su - postgres -c "psql sepromcbmepi -c \"
SELECT 
    'auth_user' as tabela, COUNT(*) as registros FROM auth_user
UNION ALL
SELECT 'militares_militar', COUNT(*) FROM militares_militar;
\""

# Verificar aplicação
curl -I http://localhost
```

---

## 📝 Vantagens do Backup PostgreSQL

- ✅ **Mais rápido**: pg_dump é otimizado para PostgreSQL
- ✅ **Estrutura completa**: Preserva índices, constraints, triggers
- ✅ **Mais confiável**: Menos problemas de encoding e compatibilidade
- ✅ **Menor tamanho**: Arquivos SQL são geralmente menores que JSON
- ✅ **Restauração simples**: Um comando `psql` restaura tudo

---

## 🔧 Se Houver Problemas

### Erro de permissão

```bash
# Verificar permissões do arquivo
ls -la /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql

# Dar permissão de leitura
chmod 644 /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql
```

### Erro de encoding

```bash
# Verificar encoding do arquivo
file -bi /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql

# Se necessário, converter para UTF-8
iconv -f ISO-8859-1 -t UTF-8 backup.sql > backup_utf8.sql
```

