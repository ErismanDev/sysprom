#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste usando string de conexão
"""

import psycopg2

print("Teste com string de conexao...")

# String de conexão
connection_string = "postgresql://postgres:2YXGdmXESoZAoPkO@db.vubnekyyfjcrswaufnla.supabase.co:5432/postgres?sslmode=require"

try:
    print("Conectando...")
    conn = psycopg2.connect(connection_string)
    print("SUCESSO!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"Query result: {result}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERRO: {e}") 