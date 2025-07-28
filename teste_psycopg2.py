#!/usr/bin/env python
"""
Teste direto com psycopg2
"""

import psycopg2

# Configurações de conexão
config = {
    'host': 'db.vubnekyyfjcrswaufnla.supabase.co',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': '2YXGdmXESoZAoPkO'
}

print("Testando conexao direta com psycopg2...")
print(f"Host: {config['host']}")
print(f"Port: {config['port']}")
print(f"Database: {config['database']}")
print(f"User: {config['user']}")
print(f"Password: {config['password']}")

try:
    # Tentar conexão
    print("Tentando conectar...")
    conn = psycopg2.connect(**config)
    print("Conexao estabelecida com sucesso!")
    
    # Testar query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL: {version[0]}")
    
    cursor.close()
    conn.close()
    print("Conexao fechada com sucesso!")
    
except Exception as e:
    print(f"Erro na conexao: {e}")
    import traceback
    traceback.print_exc()

print("Fim do teste") 