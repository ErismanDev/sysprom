#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Configuração do Supabase - Migrações e Superusuário
"""

import os
import sys
import django
import subprocess

print("=== Configurando Supabase ===")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')
django.setup()

from django.db import connection

try:
    # Testar conexão
    print("1. Testando conexão...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"   PostgreSQL: {version[0]}")
    
    print("2. Executando migrações...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'migrate', '--settings=sepromcbmepi.settings_supabase'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   Migrações executadas com sucesso!")
        print(result.stdout)
    else:
        print("   ERRO nas migrações:")
        print(result.stderr)
        exit(1)
    
    print("3. Criando superusuário...")
    # Criar superusuário interativamente
    result = subprocess.run([
        sys.executable, 'manage.py', 'createsuperuser', '--settings=sepromcbmepi.settings_supabase'
    ], input='admin\nadmin@supabase.com\nadmin123\nadmin123\n', text=True)
    
    if result.returncode == 0:
        print("   Superusuário criado com sucesso!")
    else:
        print("   ERRO ao criar superusuário:")
        print(result.stderr)
    
    print("4. Verificando configuração...")
    from django.contrib.auth.models import User
    user_count = User.objects.count()
    print(f"   Usuários no banco: {user_count}")
    
    print("\n=== Configuração Concluída! ===")
    print("Você pode agora usar o Supabase como banco de dados.")
    print("Para usar, execute: python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc() 