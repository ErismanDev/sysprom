# 🔧 Corrigir Acesso do Superusuário

## ⚠️ Problema
Superusuário não consegue fazer login após restore do backup.

## ✅ SOLUÇÃO

### Opção 1: Verificar e Recriar Superusuário

```bash
# Como seprom no servidor
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Verificar superusuários existentes
python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
superusers = User.objects.filter(is_superuser=True)
print(f"Superusuários encontrados: {superusers.count()}")
for user in superusers:
    print(f"- {user.username} (ID: {user.id}, Email: {user.email}, Ativo: {user.is_active})")
PYEOF

# Criar novo superusuário (se necessário)
python manage.py createsuperuser
```

### Opção 2: Resetar Senha do Superusuário Existente

```bash
# Como seprom no servidor
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Resetar senha do superusuário
python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
username = input("Digite o username do superusuário: ")
try:
    user = User.objects.get(username=username)
    if user.is_superuser:
        new_password = input("Digite a nova senha: ")
        user.set_password(new_password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ Senha do superusuário '{username}' resetada com sucesso!")
    else:
        print(f"⚠️ Usuário '{username}' não é superusuário")
except User.DoesNotExist:
    print(f"❌ Usuário '{username}' não encontrado")
PYEOF
```

### Opção 3: Criar Superusuário via Script (Automático)

```bash
# Como seprom no servidor
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

# Criar superusuário automaticamente
python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
import os

# Configurações
username = os.environ.get('SUPERUSER_USERNAME', 'admin')
email = os.environ.get('SUPERUSER_EMAIL', 'admin@cbmepi.gov.br')
password = os.environ.get('SUPERUSER_PASSWORD', 'admin123')

# Verificar se já existe
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.email = email
    user.save()
    print(f"✅ Superusuário '{username}' atualizado!")
else:
    User.objects.create_superuser(username, email, password)
    print(f"✅ Superusuário '{username}' criado!")
PYEOF
```

---

## 🚀 COMANDO RÁPIDO - Criar/Atualizar Superusuário

```bash
# Como root no servidor
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
username = 'admin'
email = 'admin@cbmepi.gov.br'
password = 'admin123'
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_active = True
    user.is_staff = True
    user.is_superuser = True
    user.email = email
    user.save()
    print(f'✅ Superusuário {username} atualizado!')
else:
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superusuário {username} criado!')
PYEOF
"
```

---

## 🔍 Verificar Todos os Superusuários

```bash
# Como seprom no servidor
su - seprom
cd /home/seprom/sepromcbmepi
source venv/bin/activate

python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
superusers = User.objects.filter(is_superuser=True)
print(f"\n=== SUPERUSUÁRIOS ({superusers.count()}) ===\n")
for user in superusers:
    print(f"Username: {user.username}")
    print(f"  ID: {user.id}")
    print(f"  Email: {user.email}")
    print(f"  Ativo: {user.is_active}")
    print(f"  Staff: {user.is_staff}")
    print(f"  Superuser: {user.is_superuser}")
    print()
PYEOF
```

---

## 🔧 Se o Problema Persistir

### Verificar Permissões no Banco

```bash
# Verificar se há problemas de permissão
su - postgres -c "psql sepromcbmepi -c \"
SELECT id, username, email, is_active, is_staff, is_superuser 
FROM auth_user 
WHERE is_superuser = true;
\""
```

### Verificar Logs de Autenticação

```bash
# Ver logs do Django quando tentar fazer login
sudo journalctl -u seprom -n 100 --no-pager | grep -i "login\|auth\|user"
```

---

## ✅ Testar Login

Após criar/atualizar o superusuário:

1. Acesse: http://64.23.185.235/admin/
2. Use as credenciais:
   - Username: `admin` (ou o que você definiu)
   - Password: `admin123` (ou o que você definiu)

---

## 🔐 Alterar Senha do Superusuário

Se precisar alterar a senha de um superusuário existente:

```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py changepassword admin"
```

