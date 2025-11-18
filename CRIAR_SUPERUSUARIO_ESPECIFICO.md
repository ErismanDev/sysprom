# 🔧 Criar Superusuário Específico

## ✅ COMANDO PARA CRIAR SUPERUSUÁRIO

```bash
# Como root no servidor
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User

username = '33888647304'
email = '33888647304@cbmepi.gov.br'
password = 'Erisman@193'

# Verificar se já existe
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

print(f'\n=== CREDENCIAIS ===')
print(f'Username: {username}')
print(f'Password: {password}')
print(f'URL: http://64.23.185.235/admin/')
PYEOF
"
```

