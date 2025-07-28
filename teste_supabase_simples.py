#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples de conexão com Supabase sem Django
"""

import psycopg2
import sys

print("Iniciando teste de conexao...")

try:
    # Configurações
    host = 'db.vubnekyyfjcrswaufnla.supabase.co'
    port = 5432
    database = 'postgres'
    user = 'postgres'
    password = '2YXGdmXESoZAoPkO'
    
    print(f"Conectando a {host}:{port}")
    print(f"Database: {database}")
    print(f"User: {user}")
    
    # Conexão
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        sslmode='require'
    )
    
    print("Conexao estabelecida!")
    
    # Teste simples
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"Teste de query: {result}")
    
    cursor.close()
    conn.close()
    print("Conexao fechada!")
    print("SUCESSO!")
    
except Exception as e:
    print(f"ERRO: {e}")
    print("FALHA!")
    sys.exit(1) 