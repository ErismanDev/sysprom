# 🔧 Resolver Problema de Migração 0074

## ⚠️ Problema
A migração `militares.0074` está tentando remover um campo que não existe mais.

## ✅ SOLUÇÃO: Marcar Migração como Fake

### Comando Único

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
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate militares 0073" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate militares 0074 --fake" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

---

## 🔧 OU: Passo a Passo

### Passo 1: Parar Aplicação
```bash
systemctl stop seprom
```

### Passo 2: Deletar e Recriar Banco
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

### Passo 3: Executar Migrações até 0073
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate militares 0073"
```

### Passo 4: Marcar 0074 como Fake
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate militares 0074 --fake"
```

### Passo 5: Executar Resto das Migrações
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate"
```

### Passo 6: Restaurar Backup
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent"
```

### Passo 7: Reiniciar
```bash
systemctl start seprom
```

