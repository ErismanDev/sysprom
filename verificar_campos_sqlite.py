#!/usr/bin/env python
import sqlite3

def verificar_campos_sqlite():
    print("=== VERIFICANDO CAMPOS DA TABELA MILITARES NO SQLITE ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Verificar estrutura da tabela
        cursor_sqlite.execute("PRAGMA table_info(militares_militar)")
        colunas = cursor_sqlite.fetchall()
        
        print("Colunas da tabela militares_militar:")
        for coluna in colunas:
            print(f"  • {coluna[1]} ({coluna[2]}) - NOT NULL: {coluna[3]}")
        
        # Verificar alguns registros de exemplo
        print(f"\n=== EXEMPLOS DE REGISTROS ===")
        cursor_sqlite.execute("""
            SELECT id, nome_guerra, cpf, nome_completo, posto_graduacao, 
                   data_nascimento, data_incorporacao, data_promocao_atual
            FROM militares_militar 
            LIMIT 3
        """)
        
        registros = cursor_sqlite.fetchall()
        for registro in registros:
            print(f"ID: {registro[0]}")
            print(f"  Nome Guerra: {registro[1]}")
            print(f"  CPF: {registro[2]}")
            print(f"  Nome Completo: {registro[3]}")
            print(f"  Posto/Graduação: {registro[4]}")
            print(f"  Data Nascimento: {registro[5]}")
            print(f"  Data Incorporação: {registro[6]}")
            print(f"  Data Promoção Atual: {registro[7]}")
            print()
        
        conn_sqlite.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_campos_sqlite() 