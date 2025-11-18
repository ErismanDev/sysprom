#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar backup PostgreSQL usando Python (psycopg2)
Funciona mesmo sem pg_dump instalado
"""
import os
import sys
import psycopg2
from datetime import datetime

# Configurações do banco
DB_NAME = "sepromcbmepi"
DB_USER = "postgres"
DB_PASSWORD = "11322361"
DB_HOST = "localhost"
DB_PORT = "5432"

# Nome do arquivo de backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup_sepromcbmepi_{timestamp}.sql"

print("Criando backup PostgreSQL usando Python...")
print(f"Arquivo: {backup_file}")

try:
    # Conectar ao banco
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    # Criar cursor
    cur = conn.cursor()
    
    # Abrir arquivo para escrita
    with open(backup_file, 'w', encoding='utf-8') as f:
        # Escrever cabeçalho
        f.write("-- PostgreSQL database dump\n")
        f.write(f"-- Dumped by Python script on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Database: {DB_NAME}\n\n")
        f.write("SET statement_timeout = 0;\n")
        f.write("SET lock_timeout = 0;\n")
        f.write("SET idle_in_transaction_session_timeout = 0;\n")
        f.write("SET client_encoding = 'UTF8';\n")
        f.write("SET standard_conforming_strings = on;\n")
        f.write("SELECT pg_catalog.set_config('search_path', '', false);\n\n")
        
        # Obter todas as tabelas
        cur.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        print(f"Encontradas {len(tables)} tabelas")
        
        # Para cada tabela, fazer dump dos dados
        for table in tables:
            print(f"  Exportando tabela: {table}...")
            
            # Obter estrutura da tabela
            cur.execute(f"""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = '{table}' AND table_schema = 'public'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            # Obter dados
            cur.execute(f'SELECT * FROM "{table}";')
            rows = cur.fetchall()
            
            if rows:
                # Escrever CREATE TABLE (simplificado)
                f.write(f"\n-- Dados da tabela: {table}\n")
                f.write(f"COPY \"{table}\" (")
                col_names = [col[0] for col in columns]
                f.write(", ".join(f'"{col}"' for col in col_names))
                f.write(") FROM stdin;\n")
                
                # Escrever dados
                for row in rows:
                    values = []
                    for val in row:
                        if val is None:
                            values.append('\\N')
                        elif isinstance(val, str):
                            # Escapar caracteres especiais
                            val = val.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                            values.append(val)
                        else:
                            values.append(str(val))
                    f.write('\t'.join(values) + '\n')
                
                f.write("\\.\n")
        
        f.write("\n-- Fim do dump\n")
    
    # Fechar conexão
    cur.close()
    conn.close()
    
    # Verificar tamanho
    file_size = os.path.getsize(backup_file)
    size_mb = file_size / (1024 * 1024)
    
    print(f"\n✅ Backup criado com sucesso!")
    print(f"📊 Tamanho: {size_mb:.2f} MB")
    print(f"📁 Local: {os.path.abspath(backup_file)}")
    
except psycopg2.Error as e:
    print(f"\n❌ Erro ao conectar ao PostgreSQL: {e}")
    print("\n💡 Alternativa: Use o backup JSON que já foi criado:")
    print("   backup_sepromcbmepi_completo_20251115_154308.json")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Erro ao criar backup: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print(f"\n💡 Próximo passo: Envie este arquivo via WinSCP para:")
print(f"   /home/seprom/sepromcbmepi/")

