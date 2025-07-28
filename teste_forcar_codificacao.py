#!/usr/bin/env python
# -*- coding: latin1 -*-
"""
Teste forçando codificação Latin-1
"""

import os
import sys

# Forçar codificação antes de qualquer import
os.environ['PYTHONIOENCODING'] = 'latin1'
os.environ['PYTHONUTF8'] = '0'

# Configurar stdout para Latin-1
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='latin1')

print("=== Teste com Codificação Forçada ===")

try:
    import psycopg2
    print("psycopg2 importado com sucesso")
    
    # Parâmetros de conexão
    params = {
        'host': 'db.vubnekyyfjcrswaufnla.supabase.co',
        'port': '5432',
        'database': 'postgres',
        'user': 'postgres',
        'password': '2YXGdmXESoZAoPkO',
        'sslmode': 'require'
    }
    
    print("Tentando conexao...")
    conn = psycopg2.connect(**params)
    print("SUCESSO!")
    
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