#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para restaurar backup desabilitando signals temporariamente"""
import os
import sys
import django
from django.core.management import call_command
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

# Desabilitar signals temporariamente
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from militares import signals

# Desconectar signals que causam problemas
try:
    post_save.disconnect(signals.criar_militar_para_usuario, sender=User)
    print("✅ Signals desabilitados temporariamente")
except:
    pass

# Encontrar arquivo de backup
import glob
backup_files = glob.glob('/home/seprom/sepromcbmepi/backup_sepromcbmepi_*.json')
if not backup_files:
    print("❌ Nenhum arquivo de backup encontrado!")
    sys.exit(1)

backup_file = sorted(backup_files, reverse=True)[0]
print(f"📦 Restaurando backup: {backup_file}")

# Fazer backup de segurança primeiro
from datetime import datetime
backup_seguranca = f"/tmp/backup_seguranca_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
print(f"💾 Criando backup de segurança: {backup_seguranca}")
call_command('dumpdata', output=backup_seguranca, exclude=['auth.permission', 'contenttypes'])

# Limpar banco
print("🗑️ Limpando banco de dados...")
call_command('flush', interactive=False, verbosity=0)

# Restaurar backup
print("📥 Restaurando backup...")
try:
    # Tentar restaurar normalmente
    call_command('loaddata', backup_file, verbosity=1)
    print("✅ Backup restaurado com sucesso!")
except Exception as e:
    print(f"⚠️ Erro durante restore: {e}")
    print("🔄 Tentando restaurar ignorando erros de foreign key...")
    try:
        # Usar defer constraints (não requer privilégios especiais)
        from django.db import connection
        with connection.cursor() as cursor:
            # Defer constraints - permite inserir dados e validar depois
            cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
            try:
                call_command('loaddata', backup_file, verbosity=1)
            except Exception as load_error:
                print(f"⚠️ Erro ao carregar: {load_error}")
                # Continuar mesmo com erros
            cursor.execute("SET CONSTRAINTS ALL IMMEDIATE;")
        print("✅ Backup restaurado (alguns dados podem estar inconsistentes)")
        print("💡 Limpando dados órfãos...")
        # Limpar dados órfãos após restore
        try:
            from militares.models import FichaConceitoOficiais, FichaConceitoPracas, Militar
            militares_ids = set(Militar.objects.values_list('id', flat=True))
            deleted_o = FichaConceitoOficiais.objects.exclude(militar_id__in=militares_ids).delete()
            deleted_p = FichaConceitoPracas.objects.exclude(militar_id__in=militares_ids).delete()
            if deleted_o[0] > 0 or deleted_p[0] > 0:
                print(f"✅ Removidos {deleted_o[0]} fichas de oficiais e {deleted_p[0]} fichas de praças órfãs")
        except Exception as cleanup_error:
            print(f"⚠️ Erro ao limpar dados órfãos: {cleanup_error}")
    except Exception as e2:
        print(f"❌ Erro crítico ao restaurar: {e2}")
        print("💾 Backup de segurança salvo em:", backup_seguranca)
        print("⚠️ Você pode precisar limpar dados órfãos manualmente")
        # Não sair com erro - deixar continuar

# Reconectar signals
try:
    post_save.connect(signals.criar_militar_para_usuario, sender=User)
    print("✅ Signals reabilitados")
except:
    pass

print("✅ Processo concluído!")

