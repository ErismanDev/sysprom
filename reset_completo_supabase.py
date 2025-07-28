#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reset completo do Supabase
"""

import os
import sys
import django
import subprocess

print("=== Reset Completo do Supabase ===")

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
    
    print("2. Limpando completamente o banco...")
    with connection.cursor() as cursor:
        # Desabilitar foreign key checks temporariamente
        cursor.execute("SET session_replication_role = replica;")
        
        # Remover todas as tabelas do schema public
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        
        # Remover todas as sequências
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT sequencename FROM pg_sequences WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequencename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        
        # Reabilitar foreign key checks
        cursor.execute("SET session_replication_role = DEFAULT;")
        
        print("   Banco limpo completamente!")
    
    print("3. Resetando migrações...")
    result = subprocess.run([
        sys.executable, 'manage.py', 'migrate', '--settings=sepromcbmepi.settings_supabase', '--fake-initial'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   Migrações resetadas com sucesso!")
        print(result.stdout)
    else:
        print("   ERRO ao resetar migrações:")
        print(result.stderr)
    
    print("4. Executando migrações...")
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
    
    print("5. Criando superusuário...")
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
    
    print("6. Verificando configuração...")
    from django.contrib.auth.models import User
    user_count = User.objects.count()
    print(f"   Usuários no banco: {user_count}")
    
    print("\n=== Reset Completo Concluído! ===")
    print("Credenciais do admin:")
    print("  Usuário: admin")
    print("  Senha: admin123")
    print("  Email: admin@supabase.com")
    print("\nPara usar, execute: python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc() 