#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Limpar e configurar Supabase do zero
"""

import os
import sys
import django
import subprocess

print("=== Limpando e Configurando Supabase ===")

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
    
    print("2. Limpando banco...")
    # Listar todas as tabelas
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'django_%'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   Encontradas {len(tables)} tabelas para remover:")
            for table in tables:
                print(f"     - {table[0]}")
            
            # Remover tabelas
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}" CASCADE')
                print(f"     Removida: {table[0]}")
        else:
            print("   Nenhuma tabela encontrada para remover")
    
    print("3. Executando migrações...")
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
    
    print("4. Criando superusuário...")
    # Criar superusuário não-interativo
    result = subprocess.run([
        sys.executable, 'manage.py', 'createsuperuser', 
        '--settings=sepromcbmepi.settings_supabase',
        '--noinput',
        '--username=admin',
        '--email=admin@supabase.com'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   Superusuário criado com sucesso!")
        # Definir senha
        from django.contrib.auth.models import User
        user = User.objects.get(username='admin')
        user.set_password('admin123')
        user.save()
        print("   Senha definida: admin123")
    else:
        print("   ERRO ao criar superusuário:")
        print(result.stderr)
    
    print("5. Verificando configuração...")
    from django.contrib.auth.models import User
    user_count = User.objects.count()
    print(f"   Usuários no banco: {user_count}")
    
    print("\n=== Configuração Concluída! ===")
    print("Credenciais do admin:")
    print("  Usuário: admin")
    print("  Senha: admin123")
    print("  Email: admin@supabase.com")
    print("\nPara usar, execute: python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc() 