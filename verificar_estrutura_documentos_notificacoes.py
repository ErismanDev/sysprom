#!/usr/bin/env python
import os
import sys
import django
import sqlite3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

def verificar_estrutura_documentos_notificacoes():
    print("=== VERIFICANDO ESTRUTURA DAS TABELAS DE DOCUMENTOS E NOTIFICAÇÕES ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Verificar estrutura da tabela de documentos
        print(f"\n=== ESTRUTURA DA TABELA DOCUMENTOS ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_documento)")
        colunas_documento = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_documento:")
        for coluna in colunas_documento:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de documentos
        cursor_sqlite.execute("SELECT * FROM militares_documento LIMIT 1")
        dados_documento = cursor_sqlite.fetchone()
        
        if dados_documento:
            print(f"\nExemplo de dados de documento:")
            for i, coluna in enumerate(colunas_documento):
                print(f"   • {coluna[1]}: {dados_documento[i]}")
        
        # Verificar estrutura da tabela de notificações
        print(f"\n=== ESTRUTURA DA TABELA NOTIFICAÇÕES ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_notificacaosessao)")
        colunas_notificacao = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_notificacaosessao:")
        for coluna in colunas_notificacao:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de notificações
        cursor_sqlite.execute("SELECT * FROM militares_notificacaosessao LIMIT 1")
        dados_notificacao = cursor_sqlite.fetchone()
        
        if dados_notificacao:
            print(f"\nExemplo de dados de notificação:")
            for i, coluna in enumerate(colunas_notificacao):
                print(f"   • {coluna[1]}: {dados_notificacao[i]}")
        
        # Verificar estrutura da tabela de documentos de sessão
        print(f"\n=== ESTRUTURA DA TABELA DOCUMENTOS DE SESSÃO ===")
        cursor_sqlite.execute("PRAGMA table_info(militares_documentosessao)")
        colunas_documento_sessao = cursor_sqlite.fetchall()
        
        print(f"Colunas da tabela militares_documentosessao:")
        for coluna in colunas_documento_sessao:
            print(f"   • {coluna[1]} ({coluna[2]}) - NotNull: {coluna[3]} - Default: {coluna[4]}")
        
        # Verificar dados da tabela de documentos de sessão
        cursor_sqlite.execute("SELECT * FROM militares_documentosessao LIMIT 1")
        dados_documento_sessao = cursor_sqlite.fetchone()
        
        if dados_documento_sessao:
            print(f"\nExemplo de dados de documento de sessão:")
            for i, coluna in enumerate(colunas_documento_sessao):
                print(f"   • {coluna[1]}: {dados_documento_sessao[i]}")
        
        # Contar registros
        print(f"\n=== CONTAGEM DE REGISTROS ===")
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_documento")
        count_documentos = cursor_sqlite.fetchone()[0]
        print(f"Documentos: {count_documentos}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_notificacaosessao")
        count_notificacoes = cursor_sqlite.fetchone()[0]
        print(f"Notificações: {count_notificacoes}")
        
        cursor_sqlite.execute("SELECT COUNT(*) FROM militares_documentosessao")
        count_documentos_sessao = cursor_sqlite.fetchone()[0]
        print(f"Documentos de Sessão: {count_documentos_sessao}")
        
        conn_sqlite.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    verificar_estrutura_documentos_notificacoes() 