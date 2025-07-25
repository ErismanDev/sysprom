#!/usr/bin/env python
import os
import sys
import django
import sqlite3
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def corrigir_senhas_usuarios():
    print("=== CORRIGINDO SENHAS DOS USUÁRIOS ===\n")
    
    try:
        # Conectar ao SQLite
        conn_sqlite = sqlite3.connect('db_backup.sqlite3')
        cursor_sqlite = conn_sqlite.cursor()
        
        print("✅ Conectado ao SQLite")
        
        # Buscar usuários do SQLite com senhas
        cursor_sqlite.execute("""
            SELECT username, password, is_active, is_staff, is_superuser
            FROM auth_user
            WHERE password IS NOT NULL AND password != ''
            ORDER BY username
        """)
        
        usuarios_sqlite = cursor_sqlite.fetchall()
        
        print(f"Total de usuários com senha no SQLite: {len(usuarios_sqlite)}")
        
        if len(usuarios_sqlite) == 0:
            print("❌ Nenhum usuário com senha encontrado no SQLite!")
            return
        
        print("\n=== CORRIGINDO SENHAS ===")
        
        senhas_corrigidas = 0
        usuarios_nao_encontrados = 0
        
        for usuario_sqlite in usuarios_sqlite:
            username, password_sqlite, is_active, is_staff, is_superuser = usuario_sqlite
            
            print(f"\n--- Corrigindo usuário: {username} ---")
            
            try:
                # Buscar usuário no PostgreSQL
                try:
                    usuario_postgres = User.objects.get(username=username)
                    print(f"   ✅ Usuário encontrado no PostgreSQL")
                    
                    # Verificar se a senha precisa ser corrigida
                    if not usuario_postgres.password or usuario_postgres.password == '':
                        print(f"   ⚠️ Usuário sem senha no PostgreSQL")
                        
                        # Definir senha padrão baseada no tipo de usuário
                        if username == 'admin':
                            nova_senha = 'admin'
                        elif is_superuser:
                            nova_senha = 'admin123'
                        elif is_staff:
                            nova_senha = '123456'
                        else:
                            nova_senha = '123456'
                        
                        # Definir a nova senha
                        usuario_postgres.password = make_password(nova_senha)
                        usuario_postgres.save()
                        
                        print(f"   ✅ Senha definida: '{nova_senha}'")
                        senhas_corrigidas += 1
                        
                    else:
                        print(f"   ✅ Usuário já tem senha definida")
                        
                except User.DoesNotExist:
                    print(f"   ❌ Usuário não encontrado no PostgreSQL")
                    usuarios_nao_encontrados += 1
                
            except Exception as e:
                print(f"   ❌ Erro ao corrigir usuário: {e}")
        
        conn_sqlite.close()
        
        print(f"\n=== RESUMO ===")
        print(f"Senhas corrigidas: {senhas_corrigidas}")
        print(f"Usuários não encontrados: {usuarios_nao_encontrados}")
        print(f"Total processado: {len(usuarios_sqlite)}")
        
        # Definir senhas para usuários importantes que podem não ter senha
        print(f"\n=== DEFININDO SENHAS PARA USUÁRIOS IMPORTANTES ===")
        
        usuarios_importantes = [
            ('admin', 'admin'),
            ('490.083.823-34', '123456'),  # ERISMAN
            ('361.367.943-49', '123456'),  # CLEMILTON
            ('342.306.373-49', '123456'),  # TAVARES
            ('351.104.653-04', '123456'),  # VELOSO
        ]
        
        for username, senha in usuarios_importantes:
            try:
                usuario = User.objects.get(username=username)
                if not usuario.password or usuario.password == '':
                    usuario.password = make_password(senha)
                    usuario.save()
                    print(f"   ✅ {username}: senha definida como '{senha}'")
                else:
                    print(f"   ✅ {username}: já tem senha definida")
            except User.DoesNotExist:
                print(f"   ❌ {username}: usuário não encontrado")
        
        print(f"\n=== SENHAS PADRÃO DEFINIDAS ===")
        print(f"• admin: admin")
        print(f"• Usuários comuns: 123456")
        print(f"• Superusuários: admin123")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == '__main__':
    corrigir_senhas_usuarios() 