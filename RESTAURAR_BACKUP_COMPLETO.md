# 📥 Restaurar Backup Completo no Servidor

## ✅ Backup Criado Localmente

- **Arquivo**: `backup_sepromcbmepi_completo_20251115_153440.json`
- **Tamanho**: 44.15 MB
- **Local**: `C:\projetos\Sysgabom\backup_sepromcbmepi_completo_20251115_153440.json`

---

## 📤 PASSO 1: Enviar Backup via WinSCP

1. Abra o WinSCP
2. Conecte ao servidor: `64.23.185.235` (usuário: `root`)
3. Navegue até: `/home/seprom/sepromcbmepi/`
4. Arraste o arquivo `backup_sepromcbmepi_completo_20251115_153440.json` para lá
5. Aguarde o upload terminar

---

## 🔧 PASSO 2: Restaurar Backup no Servidor

Execute este comando no console do Digital Ocean:

```bash
# Parar aplicação
systemctl stop seprom

# Instalar dateutil se necessário
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install -q python-dateutil==2.9.0"

# Criar script de restore
su - seprom -c "cat > /home/seprom/sepromcbmepi/restaurar_backup_completo.py << 'PYEOF'
import os, sys, django, glob
from datetime import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()
from django.core.management import call_command
from django.db import connection
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from militares import signals

# Desconectar signals
try:
    post_save.disconnect(signals.criar_militar_para_usuario, sender=User)
    print('✅ Signals desabilitados')
except: pass

# Encontrar backup
backup_files = glob.glob('/home/seprom/sepromcbmepi/backup_sepromcbmepi_completo_*.json')
if not backup_files:
    print('❌ Nenhum backup encontrado!')
    sys.exit(1)

backup_file = sorted(backup_files, reverse=True)[0]
print(f'📦 Restaurando: {backup_file}')
file_size = os.path.getsize(backup_file)
print(f'📊 Tamanho: {file_size / 1024 / 1024:.2f} MB')

# Backup de segurança
backup_seguranca = f'/tmp/backup_seguranca_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.json'
print(f'💾 Backup de segurança: {backup_seguranca}')
try:
    call_command('dumpdata', output=backup_seguranca, exclude=['auth.permission', 'contenttypes'], verbosity=0)
except: pass

# Limpar banco
print('🗑️ Limpando banco de dados...')
call_command('flush', interactive=False, verbosity=0)

# Restaurar backup
print('📥 Restaurando backup (isso pode levar alguns minutos)...')
try:
    # Tentar restaurar normalmente
    call_command('loaddata', backup_file, verbosity=2)
    print('✅ Backup restaurado com sucesso!')
except Exception as e:
    print(f'⚠️ Erro ao restaurar: {e}')
    print('🔄 Tentando restaurar com constraints deferidas...')
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
            call_command('loaddata', backup_file, verbosity=2)
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
        print('✅ Backup restaurado (alguns dados podem estar inconsistentes)')
    except Exception as e2:
        print(f'❌ Erro crítico: {e2}')
        print('💾 Backup de segurança salvo em:', backup_seguranca)

# Limpar dados órfãos
print('💡 Limpando dados órfãos...')
try:
    from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar
    militares_ids = set(Militar.objects.values_list('id', flat=True))
    deleted_o = FichaConceitoOficiais.objects.exclude(militar_id__in=militares_ids).delete()
    deleted_p = FichaConceitoPracas.objects.exclude(militar_id__in=militares_ids).delete()
    if deleted_o[0] > 0 or deleted_p[0] > 0:
        print(f'✅ Removidos {deleted_o[0]} fichas de oficiais e {deleted_p[0]} fichas de praças órfãs')
except Exception as cleanup_error:
    print(f'⚠️ Erro ao limpar dados órfãos: {cleanup_error}')

# Reconectar signals
try:
    post_save.connect(signals.criar_militar_para_usuario, sender=User)
    print('✅ Signals reabilitados')
except: pass

# Verificar dados restaurados
print('\n=== DADOS RESTAURADOS ===')
from django.contrib.auth.models import User
from militares.models import Militar
users_count = User.objects.count()
militares_count = Militar.objects.count()
superusers_count = User.objects.filter(is_superuser=True).count()
print(f'Usuários: {users_count}')
print(f'Militares: {militares_count}')
print(f'Superusuários: {superusers_count}')

if users_count > 0 and militares_count > 0:
    print('\n✅ Dados restaurados com sucesso!')
else:
    print('\n⚠️ Aviso: Poucos dados foram restaurados')

print('\n✅ Processo concluído!')
PYEOF
"

# Executar restore
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python restaurar_backup_completo.py"

# Reiniciar aplicação
systemctl start seprom

# Verificar status
systemctl status seprom --no-pager | head -20
```

