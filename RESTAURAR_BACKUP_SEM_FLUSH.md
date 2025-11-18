# ✅ Restaurar Backup Sem Flush

## ⚠️ Problema
O banco está vazio, então flush não funciona. Precisa criar tabelas primeiro.

## 🚀 SOLUÇÃO: Criar Tabelas e Restaurar

### Comando Único

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --run-syncdb" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

---

## 🔧 OU: Deletar e Recriar Banco (Mais Limpo)

### Opção A: Deletar e Recriar Banco

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
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

---

## 🚀 COMANDO RECOMENDADO (Deletar e Recriar)

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
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

