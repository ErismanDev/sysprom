#!/usr/bin/env python
import sqlite3

def verificar_sqlite_simples():
    print("=== VERIFICANDO SQLITE SIMPLES ===\n")
    
    try:
        # Conectar ao SQLite
        conn = sqlite3.connect('db_backup.sqlite3')
        cursor = conn.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(militares_membrocomissao)")
        colunas = cursor.fetchall()
        
        print("Colunas da tabela militares_membrocomissao:")
        for coluna in colunas:
            print(f"  • {coluna[1]} ({coluna[2]})")
        
        # Verificar dados
        cursor.execute("SELECT COUNT(*) FROM militares_membrocomissao")
        total = cursor.fetchone()[0]
        print(f"\nTotal de membros no SQLite: {total}")
        
        if total > 0:
            cursor.execute("SELECT * FROM militares_membrocomissao LIMIT 3")
            dados = cursor.fetchall()
            print("\nPrimeiros 3 registros:")
            for registro in dados:
                print(f"  {registro}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_sqlite_simples() 