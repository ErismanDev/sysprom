#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste Django com Supabase
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')
django.setup()

from django.db import connection
from django.contrib.auth.models import User

print("=== Teste Django com Supabase ===")

try:
    # Testar conexão
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"PostgreSQL: {version[0]}")
    
    print("SUCESSO: Conexão Django estabelecida!")
    
    # Testar modelo User
    user_count = User.objects.count()
    print(f"Usuários no banco: {user_count}")
    
    # Listar alguns usuários
    users = User.objects.all()[:5]
    print("\nPrimeiros 5 usuários:")
    for user in users:
        print(f"  - {user.username} ({user.email})")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc() 