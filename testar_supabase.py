#!/usr/bin/env python
"""
Script simples para testar a conexão com o Supabase
"""

import os
import sys

def testar_conexao_supabase():
    """Testa a conexão com o Supabase"""
    
    # Configurar ambiente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')
    
    try:
        import django
        django.setup()
        
        from django.db import connection
        
        print("Testando conexao com o Supabase...")
        print("=" * 50)
        
        with connection.cursor() as cursor:
            # Teste 1: Versão do PostgreSQL
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] PostgreSQL: {version[0]}")
            
            # Teste 2: Listar tabelas
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"[OK] Tabelas encontradas: {len(tables)}")
            
            # Teste 3: Contar usuários
            try:
                cursor.execute("SELECT COUNT(*) FROM auth_user;")
                user_count = cursor.fetchone()[0]
                print(f"[OK] Usuarios no sistema: {user_count}")
            except Exception as e:
                print(f"[AVISO] Tabela auth_user nao encontrada: {e}")
            
            # Teste 4: Contar militares
            try:
                cursor.execute("SELECT COUNT(*) FROM militares_militar;")
                militar_count = cursor.fetchone()[0]
                print(f"[OK] Militares no sistema: {militar_count}")
            except Exception as e:
                print(f"[AVISO] Tabela militares_militar nao encontrada: {e}")
        
        print("=" * 50)
        print("Conexao com Supabase estabelecida com sucesso!")
        return True
        
    except Exception as e:
        print(f"ERRO ao conectar com o Supabase: {e}")
        print("\nPossiveis solucoes:")
        print("1. Verifique se a senha esta correta em settings_supabase.py")
        print("2. Verifique se o host e porta estao corretos")
        print("3. Verifique se o banco de dados existe no Supabase")
        print("4. Verifique se o SSL esta configurado corretamente")
        return False

if __name__ == "__main__":
    testar_conexao_supabase() 