#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simples para criar backup completo do banco de dados Django
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

# Nome do arquivo de backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup_sepromcbmepi_{timestamp}.json"

print(f"Criando backup completo...")
print(f"Arquivo: {backup_file}")

# Verificar dados antes
from django.contrib.auth.models import User
from militares.models import Militar
print(f"Usuarios no banco: {User.objects.count()}")
print(f"Militares no banco: {Militar.objects.count()}")

# Criar backup usando subprocess para evitar problemas de encoding
import subprocess
import json

try:
    # Usar subprocess para executar dumpdata diretamente
    result = subprocess.run(
        ['python', 'manage.py', 'dumpdata', '--indent', '2', '--natural-foreign', '--natural-primary'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=os.getcwd()
    )
    
    if result.returncode == 0:
        # Salvar em arquivo
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        # Verificar tamanho
        file_size = os.path.getsize(backup_file)
        size_mb = file_size / (1024 * 1024)
        
        print(f"\nBackup criado com sucesso!")
        print(f"Tamanho: {size_mb:.2f} MB")
        print(f"Local: {os.path.abspath(backup_file)}")
        
        # Verificar conteúdo
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"Total de objetos no backup: {len(data)}")
                    # Contar militares e usuários
                    militares = sum(1 for item in data if item.get('model') == 'militares.militar')
                    usuarios = sum(1 for item in data if item.get('model') == 'auth.user')
                    print(f"Militares no backup: {militares}")
                    print(f"Usuarios no backup: {usuarios}")
                    if militares > 0 and usuarios > 0:
                        print("✅ Backup contem dados!")
                    else:
                        print("⚠️ Aviso: Backup pode estar vazio!")
        except Exception as e:
            print(f"Erro ao verificar conteudo: {e}")
    else:
        print(f"Erro ao criar backup:")
        print(result.stderr)
        sys.exit(1)
        
except Exception as e:
    print(f"Erro ao criar backup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\nProximo passo: Envie este arquivo via WinSCP para:")
print(f"   /home/seprom/sepromcbmepi/")

