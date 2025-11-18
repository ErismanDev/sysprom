# ✅ Criar Superusuário Específico

## 🔐 Credenciais
- **CPF/Username**: `33888647304`
- **Senha**: `Erisman@193`

## 🚀 Comandos para Executar no Servidor

### Opção 1: Usando Script Python

```bash
# Enviar script para o servidor via WinSCP primeiro
# Depois executar:

su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python criar_superusuario_especifico.py
EOF
```

---

### Opção 2: Criar Diretamente via Django Shell

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate

python manage.py shell << 'PYEOF'
import os
os.environ['DISABLE_SIGNALS'] = '1'
from django.contrib.auth.models import User

CPF = '33888647304'
SENHA = 'Erisman@193'
EMAIL = 'admin@cbmepi.gov.br'
FIRST_NAME = 'Admin'
LAST_NAME = 'Sistema'

# Verificar se já existe
if User.objects.filter(username=CPF).exists():
    user = User.objects.get(username=CPF)
    user.set_password(SENHA)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.email = EMAIL
    user.first_name = FIRST_NAME
    user.last_name = LAST_NAME
    user.save()
    print(f"✅ Usuário existente atualizado para superusuário!")
else:
    user = User.objects.create_user(
        username=CPF,
        email=EMAIL,
        password=SENHA,
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        is_superuser=True,
        is_staff=True,
        is_active=True
    )
    print(f"✅ Superusuário criado com sucesso!")

print(f"\n📋 Username: {user.username}")
print(f"📋 Email: {user.email}")
print(f"📋 Nome: {user.get_full_name()}")
print(f"📋 Superusuário: {user.is_superuser}")
PYEOF
EOF
```

---

### Opção 3: Comando Único (Mais Simples)

```bash
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && DISABLE_SIGNALS=1 python manage.py shell -c \"from django.contrib.auth.models import User; user, created = User.objects.get_or_create(username='33888647304', defaults={'email': 'admin@cbmepi.gov.br', 'first_name': 'Admin', 'last_name': 'Sistema', 'is_superuser': True, 'is_staff': True, 'is_active': True}); user.set_password('Erisman@193'); user.save(); print('✅ Superusuário criado!' if created else '✅ Superusuário atualizado!')\""
```

---

## ✅ Verificar se Foi Criado

```bash
su - seprom << 'EOF'
cd /home/seprom/sepromcbmepi
source venv/bin/activate
python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='33888647304'); print(f'Username: {u.username}'); print(f'Email: {u.email}'); print(f'Superusuário: {u.is_superuser}'); print(f'Staff: {u.is_staff}'); print(f'Ativo: {u.is_active}')"
EOF
```

