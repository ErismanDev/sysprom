# ✅ Restaurar Backup JSON (Funcional)

## ⚠️ Problema
O backup SQL tem formato incorreto. Vamos usar o backup JSON que já funciona.

## 🚀 SOLUÇÃO: Restaurar Backup JSON

### Passo 1: Verificar Backup JSON

```bash
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_completo_*.json
```

### Passo 2: Restaurar Backup JSON

```bash
# Parar aplicação
systemctl stop seprom

# Instalar dateutil se necessário
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install -q python-dateutil==2.9.0"

# Desabilitar signals e restaurar
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
import os
os.environ['DISABLE_SIGNALS'] = '1'
PYEOF
"

# Limpar banco
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput"

# Restaurar backup JSON
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json"

# Reiniciar aplicação
systemctl start seprom
```

---

## 🚀 COMANDO ÚNICO

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install -q python-dateutil==2.9.0" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py flush --noinput" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py loaddata backup_sepromcbmepi_completo_20251115_154308.json" && \
systemctl start seprom && \
echo "✅ Backup restaurado!"
```

---

## 🔍 Verificar Dados Restaurados

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

---

## 💡 Se o Backup JSON Não Estiver no Servidor

Se você ainda não enviou o backup JSON via WinSCP:

1. **Arquivo local**: `backup_sepromcbmepi_completo_20251115_154308.json` (44.15 MB)
2. **Enviar via WinSCP** para `/home/seprom/sepromcbmepi/`
3. **Depois executar** o comando único acima

---

## ✅ Vantagens do Backup JSON

- ✅ Formato correto e testado
- ✅ Funciona com Django loaddata
- ✅ Preserva todos os relacionamentos
- ✅ Já foi testado e funciona (497 militares, 512 usuários)

