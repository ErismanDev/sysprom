# 🔧 Restaurar Backup com Debug

## 🔍 Primeiro: Verificar o Erro

Execute e me envie a saída completa:

```bash
# Verificar se arquivo existe
ls -la /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# Tentar ler o arquivo
head -n 20 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# Verificar permissões
stat /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql
```

---

## 🔧 SOLUÇÃO: Restaurar com Verificação de Erros

### Método 1: Usar psql diretamente com arquivo

```bash
# Ajustar permissões
chmod 644 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# Mudar para usuário postgres
su - postgres

# Ir para diretório do arquivo
cd /home/seprom/sepromcbmepi

# Restaurar
psql sepromcbmepi < backup_sepromcbmepi_20251115_154719.sql

# Sair
exit
```

### Método 2: Copiar para /tmp e restaurar

```bash
# Copiar para /tmp
cp /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql /tmp/backup.sql

# Dar permissão
chmod 644 /tmp/backup.sql

# Restaurar
su - postgres -c "psql sepromcbmepi < /tmp/backup.sql"
```

### Método 3: Usar cat com tratamento de erros

```bash
chmod 644 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql
cat /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql 2>&1 | su - postgres -c "psql sepromcbmepi" 2>&1
```

---

## 🔍 Verificar Erros Específicos

### Se der erro de encoding:

```bash
# Verificar encoding do arquivo
file -bi /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# Se necessário, converter para UTF-8
iconv -f ISO-8859-1 -t UTF-8 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql > /tmp/backup_utf8.sql
su - postgres -c "psql sepromcbmepi < /tmp/backup_utf8.sql"
```

### Se der erro de formato SQL:

O arquivo pode estar em formato COPY (do script Python). Nesse caso, use o backup JSON que já funcionou:

```bash
# Usar o backup JSON que já foi criado
systemctl stop seprom
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput && python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json"
systemctl start seprom
```

---

## 🚀 COMANDO COMPLETO COM DEBUG

```bash
# Parar aplicação
systemctl stop seprom

# Verificar arquivo
echo "=== Verificando arquivo ==="
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql
file /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql | head -1

# Ajustar permissões
chmod 644 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql

# Backup de segurança
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# Deletar e recriar banco
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Tentar restaurar (mostrar erros)
echo "=== Restaurando backup ==="
cat /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql 2>&1 | su - postgres -c "psql sepromcbmepi" 2>&1 | tee /tmp/restore_errors.log

# Verificar se deu erro
if [ ${PIPESTATUS[1]} -eq 0 ]; then
    echo "✅ Backup restaurado com sucesso!"
    systemctl start seprom
else
    echo "❌ Erro ao restaurar. Verifique /tmp/restore_errors.log"
    echo "💡 Alternativa: Use o backup JSON"
fi
```

---

## 📋 Me Envie

1. A mensagem de erro completa
2. Saída do comando: `head -n 50 /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql`
3. Saída do comando: `file /home/seprom/sepromcbmepi/backup_sepromcbmepi_20251115_154719.sql`

Com essas informações, posso ajudar melhor!

