#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste com diferentes codificações para resolver UnicodeDecodeError
"""

import os
import sys
import psycopg2

# Forçar codificação do sistema
os.environ['PYTHONIOENCODING'] = 'latin1'
os.environ['PYTHONUTF8'] = '0'

print("=== Teste com Codificação Corrigida ===")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Default encoding: {sys.getdefaultencoding()}")

# Lista de codificações para tentar
codificacoes = ['latin1', 'cp1252', 'iso-8859-1', 'utf-8']

for encoding in codificacoes:
    print(f"\n--- Tentando codificação: {encoding} ---")
    
    try:
        # Configurar ambiente para a codificação
        os.environ['PYTHONIOENCODING'] = encoding
        
        # Tentar conexão
        conn = psycopg2.connect(
            host='db.vubnekyyfjcrswaufnla.supabase.co',
            port='5432',
            database='postgres',
            user='postgres',
            password='2YXGdmXESoZAoPkO',
            sslmode='require'
        )
        
        print(f"SUCESSO com codificação {encoding}!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"PostgreSQL: {version[0]}")
        
        cursor.close()
        conn.close()
        print("Conexao fechada!")
        
        # Se chegou aqui, encontrou a codificação correta
        break
        
    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError com {encoding}: {e}")
        continue
    except Exception as e:
        print(f"Outro erro com {encoding}: {e}")
        continue

print("\n=== Fim do teste ===") 