# ✅ Restaurar Backup - Solução Final

## ⚠️ Problema
Tabelas não existem após flush. Precisa executar migrações completas.

## 🚀 SOLUÇÃO DEFINITIVA

### Comando Único Completo

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --run-syncdb" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent" && \
systemctl start seprom && \
echo "Backup restaurado!"
```

---

## 🔧 OU: Passo a Passo (Mais Seguro)

### Passo 1: Parar Aplicação
```bash
systemctl stop seprom
```

### Passo 2: Limpar Banco
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput"
```

### Passo 3: Executar TODAS as Migrações
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate --run-syncdb"
```

### Passo 4: Verificar Tabelas Criadas
```bash
su - postgres -c "psql sepromcbmepi -c '\dt' | head -30"
```

### Passo 5: Restaurar Backup (Ignorando Erros de Tabelas Inexistentes)
```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json --ignorenonexistent"
```

### Passo 6: Reiniciar
```bash
systemctl start seprom
```

---

## 🔍 Verificar Dados

```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell -c \"from django.contrib.auth.models import User; from militares.models import Militar; print('Usuarios:', User.objects.count()); print('Militares:', Militar.objects.count())\""
```
