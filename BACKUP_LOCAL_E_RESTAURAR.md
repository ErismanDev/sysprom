# 💾 Backup Local e Restaurar no Digital Ocean

## 📋 ETAPA 1: Fazer Backup no PC (Windows PowerShell)

### Opção 1: Backup Django (JSON) - Recomendado

```powershell
# No PowerShell, no diretório do projeto
cd C:\projetos\Sysgabom

# Ativar venv
.\venv\Scripts\activate

# Fazer backup completo
python manage.py dumpdata > backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").json

# Ou backup sem permissões e contenttypes (mais rápido)
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").json
```

### Opção 2: Backup PostgreSQL (SQL) - Se tiver pg_dump

```powershell
# Backup em formato SQL
pg_dump -h localhost -U postgres -d sepromcbmepi -f backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Ou formato custom (menor, mais rápido)
pg_dump -h localhost -U postgres -d sepromcbmepi -F c -f backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").backup
```

---

## 📋 ETAPA 2: Enviar via WinSCP

1. Abra WinSCP
2. Conecte: `64.23.185.235` (usuário: root)
3. Navegue até: `/home/seprom/sepromcbmepi/`
4. Arraste o arquivo de backup para o servidor
5. Aguarde o upload completar

---

## 📋 ETAPA 3: Restaurar no Servidor (Console Digital Ocean)

### Se backup for .json (Django)

```bash
# Parar aplicação
systemctl stop seprom

# Mudar para seprom
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Fazer backup de segurança do banco atual
python manage.py dumpdata > /tmp/backup_seguranca_$(date +%Y%m%d_%H%M%S).json

# Limpar banco
python manage.py flush --noinput

# Encontrar e restaurar backup
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1)
if [ -n "$BACKUP_FILE" ]; then
    echo "Restaurando: $BACKUP_FILE"
    python manage.py loaddata "$BACKUP_FILE"
    echo "✅ Backup restaurado com sucesso!"
else
    echo "❌ Arquivo de backup não encontrado!"
    ls -la /home/seprom/sepromcbmepi/backup_*.json
fi

# Sair
exit

# Reiniciar aplicação
systemctl start seprom
```

### Se backup for .sql (PostgreSQL)

```bash
# Parar aplicação
systemctl stop seprom

# Fazer backup de segurança
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# Limpar banco
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Encontrar e restaurar backup
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql 2>/dev/null | head -1)
if [ -n "$BACKUP_FILE" ]; then
    echo "Restaurando: $BACKUP_FILE"
    su - postgres -c "psql sepromcbmepi < $BACKUP_FILE"
    echo "✅ Backup restaurado com sucesso!"
else
    echo "❌ Arquivo de backup não encontrado!"
    ls -la /home/seprom/sepromcbmepi/backup_*.sql
fi

# Reiniciar aplicação
systemctl start seprom
```

### Se backup for .backup (PostgreSQL custom)

```bash
# Parar aplicação
systemctl stop seprom

# Fazer backup de segurança
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_$(date +%Y%m%d_%H%M%S).sql"

# Limpar banco
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF

# Encontrar e restaurar backup
BACKUP_FILE=$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.backup 2>/dev/null | head -1)
if [ -n "$BACKUP_FILE" ]; then
    echo "Restaurando: $BACKUP_FILE"
    su - postgres -c "pg_restore -d sepromcbmepi $BACKUP_FILE"
    echo "✅ Backup restaurado com sucesso!"
else
    echo "❌ Arquivo de backup não encontrado!"
    ls -la /home/seprom/sepromcbmepi/backup_*.backup
fi

# Reiniciar aplicação
systemctl start seprom
```

---

## ⚡ COMANDO ÚNICO - Restaurar JSON

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py dumpdata > /tmp/backup_seguranca_\$(date +%Y%m%d_%H%M%S).json && python manage.py flush --noinput && python manage.py loaddata \$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>/dev/null | head -1)" && \
systemctl start seprom && \
echo "✅ Backup restaurado!"
```

---

## ⚡ COMANDO ÚNICO - Restaurar SQL

```bash
systemctl stop seprom && \
su - postgres -c "pg_dump sepromcbmepi > /tmp/sepromcbmepi_backup_seguranca_\$(date +%Y%m%d_%H%M%S).sql" && \
su - postgres -c "psql -c 'DROP DATABASE IF EXISTS sepromcbmepi; CREATE DATABASE sepromcbmepi OWNER seprom; GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;'" && \
su - postgres -c "psql sepromcbmepi < \$(ls -t /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.sql 2>/dev/null | head -1)" && \
systemctl start seprom && \
echo "✅ Backup restaurado!"
```

---

## ✅ Verificar Restauração

```bash
# Verificar tabelas
su - postgres -c "psql sepromcbmepi -c '\dt' | head -20"

# Verificar quantidade de registros em algumas tabelas
su - postgres -c "psql sepromcbmepi -c \"SELECT 'militares_militar' as tabela, COUNT(*) as registros FROM militares_militar UNION ALL SELECT 'auth_user', COUNT(*) FROM auth_user;\""

# Testar aplicação
curl http://localhost/login/ | head -10
```

---

## 📝 Resumo dos Passos

1. **No PC (PowerShell):**
   ```powershell
   cd C:\projetos\Sysgabom
   .\venv\Scripts\activate
   python manage.py dumpdata > backup_sepromcbmepi_$(Get-Date -Format "yyyyMMdd_HHmmss").json
   ```

2. **Via WinSCP:**
   - Conectar: `64.23.185.235`
   - Enviar arquivo para: `/home/seprom/sepromcbmepi/`

3. **No Servidor (Console Digital Ocean):**
   - Execute o comando único de restauração conforme o formato do backup

---

## 🆘 Troubleshooting

### Arquivo não encontrado
```bash
# Listar arquivos de backup
ls -lh /home/seprom/sepromcbmepi/backup_*

# Verificar permissões
chmod 644 /home/seprom/sepromcbmepi/backup_*
```

### Erro ao restaurar
```bash
# Ver logs do Django
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py loaddata /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json 2>&1"
```

