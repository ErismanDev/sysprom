# ✅ Restaurar Backup Corretamente

## ⚠️ Problema
O banco foi limpo mas as tabelas não existem. Precisa executar migrações primeiro.

## 🚀 SOLUÇÃO CORRETA

### Passo 1: Parar Aplicação

```bash
systemctl stop seprom
```

### Passo 2: Limpar Banco e Criar Tabelas

```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput && python manage.py migrate"
```

### Passo 3: Restaurar Backup

```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json"
```

### Passo 4: Reiniciar Aplicação

```bash
systemctl start seprom
```

---

## 🚀 COMANDO ÚNICO (Corrigido)

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install -q python-dateutil==2.9.0" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py migrate" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json" && \
systemctl start seprom && \
echo "✅ Backup restaurado!"
```

---

## 🔍 Verificar Dados

```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
from militares.models import Militar
print(f'Usuários: {User.objects.count()}')
print(f'Militares: {Militar.objects.count()}')
print(f'Superusuários: {User.objects.filter(is_superuser=True).count()}')
PYEOF
"
```

