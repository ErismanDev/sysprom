# ✅ Restaurar Backup Ignorando Migração Problemática

## ⚠️ Problema
A migração 0074 e criação de permissões têm problemas. Vamos restaurar o backup que já tem a estrutura correta.

## 🚀 SOLUÇÃO: Restaurar Backup Diretamente

### Opção 1: Restaurar Backup que Já Tem Estrutura

O backup JSON já tem todos os dados e estrutura. Podemos restaurar diretamente:

```bash
systemctl stop seprom && \
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --run-syncdb --fake-initial" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate militares 0073" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate militares 0074 --fake" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --fake" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

---

## 🔧 SOLUÇÃO ALTERNATIVA: Usar pg_restore do Backup JSON

Se o backup JSON não funcionar, podemos tentar restaurar apenas os dados essenciais:

```bash
systemctl stop seprom && \
su - postgres << 'EOF'
psql << SQL
DROP DATABASE IF EXISTS sepromcbmepi;
CREATE DATABASE sepromcbmepi OWNER seprom;
GRANT ALL PRIVILEGES ON DATABASE sepromcbmepi TO seprom;
\q
SQL
EOF
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --run-syncdb" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
import os
os.environ['DISABLE_SIGNALS'] = '1'
from django.core.management import call_command
# Restaurar apenas dados essenciais (sem contenttypes e permissions)
call_command('loaddata', 'backup_sepromcbmepi_completo_20251115_154308.json', 
             exclude=['contenttypes', 'auth.permission'], 
             ignorenonexistent=True)
PYEOF
" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

