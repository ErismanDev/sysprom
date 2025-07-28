#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste final de conexão com Supabase
"""

import os
import sys
import psycopg2

# Configurar encoding
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def testar_conexao():
    """Testa a conexão com o Supabase"""
    
    # Configurações de conexão
    config = {
        'host': 'db.vubnekyyfjcrswaufnla.supabase.co',
        'port': '5432',
        'database': 'postgres',
        'user': 'postgres',
        'password': '2YXGdmXESoZAoPkO',
        'sslmode': 'require'
    }
    
    print("=== Teste de Conexao com Supabase ===")
    print(f"Host: {config['host']}")
    print(f"Port: {config['port']}")
    print(f"Database: {config['database']}")
    print(f"User: {config['user']}")
    print(f"Password: {config['password']}")
    print(f"SSL Mode: {config['sslmode']}")
    print("=" * 40)
    
    try:
        print("Tentando conectar...")
        
        # Tentar conexão
        conn = psycopg2.connect(**config)
        print("SUCESSO: Conexao estabelecida!")
        
        # Testar query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        # Testar tabelas
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        count = cursor.fetchone()[0]
        print(f"Tabelas encontradas: {count}")
        
        cursor.close()
        conn.close()
        print("Conexao fechada com sucesso!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"ERRO OPERACIONAL: {e}")
        return False
    except psycopg2.Error as e:
        print(f"ERRO PSYCOPG2: {e}")
        return False
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sucesso = testar_conexao()
    if sucesso:
        print("\n=== RESULTADO: CONEXAO OK ===")
    else:
        print("\n=== RESULTADO: FALHA NA CONEXAO ===") 