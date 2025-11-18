# 🔄 Restaurar Backup no Digital Ocean - Comandos Diretos

## ⚠️ Problema com Script

Se o script `.sh` não funcionar (erro "cannot execute"), use estes comandos diretamente no servidor.

---

## 📋 COMANDOS PARA EXECUTAR NO SERVIDOR

Execute estes comandos **um por vez** no servidor:

### 1. Verificar arquivos de backup

```bash
cd /home/seprom/sepromcbmepi
ls -lh backup_sepromcbmepi_completo_*.sql*
```

### 2. Parar aplicação

```bash
systemctl stop seprom
```

### 3. Fazer backup de segurança do banco atual

```bash
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"
```

### 4. Limpar banco atual

```bash
su - postgres << 'EOF'
psql << SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'sepromcbmepi' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
```

### 5. Restaurar backup

**Se o arquivo estiver COMPRIMIDO (.sql.gz):**

```bash
cd /home/seprom/sepromcbmepi
gunzip -c backup_sepromcbmepi_completo_20251116_114134.sql.gz | su - postgres -c "psql sepromcbmepi"
```

**Se o arquivo NÃO estiver comprimido (.sql):**

```bash
cd /home/seprom/sepromcbmepi
su - postgres -c "psql sepromcbmepi < backup_sepromcbmepi_completo_20251116_114134.sql"
```

### 6. Verificar restauração

```bash
su - postgres -c "psql sepromcbmepi -c '\dt' | head -20"
```

### 7. Reiniciar aplicação

```bash
systemctl start seprom
```

### 8. Verificar status

```bash
systemctl status seprom
```

---

## 🚀 COMANDO ÚNICO (Copiar e Colar Tudo)

Se preferir, execute tudo de uma vez:

```bash
cd /home/seprom/sepromcbmepi && \
systemctl stop seprom && \
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql" && \
su - postgres << 'EOF'
psql << SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'sepromcbmepi' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
gunzip -c backup_sepromcbmepi_completo_20251116_114134.sql.gz | su - postgres -c "psql sepromcbmepi" && \
systemctl start seprom && \
echo "✅ Restauração concluída!"
```

**⚠️ IMPORTANTE**: Substitua `backup_sepromcbmepi_completo_20251116_114134.sql.gz` pelo nome exato do arquivo que você encontrou no passo 1!

---

## 🔧 Corrigir Script no Servidor

Se quiser corrigir o script existente:

```bash
cd /home/seprom/sepromcbmepi

# Converter quebras de linha de Windows para Unix
dos2unix restaurar_backup_do_20251116_114134.sh

# Ou usar sed
sed -i 's/\r$//' restaurar_backup_do_20251116_114134.sh

# Tornar executável
chmod +x restaurar_backup_do_20251116_114134.sh

# Executar
./restaurar_backup_do_20251116_114134.sh
```

---

## 🔍 Verificar Arquivo de Backup

Antes de restaurar, verifique se o arquivo existe e seu tamanho:

```bash
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_completo_*
```

O arquivo deve ter aproximadamente:
- **Comprimido**: ~1.4 MB (`.sql.gz`)
- **Descomprimido**: ~21 MB (`.sql`)

---

## ❌ Troubleshooting

### Erro: "No such file or directory"
- Verifique se o arquivo foi enviado corretamente via WinSCP
- Confirme o nome exato do arquivo com `ls -lh`

### Erro: "permission denied"
```bash
chmod 644 /home/seprom/sepromcbmepi/backup_*.sql*
```

### Erro: "database is being accessed"
O script já termina conexões automaticamente. Se ainda der erro:
```bash
su - postgres -c "psql -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'sepromcbmepi' AND pid <> pg_backend_pid();\""
```

### Restauração muito lenta
É normal para bancos grandes. Monitore o progresso em outro terminal:
```bash
watch -n 1 "su - postgres -c \"psql sepromcbmepi -t -c 'SELECT COUNT(*) FROM information_schema.tables;'\""
```

