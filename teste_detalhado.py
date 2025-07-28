#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste detalhado para identificar o problema de codificação
"""

import psycopg2
import sys

print("=== Teste Detalhado ===")

# Parâmetros de conexão
params = {
    'host': 'db.vubnekyyfjcrswaufnla.supabase.co',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '2YXGdmXESoZAoPkO',
    'sslmode': 'require'
}

print("Parâmetros de conexão:")
for key, value in params.items():
    if key == 'password':
        print(f"  {key}: {'*' * len(value)}")
    else:
        print(f"  {key}: {value}")

print(f"\nTamanho do host: {len(params['host'])}")
print(f"Tamanho do password: {len(params['password'])}")

try:
    print("\nTentando conexão...")
    conn = psycopg2.connect(**params)
    print("SUCESSO!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    print(f"Query teste: {result}")
    
    cursor.close()
    conn.close()
    
except UnicodeDecodeError as e:
    print(f"UnicodeDecodeError: {e}")
    print(f"Posição do erro: {e.start}, {e.end}")
    print(f"Objeto causador: {e.object}")
    
except Exception as e:
    print(f"Outro erro: {e}")
    import traceback
    traceback.print_exc() 