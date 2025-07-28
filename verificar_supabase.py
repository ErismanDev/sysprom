#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verificação das informações do Supabase
"""

import socket
import psycopg2

print("=== Verificação do Supabase ===")

# Host atual
host = "db.vubnekyyfjcrswaufnla.supabase.co"
port = 5432

print(f"Host: {host}")
print(f"Port: {port}")

# Teste de resolução DNS
try:
    print(f"\nTentando resolver DNS para {host}...")
    ip = socket.gethostbyname(host)
    print(f"IP resolvido: {ip}")
except socket.gaierror as e:
    print(f"ERRO DNS: {e}")
    print("O host não pode ser resolvido. Verifique se:")
    print("1. O nome do host está correto")
    print("2. Você tem conexão com a internet")
    print("3. O Supabase está ativo")
    exit(1)

# Teste de conectividade TCP
try:
    print(f"\nTestando conectividade TCP para {host}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((host, port))
    sock.close()
    
    if result == 0:
        print("SUCESSO: Porta 5432 está acessível!")
    else:
        print(f"ERRO: Porta 5432 não está acessível (código: {result})")
        print("Verifique se:")
        print("1. O Supabase está ativo")
        print("2. A porta 5432 está correta")
        print("3. Não há firewall bloqueando")
        exit(1)
        
except Exception as e:
    print(f"ERRO de conectividade: {e}")
    exit(1)

# Teste de conexão PostgreSQL
try:
    print(f"\nTestando conexão PostgreSQL...")
    conn = psycopg2.connect(
        host=host,
        port=port,
        database='postgres',
        user='postgres',
        password='2YXGdmXESoZAoPkO',
        sslmode='require'
    )
    
    print("SUCESSO: Conexão PostgreSQL estabelecida!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT version()")
    version = cursor.fetchone()
    print(f"PostgreSQL: {version[0]}")
    
    cursor.close()
    conn.close()
    print("Conexão fechada!")
    
except Exception as e:
    print(f"ERRO PostgreSQL: {e}")
    print("\nPossíveis soluções:")
    print("1. Verifique se a senha está correta")
    print("2. Verifique se o usuário 'postgres' existe")
    print("3. Verifique se o banco 'postgres' existe")
    print("4. Verifique as configurações SSL") 