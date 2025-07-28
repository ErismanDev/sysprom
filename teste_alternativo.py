#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste alternativo de conexão
"""

import subprocess
import sys

print("Teste alternativo usando subprocess...")

# Comando para testar conexão
cmd = [
    sys.executable, "-c",
    "import psycopg2; conn = psycopg2.connect(host='db.vubnekyyfjcrswaufnla.supabase.co', port=5432, database='postgres', user='postgres', password='2YXGdmXESoZAoPkO', sslmode='require'); print('OK'); conn.close()"
]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print("SUCESSO!")
        print(result.stdout)
    else:
        print("ERRO!")
        print(result.stderr)
        
except Exception as e:
    print(f"ERRO: {e}") 