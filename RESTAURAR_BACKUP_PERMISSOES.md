# 🔧 Corrigir Permissões e Restaurar Backup

## ⚠️ Problema
O arquivo não tem permissão de leitura para o usuário postgres.

## ✅ SOLUÇÃO

### Opção 1: Ajustar Permissões do Arquivo

```bash
# Dar permissão de leitura para todos
chmod 644 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# OU dar permissão de leitura para o grupo postgres
chmod 640 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql
chgrp postgres /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# Depois restaurar
su - postgres -c "psql sepromcbmepi < /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql"
```

### Opção 2: Copiar para /tmp (Mais Simples)

```bash
# Copiar arquivo para /tmp (acessível por todos)
cp /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql /tmp/backup_restore.sql

# Restaurar de /tmp
su - postgres -c "psql sepromcbmepi < /tmp/backup_restore.sql"

# Limpar arquivo temporário (opcional)
rm /tmp/backup_restore.sql
```

### Opção 3: Usar cat e pipe (Mais Confiável)

```bash
# Usar cat para ler o arquivo e passar para psql
cat /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql | su - postgres -c "psql sepromcbmepi"
```

---

## 🚀 COMANDO RÁPIDO (Recomendado)

```bash
# Ajustar permissões e restaurar
chmod 644 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql && \
cat /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql | su - postgres -c "psql sepromcbmepi" && \
echo "✅ Backup restaurado!"
```

---

## 🔍 Verificar Permissões

```bash
# Ver permissões atuais
ls -la /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql
```

