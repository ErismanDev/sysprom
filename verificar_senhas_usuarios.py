#!/usr/bin/env python
import os
import sys
import django
import sqlite3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

def verificar_senhas_usuarios():
    print("=== VERIFICANDO SENHAS DOS USUÁRIOS ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Buscar usuários do SQLite com senhas
        cursor_sqlite.execute("""
            SELECT username, password, is_active, is_staff, is_superuser
            FROM auth_user
            ORDER BY username
        """)
        
        usuarios_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de usuários no SQLite: {len(usuarios_sqlite)}")
        
        if len(usuarios_sqlite) == 0:
            print("❌ Nenhum usuário encontrado no SQLite!")
            return
        
        print("\n=== VERIFICANDO SENHAS ===")
        
        senhas_migradas = 0
        senhas_nao_migradas = 0
        usuarios_nao_encontrados = 0
        
        for usuario_sqlite in usuarios_sqlite:
            username, password_sqlite, is_active, is_staff, is_superuser = usuario_sqlite
            
            print(f"\n--- Verificando usuário: {username} ---")
            
            try:
                # Buscar usuário no PostgreSQL
                try:
                    usuario_postgres = User.objects.get(username=username)
                    print(f"   ✅ Usuário encontrado no PostgreSQL")
                    
                    # Verificar se a senha foi migrada
                    if password_sqlite and password_sqlite != '':
                        # Verificar se a senha no PostgreSQL é diferente (hash do Django)
                        if usuario_postgres.password != password_sqlite:
                            print(f"   ✅ Senha migrada (hash atualizado)")
                            senhas_migradas += 1
                        else:
                            print(f"   ⚠️ Senha não foi migrada (ainda é a original)")
                            senhas_nao_migradas += 1
                    else:
                        print(f"   ⚠️ Usuário sem senha no SQLite")
                    
                    # Verificar outros campos
                    if usuario_postgres.is_active != is_active:
                        print(f"   ⚠️ Status ativo diferente: SQLite={is_active}, PostgreSQL={usuario_postgres.is_active}")
                    
                    if usuario_postgres.is_staff != is_staff:
                        print(f"   ⚠️ Status staff diferente: SQLite={is_staff}, PostgreSQL={usuario_postgres.is_staff}")
                    
                    if usuario_postgres.is_superuser != is_superuser:
                        print(f"   ⚠️ Status superuser diferente: SQLite={is_superuser}, PostgreSQL={usuario_postgres.is_superuser}")
                    
                except User.DoesNotExist:
                    print(f"   ❌ Usuário não encontrado no PostgreSQL")
                    usuarios_nao_encontrados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar usuário: {e}")
        
        conn_sqlite.close()
        
        print(f"\n=== RESUMO ===")
        print(f"Senhas migradas: {senhas_migradas}")
        print(f"Senhas não migradas: {senhas_nao_migradas}")
        print(f"Usuários não encontrados: {usuarios_nao_encontrados}")
        print(f"Total processado: {len(usuarios_sqlite)}")
        
        # Verificar alguns usuários específicos
        print(f"\n=== TESTE DE LOGIN ===")
        usuarios_teste = ['admin', '490.083.823-34', '361.367.943-49']
        
        for username_teste in usuarios_teste:
            try:
                usuario = User.objects.get(username=username_teste)
                print(f"   • {username_teste}: {'Ativo' if usuario.is_active else 'Inativo'}")
                print(f"     - Staff: {'Sim' if usuario.is_staff else 'Não'}")
                print(f"     - Superuser: {'Sim' if usuario.is_superuser else 'Não'}")
                print(f"     - Senha: {'Definida' if usuario.password else 'Não definida'}")
            except User.DoesNotExist:
                print(f"   • {username_teste}: Não encontrado")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    verificar_senhas_usuarios() 