#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de encoding para Supabase
"""

import os
import sys
import psycopg2

# Forçar encoding UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Configurar stdout para UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=== Teste de Encoding ===")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Default encoding: {sys.getdefaultencoding()}")
print(f"Filesystem encoding: {sys.getfilesystemencoding()}")

try:
    # Teste de conexão com encoding explícito
    print("\nTentando conexao com encoding explícito...")
    
    conn = psycopg2.connect(
        host='db.vubnekyyfjcrswaufnla.supabase.co',
        port='5432',
        database='postgres',
        user='postgres',
        password='2YXGdmXESoZAoPkO',
        sslmode='require',
        client_encoding='utf8'
    )
    
    print("SUCESSO: Conexao estabelecida!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"PostgreSQL: {version[0]}")
    
    cursor.close()
    conn.close()
    print("Conexao fechada!")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc() 