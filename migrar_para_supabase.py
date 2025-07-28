#!/usr/bin/env python
"""
Script para migrar dados do banco local para o Supabase
"""

import os
import sys
import django
import subprocess
from datetime import datetime

def configurar_ambiente():
    """Configura o ambiente Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
    django.setup()

def fazer_backup_local():
    """Faz backup do banco de dados local"""
    try:
        print("💾 Fazendo backup do banco local...")
        
        # Nome do arquivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_local_{timestamp}.json"
        
        # Comando para fazer dump dos dados
        cmd = [
            'python', 'manage.py', 'dumpdata',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.Permission',
            '--indent', '2',
            '--output', backup_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Backup criado com sucesso: {backup_file}")
            return backup_file
        else:
            print(f"❌ Erro ao criar backup: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return None

def configurar_supabase():
    """Configura o ambiente para o Supabase"""
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings_supabase'
    django.setup()

def executar_migracoes_supabase():
    """Executa migrações no Supabase"""
    try:
        print("🔄 Executando migrações no Supabase...")
        
        cmd = [
            'python', 'manage.py', 'migrate',
            '--settings=sepromcbmepi.settings_supabase'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrações executadas com sucesso no Supabase")
            return True
        else:
            print(f"❌ Erro nas migrações: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False

def carregar_dados_supabase(backup_file):
    """Carrega os dados do backup no Supabase"""
    try:
        print(f"📤 Carregando dados no Supabase: {backup_file}")
        
        cmd = [
            'python', 'manage.py', 'loaddata', backup_file,
            '--settings=sepromcbmepi.settings_supabase'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dados carregados com sucesso no Supabase")
            return True
        else:
            print(f"❌ Erro ao carregar dados: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

def criar_superusuario_supabase():
    """Cria um superusuário no Supabase"""
    try:
        print("👤 Criando superusuário no Supabase...")
        
        # Dados do superusuário
        username = "erisman"
        email = "erisman@cbmepi.com"
        password = "admin123456"
        
        cmd = [
            'python', 'manage.py', 'shell',
            '--settings=sepromcbmepi.settings_supabase',
            '-c', f'''
from django.contrib.auth.models import User
if not User.objects.filter(username="{username}").exists():
    User.objects.create_superuser("{username}", "{email}", "{password}")
    print("Superusuário criado com sucesso!")
else:
    print("Superusuário já existe!")
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Superusuário criado/verificado no Supabase")
            print(f"👤 Usuário: {username}")
            print(f"🔑 Senha: {password}")
            return True
        else:
            print(f"❌ Erro ao criar superusuário: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def testar_conexao_supabase():
    """Testa a conexão com o Supabase"""
    try:
        print("🔍 Testando conexão com o Supabase...")
        
        cmd = [
            'python', 'manage.py', 'shell',
            '--settings=sepromcbmepi.settings_supabase',
            '-c', '''
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM auth_user;")
    count = cursor.fetchone()[0]
    print(f"Total de usuários no Supabase: {count}")
'''
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Conexão com Supabase testada com sucesso")
            print(result.stdout)
            return True
        else:
            print(f"❌ Erro ao testar conexão: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando migração para o Supabase")
    print("=" * 60)
    
    # Passo 1: Fazer backup do banco local
    backup_file = fazer_backup_local()
    if not backup_file:
        print("❌ Falha no backup. Abortando migração.")
        return
    
    print()
    
    # Passo 2: Executar migrações no Supabase
    if not executar_migracoes_supabase():
        print("❌ Falha nas migrações. Abortando migração.")
        return
    
    print()
    
    # Passo 3: Carregar dados no Supabase
    if not carregar_dados_supabase(backup_file):
        print("❌ Falha no carregamento de dados. Abortando migração.")
        return
    
    print()
    
    # Passo 4: Criar superusuário
    if not criar_superusuario_supabase():
        print("❌ Falha na criação do superusuário.")
        return
    
    print()
    
    # Passo 5: Testar conexão
    if not testar_conexao_supabase():
        print("❌ Falha no teste de conexão.")
        return
    
    print()
    print("🎉 Migração para o Supabase concluída com sucesso!")
    print("=" * 60)
    print("📋 Próximos passos:")
    print("1. Execute: python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    print("2. Acesse: http://localhost:8000")
    print("3. Faça login com:")
    print("   👤 Usuário: erisman")
    print("   🔑 Senha: admin123456")
    print()
    print("⚠️  IMPORTANTE: Substitua Erisman@193 pela senha real do Supabase no arquivo settings_supabase.py")

if __name__ == "__main__":
    main() 