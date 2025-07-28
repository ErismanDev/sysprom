#!/usr/bin/env python
"""
Script para conectar o projeto SEPROM CBMEPI ao Supabase
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def configurar_supabase():
    """Configura as variáveis de ambiente para o Supabase"""
    
    # Configurar as variáveis de ambiente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')
    
    # URL de conexão do Supabase (substitua Erisman@193 pela senha real)
    DATABASE_URL = "postgresql://postgres:Erisman@193@db.vubnekyyfjcrswaufnla.supabase.co:5432/postgres"
    os.environ['DATABASE_URL'] = DATABASE_URL
    
    print("✅ Configurações do Supabase definidas")
    print(f"📊 URL do banco: {DATABASE_URL}")
    print(f"🔧 Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

def testar_conexao():
    """Testa a conexão com o banco de dados do Supabase"""
    try:
        django.setup()
        
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexão com Supabase estabelecida com sucesso!")
            print(f"📊 Versão do PostgreSQL: {version[0]}")
            
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar com o Supabase: {e}")
        return False

def executar_migracoes():
    """Executa as migrações no banco do Supabase"""
    try:
        print("🔄 Executando migrações...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações executadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def criar_superusuario():
    """Cria um superusuário no banco do Supabase"""
    try:
        print("👤 Criando superusuário...")
        execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
        print("✅ Superusuário criado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def coletar_estaticos():
    """Coleta arquivos estáticos"""
    try:
        print("📁 Coletando arquivos estáticos...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Arquivos estáticos coletados com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao coletar arquivos estáticos: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando configuração do Supabase para SEPROM CBMEPI")
    print("=" * 60)
    
    # Configurar Supabase
    configurar_supabase()
    print()
    
    # Testar conexão
    if not testar_conexao():
        print("❌ Falha na conexão. Verifique as credenciais do Supabase.")
        return
    
    print()
    
    # Executar migrações
    if not executar_migracoes():
        print("❌ Falha nas migrações.")
        return
    
    print()
    
    # Coletar arquivos estáticos
    if not coletar_estaticos():
        print("❌ Falha na coleta de arquivos estáticos.")
        return
    
    print()
    print("🎉 Configuração do Supabase concluída com sucesso!")
    print("=" * 60)
    print("📋 Próximos passos:")
    print("1. Execute: python manage.py createsuperuser")
    print("2. Execute: python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    print("3. Acesse: http://localhost:8000")

if __name__ == "__main__":
    main() 