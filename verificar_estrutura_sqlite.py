#!/usr/bin/env python
import os
import sys
import sqlite3

def verificar_estrutura_sqlite():
    print("=== VERIFICANDO ESTRUTURA DA TABELA NO SQLITE ===\n")
    
    # Caminho para o arquivo SQLite de backup
    sqlite_path = 'db_backup.sqlite3'
    
    if not os.path.exists(sqlite_path):
        print(f"❌ Arquivo {sqlite_path} não encontrado!")
        return
    
    try:
        # Conectar ao SQLite
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        print(f"✅ Conectado ao SQLite: {sqlite_path}")
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='militares_membrocomissao'")
        if not cursor.fetchone():
            print("❌ Tabela militares_membrocomissao não encontrada no SQLite!")
            return
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(militares_membrocomissao)")
        colunas = cursor.fetchall()
        
        print("Estrutura da tabela militares_membrocomissao:")
        for coluna in colunas:
            (cid, name, type, notnull, dflt_value, pk) = coluna
            print(f"  • {name} ({type}) - NOT NULL: {notnull} - PK: {pk}")
        
        # Verificar dados da tabela
        cursor.execute("SELECT * FROM militares_membrocomissao LIMIT 5")
        dados = cursor.fetchall()
        
        print(f"\nPrimeiros 5 registros:")
        for registro in dados:
            print(f"  {registro}")
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM militares_membrocomissao")
        total = cursor.fetchone()[0]
        print(f"\nTotal de registros na tabela: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao acessar SQLite: {e}")
        return

if __name__ == '__main__':
    verificar_estrutura_sqlite() 