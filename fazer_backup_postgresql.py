#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar backup PostgreSQL usando pg_dump
"""
import os
import sys
import subprocess
from datetime import datetime

# Configurações do banco
DB_NAME = "sepromcbmepi"
DB_USER = "postgres"
DB_PASSWORD = "11322361"  # Será usado via variável de ambiente PGPASSWORD
DB_HOST = "localhost"
DB_PORT = "5432"

# Nome do arquivo de backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup_sepromcbmepi_{timestamp}.sql"

print("Criando backup PostgreSQL...")
print(f"Arquivo: {backup_file}")

# Tentar encontrar pg_dump
pg_dump_path = None
possible_paths = [
    'pg_dump',  # No PATH
    r'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\14\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\13\bin\pg_dump.exe',
    r'C:\Program Files\PostgreSQL\12\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\14\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\13\bin\pg_dump.exe',
    r'C:\Program Files (x86)\PostgreSQL\12\bin\pg_dump.exe',
]

for path in possible_paths:
    try:
        result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            pg_dump_path = path
            print(f"pg_dump encontrado: {result.stdout.strip()}")
            break
    except (FileNotFoundError, subprocess.TimeoutExpired):
        continue

if not pg_dump_path:
    print("ERRO: pg_dump nao encontrado!")
    print("Locais verificados:")
    for path in possible_paths:
        print(f"  - {path}")
    print("\nInstale o PostgreSQL Client Tools ou adicione ao PATH")
    print("Ou ajuste o caminho no script")
    sys.exit(1)

# Criar backup
try:
    # Comando pg_dump
    # -F p = formato texto (SQL)
    # -b = incluir blobs
    # -v = verbose
    # -f = arquivo de saída
    cmd = [
        pg_dump_path,
        '-h', DB_HOST,
        '-p', DB_PORT,
        '-U', DB_USER,
        '-d', DB_NAME,
        '-F', 'p',  # Formato texto
        '-b',  # Incluir blobs
        '-v',  # Verbose
        '-f', backup_file
    ]
    
    print(f"Executando: pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} ...")
    
    # Usar variável de ambiente para senha (evita prompt interativo)
    env = os.environ.copy()
    env['PGPASSWORD'] = DB_PASSWORD
    
    result = subprocess.run(cmd, text=True, env=env)
    
    if result.returncode == 0:
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(backup_file)
        size_mb = file_size / (1024 * 1024)
        
        print(f"\n✅ Backup criado com sucesso!")
        print(f"📊 Tamanho: {size_mb:.2f} MB")
        print(f"📁 Local: {os.path.abspath(backup_file)}")
        
        # Verificar se o arquivo tem conteúdo
        with open(backup_file, 'r', encoding='utf-8') as f:
            first_lines = f.readlines()[:5]
            if any('PostgreSQL database dump' in line or 'CREATE DATABASE' in line or 'CREATE TABLE' in line for line in first_lines):
                print(f"✅ Arquivo valido (formato SQL PostgreSQL)")
            else:
                print(f"⚠️ Aviso: Verifique o conteudo do arquivo")
    else:
        print(f"\n❌ Erro ao criar backup!")
        print(f"Codigo de retorno: {result.returncode}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Erro ao criar backup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n💡 Proximo passo: Envie este arquivo via WinSCP para:")
print(f"   /home/seprom/sepromcbmepi/")
print(f"\n💡 Para restaurar no servidor, use:")
print(f"   psql -U seprom -d sepromcbmepi < {backup_file}")

