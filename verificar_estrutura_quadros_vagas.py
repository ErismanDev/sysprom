#!/usr/bin/env python
import os
import sys
import django
import sqlite3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def verificar_estrutura_quadros_vagas():
    print("=== VERIFICANDO ESTRUTURA DAS TABELAS DE QUADROS E VAGAS ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Verificar estrutura da tabela de quadros de acesso
        print(f"\n=== ESTRUTURA DA TABELA QUADROS DE ACESSO ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_quadroacesso)")
        colunas_quadro = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_quadroacesso:")
        for coluna in colunas_quadro:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de quadros
        cursor_sqlite.execute("SELECT * FROM militares_quadroacesso LIMIT 1")
        dados_quadro = cursor_sqlite.fetchone()
        
        if dados_quadro:
            print(f"\nExemplo de dados de quadro:")
            for i, coluna in enumerate(colunas_quadro):
                print(f"   • {coluna[1]}: {dados_quadro[i]}")
        
        # Verificar estrutura da tabela de vagas
        print(f"\n=== ESTRUTURA DA TABELA VAGAS ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_vaga)")
        colunas_vaga = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_vaga:")
        for coluna in colunas_vaga:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de vagas
        cursor_sqlite.execute("SELECT * FROM militares_vaga LIMIT 1")
        dados_vaga = cursor_sqlite.fetchone()
        
        if dados_vaga:
            print(f"\nExemplo de dados de vaga:")
            for i, coluna in enumerate(colunas_vaga):
                print(f"   • {coluna[1]}: {dados_vaga[i]}")
        
        # Verificar estrutura da tabela de quadros de fixação de vagas
        print(f"\n=== ESTRUTURA DA TABELA QUADROS DE FIXAÇÃO DE VAGAS ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_quadrofixacaovagas)")
        colunas_quadro_fixacao = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_quadrofixacaovagas:")
        for coluna in colunas_quadro_fixacao:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de quadros de fixação
        cursor_sqlite.execute("SELECT * FROM militares_quadrofixacaovagas LIMIT 1")
        dados_quadro_fixacao = cursor_sqlite.fetchone()
        
        if dados_quadro_fixacao:
            print(f"\nExemplo de dados de quadro de fixação:")
            for i, coluna in enumerate(colunas_quadro_fixacao):
                print(f"   • {coluna[1]}: {dados_quadro_fixacao[i]}")
        
        # Contar registros
        print(f"\n=== CONTAGEM DE REGISTROS ===")
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_quadroacesso")
        count_quadros = cursor_sqlite.fetchone()[0]
        print(f"Quadros de Acesso: {count_quadros}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_vaga")
        count_vagas = cursor_sqlite.fetchone()[0]
        print(f"Vagas: {count_vagas}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_quadrofixacaovagas")
        count_quadros_fixacao = cursor_sqlite.fetchone()[0]
        print(f"Quadros de Fixação de Vagas: {count_quadros_fixacao}")
        
        conn_sqlite.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_estrutura_quadros_vagas() 