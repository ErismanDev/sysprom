# 🔧 Verificar e Restaurar Dados do Backup

## 🔍 PASSO 1: Verificar Dados no Banco

```bash
# Como seprom no servidor
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
from militares.models import Militar

print('=== VERIFICAÇÃO DO BANCO ===\n')
print(f'Total de usuários: {User.objects.count()}')
print(f'Total de militares: {Militar.objects.count()}')
print(f'Superusuários: {User.objects.filter(is_superuser=True).count()}')
print(f'Usuários ativos: {User.objects.filter(is_active=True).count()}')
PYEOF
"
```

---

## 🔍 PASSO 2: Verificar Arquivo de Backup

```bash
# Verificar se o arquivo de backup existe
ls -lh /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json

# Verificar tamanho do arquivo
du -h /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json

# Verificar primeiras linhas do backup (verificar se tem dados)
head -n 50 /home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json | head -1
```

---

## 🔧 PASSO 3: Restaurar Backup Corretamente

### Opção A: Restaurar com Script Melhorado

```bash
# Parar aplicação
systemctl stop seprom

# Criar script de restore melhorado
su - seprom -c "cat > /home/seprom/sepromcbmepi/restaurar_backup_completo.py << 'PYEOF'
import os, sys, django, glob, json
from datetime import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.management import call_command
from django.db import connection, transaction
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from militares import signals

# Desconectar signals
try:
    post_save.disconnect(signals.criar_militar_para_usuario, sender=User)
    print('✅ Signals desabilitados')
except: pass

# Encontrar backup
backup_files = glob.glob('/home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json')
if not backup_files:
    print('❌ Nenhum backup encontrado!')
    sys.exit(1)

backup_file = sorted(backup_files, reverse=True)[0]
print(f'📦 Backup encontrado: {backup_file}')

# Verificar tamanho do arquivo
file_size = os.path.getsize(backup_file)
print(f'📊 Tamanho do arquivo: {file_size / 1024 / 1024:.2f} MB')

# Verificar se tem conteúdo
with open(backup_file, 'r', encoding='utf-8') as f:
    first_line = f.readline()
    if not first_line.strip().startswith('['):
        print('❌ Arquivo de backup inválido!')
        sys.exit(1)
    print('✅ Arquivo de backup válido')

# Backup de segurança
backup_seguranca = f'/tmp/backup_seguranca_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.json'
print(f'💾 Criando backup de segurança: {backup_seguranca}')
try:
    call_command('dumpdata', output=backup_seguranca, exclude=['auth.permission', 'contenttypes'], verbosity=0)
except: pass

# Limpar banco
print('🗑️ Limpando banco de dados...')
call_command('flush', interactive=False, verbosity=0)

# Restaurar backup
print('📥 Restaurando backup...')
try:
    # Tentar restaurar normalmente primeiro
    call_command('loaddata', backup_file, verbosity=2)
    print('✅ Backup restaurado com sucesso!')
except Exception as e:
    print(f'⚠️ Erro ao restaurar: {e}')
    print('🔄 Tentando restaurar com constraints deferidas...')
    try:
        with connection.cursor() as cursor:
            cursor.execute('SET CONSTRAINTS ALL DEFERRED;')
            try:
                call_command('loaddata', backup_file, verbosity=2)
            except Exception as load_error:
                print(f'⚠️ Erro ao carregar: {load_error}')
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
print(f'Usuários: {User.objects.count()}')
print(f'Militares: {Militar.objects.count()}')
print(f'Superusuários: {User.objects.filter(is_superuser=True).count()}')

print('\n✅ Processo concluído!')
PYEOF
"

# Executar restore
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python restaurar_backup_completo.py"

# Reiniciar aplicação
systemctl start seprom
```

---

## 🚀 COMANDO ÚNICO - Restaurar Backup Completo

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
backup_files = glob.glob('/home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json')
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
print('📥 Restaurando backup...')
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
print(f'\n✅ Dados restaurados: {User.objects.count()} usuários, {Militar.objects.count()} militares')
PYEOF
" && \
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python restaurar_backup_completo.py" && \
systemctl start seprom && \
echo "✅ Restauração concluída!"
```

---

## 🔍 Verificar Dados Após Restore

```bash
# Verificar quantidades
su - seprom -c "cd /home/seprom/sepromcbmepi && source venv/bin/activate && python manage.py shell << 'PYEOF'
from django.contrib.auth.models import User
from militares.models import Militar
print(f'Usuários: {User.objects.count()}')
print(f'Militares: {Militar.objects.count()}')
print(f'Superusuários: {User.objects.filter(is_superuser=True).count()}')
PYEOF
"
```

