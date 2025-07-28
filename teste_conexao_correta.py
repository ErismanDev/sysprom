#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste com as informações corretas do Supabase
"""

import psycopg2

print("=== Teste com Informações Corretas do Supabase ===")

# Informações corretas
host = "aws-0-sa-east-1.pooler.supabase.com"
port = 6543
database = "postgres"
user = "postgres.vubnekyyfjcrswaufnla"
password = "2YXGdmXESoZAoPkO"

print(f"Host: {host}")
print(f"Port: {port}")
print(f"Database: {database}")
print(f"User: {user}")
print(f"Password: {'*' * len(password)}")

try:
    print("\nTentando conexão...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        sslmode='require'
    )
    
    print("SUCESSO: Conexão estabelecida!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"PostgreSQL: {version[0]}")
    
    cursor.close()
    conn.close()
    print("Conexão fechada!")
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc() 