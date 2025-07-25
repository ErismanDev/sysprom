#!/usr/bin/env python
import os
import sys
import django
import sqlite3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def verificar_estrutura_sessoes():
    print("=== VERIFICANDO ESTRUTURA DA TABELA SESSÕES ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Verificar estrutura da tabela de sessões
        cursor_sqlite.execute("PRAGMA table_info(militares_sessaocomissao)")
        colunas = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_sessaocomissao:")
        for coluna in colunas:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela
        cursor_sqlite.execute("SELECT * FROM militares_sessaocomissao LIMIT 1")
        dados = cursor_sqlite.fetchone()
        
        if dados:
            print(f"\nExemplo de dados:")
            for i, coluna in enumerate(colunas):
                print(f"   • {coluna[1]}: {dados[i]}")
        
        # Verificar estrutura da tabela de votos
        print(f"\n=== ESTRUTURA DA TABELA VOTOS ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_votodeliberacao)")
        colunas_votos = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_votodeliberacao:")
        for coluna in colunas_votos:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de votos
        cursor_sqlite.execute("SELECT * FROM militares_votodeliberacao LIMIT 1")
        dados_votos = cursor_sqlite.fetchone()
        
        if dados_votos:
            print(f"\nExemplo de dados de votos:")
            for i, coluna in enumerate(colunas_votos):
                print(f"   • {coluna[1]}: {dados_votos[i]}")
        
        conn_sqlite.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_estrutura_sessoes() 