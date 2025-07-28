#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste com versão mais antiga do psycopg2
"""

import psycopg2

print("=== Teste com psycopg2 2.9.7 ===")

try:
    print("Tentando conexao...")
    conn = psycopg2.connect(
        host='db.vubnekyyfjcrswaufnla.supabase.co',
        port='5432',
        database='postgres',
        user='postgres',
        password='2YXGdmXESoZAoPkO',
        sslmode='require'
    )
    
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