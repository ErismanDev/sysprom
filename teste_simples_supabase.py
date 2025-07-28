#!/usr/bin/env python
"""
Teste simples de conexão com Supabase
"""

import os
import sys

# Configurar ambiente
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')

try:
    import django
    django.setup()
    
    from django.db import connection
    
    print("Testando conexao com Supabase...")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL: {version[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        count = cursor.fetchone()[0]
        print(f"Tabelas encontradas: {count}")
    
    print("Conexao OK!")
    
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc() 