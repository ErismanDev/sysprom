# ✅ Criar Superusuário - Comando Direto

## 🚀 Execute Este Comando no Servidor

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
print(f"📋 Staff: {user.is_staff}")
print(f"📋 Ativo: {user.is_active}")
PYEOF
EOF
```

