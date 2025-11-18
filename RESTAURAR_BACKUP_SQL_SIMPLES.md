# 📥 Restaurar Backup SQL - Comandos Simples

## ✅ Execute Estes Comandos Um Por Vez

### Passo 1: Parar Aplicação

```bash
systemctl stop seprom
```

### Passo 2: Backup de Segurança

```bash
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"
```

### Passo 3: Encontrar Arquivo de Backup

```bash
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql
```

### Passo 4: Deletar e Recriar Banco

```bash
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
```

### Passo 5: Restaurar Backup

```bash
# Substitua pelo nome exato do arquivo que você encontrou no Passo 3
su - postgres -c "psql sepromcbmepi < /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql"
```

### Passo 6: Reiniciar Aplicação

```bash
systemctl start seprom
```

### Passo 7: Verificar

```bash
systemctl status seprom --no-pager | head -20
```

---

## 🚀 OU: Comando Único Corrigido

```bash
systemctl stop seprom
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
su - postgres -c "psql sepromcbmepi < /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql"
systemctl start seprom
echo "✅ Restauração concluída!"
```

**⚠️ IMPORTANTE**: Substitua `backup_sepromcbmepi_20251115_154719.sql` pelo nome exato do arquivo que você enviou via WinSCP!

---

## 🔍 Verificar Nome do Arquivo

```bash
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql
```

Copie o nome exato do arquivo e use no comando de restore.