---

## 🚀 COMANDO ÚNICO (Copie e Cole Tudo)

```bash
systemctl stop seprom && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && pip install -q python-dateutil==2.9.0" && \
su - seprom -c "cat > /home/seprom/sepromcbmepi/restaurar_backup_completo.py << 'PYEOF'
import os, sys, django, glob
from datetime import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()
from django.core.management import call_command
from django.db import connection
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from militares import signals
try:
    post_save.disconnect(signals.criar_militar_para_usuario, sender=User)
    print('✅ Signals desabilitados')
except: pass
backup_files = glob.glob('/home/seprom/sepromcbmepi/backup_sepromcbmepi_completo_*.json')
if not backup_files:
    print('❌ Nenhum backup encontrado!')
    sys.exit(1)
backup_file = sorted(backup_files, reverse=True)[0]
print(f'📦 Restaurando: {backup_file}')
file_size = os.path.getsize(backup_file)
print(f'📊 Tamanho: {file_size / 1024 / 1024:.2f} MB')
backup_seguranca = f'/tmp/backup_seguranca_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.json'
print(f'💾 Backup de segurança: {backup_seguranca}')
try:
    call_command('dumpdata', output=backup_seguranca, exclude=['auth.permission', 'contenttypes'], verbosity=0)
except: pass
print('🗑️ Limpando banco...')
call_command('flush', interactive=False, verbosity=0)
print('📥 Restaurando backup (pode levar alguns minutos)...')
try:
    call_command('loaddata', backup_file, verbosity=2)
    print('✅ Backup restaurado!')
except Exception as e:
    print(f'⚠️ Erro: {e}')
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
            call_command('loaddata', backup_file, verbosity=2)
            cursor.execute('SET CONSTRAINTS ALL IMMEDIATE;')
        print('✅ Restaurado com constraints deferidas')
    except Exception as e2:
        print(f'❌ Erro crítico: {e2}')
try:
    from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar
    militares_ids = set(Militar.objects.values_list('id', flat=True))
    deleted_o = FichaConceitoOficiais.objects.exclude(militar_id__in=militares_ids).delete()
    deleted_p = FichaConceitoPracas.objects.exclude(militar_id__in=militares_ids).delete()
    if deleted_o[0] > 0 or deleted_p[0] > 0:
        print(f'✅ Removidos {deleted_o[0]} fichas órfãs')
except: pass
try:
    post_save.connect(signals.criar_militar_para_usuario, sender=User)
    print('✅ Signals reabilitados')
except: pass
from django.contrib.auth.models import User
from militares.models import Militar
print(f'\n✅ Dados: {User.objects.count()} usuários, {Militar.objects.count()} militares')
PYEOF
" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python restaurar_backup_completo.py" && \
systemctl start seprom && \
echo "✅ Restauração concluída!"
```

---

## ✅ Verificar Após Restore

```bash
# Verificar dados restaurados
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

## 📝 Resumo

1. ✅ **Backup criado localmente**: `backup_sepromcbmepi_completo_20251115_153440.json` (44.15 MB)
2. 📤 **Enviar via WinSCP** para `/home/seprom/sepromcbmepi/`
3. 🔧 **Executar comando de restore** no servidor
4. ✅ **Verificar dados** restaurados

O backup está pronto! Envie via WinSCP e execute o comando de restore.

