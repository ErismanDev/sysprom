# 💾 Backup e Restaurar Banco de Dados

## 📋 ETAPA 1: Fazer Backup no PC Local (Windows)

### Opção 1: Usando pg_dump (se PostgreSQL estiver instalado)

```powershell
# No PowerShell do Windows
# Ajustar os dados de conexão conforme seu banco local
pg_dump -h localhost -U postgres -d sepromcbmepi -F c -f backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").backup

# Ou em formato SQL (texto)
pg_dump -h localhost -U postgres -d sepromcbmepi -f backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

### Opção 2: Usando Python/Django (se não tiver pg_dump)

```powershell
# No PowerShell, no diretório do projeto
cd C:\projetos\Sysgabom

# Ativar venv
.\venv\Scripts\activate

# Fazer backup usando Django
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").json
```

### Opção 3: Usando pgAdmin ou DBeaver

Se você usa interface gráfica, exporte o banco completo.

---

## 📋 ETAPA 2: Enviar Backup para o Servidor

### Via WinSCP

1. Abra WinSCP
2. Conecte ao servidor: `64.23.185.235`
3. Navegue até: `/home/seprom/sepromcbmepi/`
4. Arraste o arquivo de backup para o servidor

### Via PowerShell (SCP)

```powershell
# Enviar arquivo via SCP
scp backup_sepromcbmepi_*.backup root@64.23.185.235:/home/seprom/sepromcbmepi/

# Ou se for .sql
scp backup_sepromcbmepi_*.sql root@64.23.185.235:/home/seprom/sepromcbmepi/
```

---

## 📋 ETAPA 3: Restaurar no Servidor Digital Ocean

### Se o backup for formato .backup (PostgreSQL custom)

```bash
# Como root no servidor
# Parar aplicação temporariamente
systemctl stop seprom

# Fazer backup do banco atual (por segurança)
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_antes_restore_$(date +%Y%m%d_%H%M%S).sql"

# Limpar banco atual
su - postgres -c "psql -c 'DROP DATABASE IF EXISTS sepromcbmepi;'"
su - postgres -c "psql -c 'CREATE DATABASE sepromcbmepi OWNER seprom;'"

# Restaurar backup
su - postgres -c "pg_restore -d sepromcbmepi /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.backup"

# Reiniciar aplicação
systemctl start seprom
```

### Se o backup for formato .sql (texto)

```bash
# Como root no servidor
# Parar aplicação
systemctl stop seprom

# Fazer backup do banco atual
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_antes_restore_$(date +%Y%m%d_%H%M%S).sql"

# Limpar banco atual
su - postgres -c "psql -c 'DROP DATABASE IF EXISTS sepromcbmepi;'"
su - postgres -c "psql -c 'CREATE DATABASE sepromcbmepi OWNER seprom;'"

# Restaurar backup
su - postgres -c "psql sepromcbmepi < /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql"

# Reiniciar aplicação
systemctl start seprom
```

### Se o backup for formato .json (Django dumpdata)

```bash
# Como seprom no servidor
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Limpar banco (cuidado!)
python manage.py flush --noinput

# Carregar dados
python manage.py loaddata /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json

# Sair
exit
```

---

## ⚡ COMANDO RÁPIDO - Restaurar Backup .sql

```bash
# Parar aplicação
systemctl stop seprom

# Backup de segurança
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# Limpar e restaurar
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Restaurar (ajuste o nome do arquivo)
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql 2>/dev/null | head -1)
if [ -n "$BACKUP_FILE" ]; then
    echo "Restaurando: $BACKUP_FILE"
    su - postgres -c "psql sepromcbmepi < $BACKUP_FILE"
    echo "✅ Backup restaurado!"
else
    echo "❌ Arquivo de backup não encontrado!"
    ls -la /home/seprom/sepromcbmepi/backup_*.sql
fi

# Reiniciar aplicação
systemctl start seprom
```

---

## 🔍 Verificar Restauração

```bash
# Verificar tabelas
su - postgres -c "psql sepromcbmepi -c '\dt' | head -20"

# Verificar quantidade de registros
su - postgres -c "psql sepromcbmepi -c \"SELECT schemaname, tablename, n_tup_ins FROM pg_stat_user_tables ORDER BY n_tup_ins DESC LIMIT 10;\""

# Testar aplicação
curl http://localhost/login/ | head -10
```

---

## 📝 Notas Importantes

1. **Sempre faça backup antes de restaurar** - O comando acima faz backup automático
2. **Formato recomendado**: Use `.sql` (texto) para maior compatibilidade
3. **Tamanho do arquivo**: Se for muito grande, pode usar compressão
4. **Tempo**: A restauração pode levar alguns minutos dependendo do tamanho

---

## 🆘 Troubleshooting

### Erro: "permission denied"
```bash
# Ajustar permissões do arquivo de backup
chmod 644 /home/seprom/sepromcbmepi/backup_*.sql
chown seprom:seprom /home/seprom/sepromcbmepi/backup_*.sql
```

### Erro: "database does not exist"
```bash
# Criar banco se não existir
su - postgres -c "psql -c 'CREATE DATABASE sepromcbmepi OWNER seprom;'"
```

### Backup muito grande
```bash
# Comprimir antes de enviar
gzip backup_sepromcbmepi_*.sql

# No servidor, descomprimir
gunzip backup_sepromcbmepi_*.sql.gz
```

