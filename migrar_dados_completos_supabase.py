#!/usr/bin/env python3
"""
Script completo para migrar todos os dados do banco local para o Supabase
"""

import os
import sys
import django
import json
from datetime import datetime
from pathlib import Path

def configurar_ambiente():
    """Configura o ambiente Django"""
    print("🔧 Configurando ambiente Django...")
    
    # Configurar settings para banco local
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
    
    try:
        django.setup()
        print("✅ Ambiente Django configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar Django: {e}")
        return False

def verificar_banco_local():
    """Verifica se o banco local tem dados"""
    print("\n🔍 Verificando dados no banco local...")
    
    try:
        from django.contrib.auth.models import User
        from militares.models import Militar, ComissaoPromocao, QuadroAcesso
        
        # Contar registros principais
        total_usuarios = User.objects.count()
        total_militares = Militar.objects.count()
        total_comissoes = ComissaoPromocao.objects.count()
        total_quadros = QuadroAcesso.objects.count()
        
        print(f"📊 Dados encontrados:")
        print(f"   • Usuários: {total_usuarios}")
        print(f"   • Militares: {total_militares}")
        print(f"   • Comissões: {total_comissoes}")
        print(f"   • Quadros de Acesso: {total_quadros}")
        
        if total_usuarios == 0 and total_militares == 0:
            print("⚠️  Nenhum dado encontrado no banco local!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco local: {e}")
        return False

def fazer_backup_completo():
    """Faz backup completo de todos os dados"""
    print("\n💾 Fazendo backup completo dos dados...")
    
    try:
        from django.core.management import call_command
        
        # Nome do arquivo de backup com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_completo_{timestamp}.json"
        
        # Fazer backup excluindo apenas contenttypes e permissions
        call_command(
            'dumpdata',
            '--exclude', 'contenttypes',
            '--exclude', 'auth.Permission',
            '--indent', '2',
            '--output', backup_file
        )
        
        print(f"✅ Backup criado: {backup_file}")
        return backup_file
        
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return None

def configurar_supabase():
    """Configura o ambiente para Supabase"""
    print("\n🌐 Configurando ambiente Supabase...")
    
    # Configurar settings para Supabase
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings_render'
    
    try:
        # Recarregar Django com configuração do Supabase
        django.setup()
        print("✅ Ambiente Supabase configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar Supabase: {e}")
        return False

def testar_conexao_supabase():
    """Testa a conexão com o Supabase"""
    print("\n🧪 Testando conexão com Supabase...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result and result[0] == 1:
            print("✅ Conexão com Supabase estabelecida")
            return True
        else:
            print("❌ Conexão com Supabase falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {e}")
        return False

def aplicar_migracoes_supabase():
    """Aplica migrações no Supabase"""
    print("\n🗄️ Aplicando migrações no Supabase...")
    
    try:
        from django.core.management import call_command
        
        call_command('migrate')
        print("✅ Migrações aplicadas no Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        return False

def carregar_dados_supabase(backup_file):
    """Carrega os dados no Supabase"""
    print(f"\n📤 Carregando dados no Supabase: {backup_file}")
    
    try:
        from django.core.management import call_command
        
        call_command('loaddata', backup_file)
        print("✅ Dados carregados no Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

def verificar_migracao():
    """Verifica se a migração foi bem-sucedida"""
    print("\n🔍 Verificando migração...")
    
    try:
        from django.contrib.auth.models import User
        from militares.models import Militar, ComissaoPromocao, QuadroAcesso
        
        # Contar registros no Supabase
        total_usuarios = User.objects.count()
        total_militares = Militar.objects.count()
        total_comissoes = ComissaoPromocao.objects.count()
        total_quadros = QuadroAcesso.objects.count()
        
        print(f"📊 Dados no Supabase:")
        print(f"   • Usuários: {total_usuarios}")
        print(f"   • Militares: {total_militares}")
        print(f"   • Comissões: {total_comissoes}")
        print(f"   • Quadros de Acesso: {total_quadros}")
        
        if total_usuarios > 0 and total_militares > 0:
            print("✅ Migração realizada com sucesso!")
            return True
        else:
            print("❌ Migração falhou - dados não encontrados")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False

def criar_superuser_supabase():
    """Cria um superusuário no Supabase se não existir"""
    print("\n👤 Verificando superusuário no Supabase...")
    
    try:
        from django.contrib.auth.models import User
        
        # Verificar se já existe superusuário
        if User.objects.filter(is_superuser=True).exists():
            print("✅ Superusuário já existe no Supabase")
            return True
        
        # Criar superusuário
        print("📝 Criando superusuário...")
        print("Por favor, insira os dados do superusuário:")
        
        username = input("Usuário (admin): ").strip() or "admin"
        email = input("Email (admin@cbmepi.com): ").strip() or "admin@cbmepi.com"
        password = input("Senha (admin123): ").strip() or "admin123"
        
        User.objects.create_superuser(username, email, password)
        print(f"✅ Superusuário '{username}' criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def limpar_arquivos_temporarios(backup_file):
    """Remove arquivos temporários"""
    print(f"\n🧹 Removendo arquivo temporário: {backup_file}")
    
    try:
        if os.path.exists(backup_file):
            os.remove(backup_file)
            print("✅ Arquivo temporário removido")
        return True
    except Exception as e:
        print(f"⚠️  Erro ao remover arquivo: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 MIGRAÇÃO COMPLETA: Banco Local → Supabase")
    print("=" * 60)
    
    # Passo 1: Configurar ambiente local
    if not configurar_ambiente():
        return False
    
    # Passo 2: Verificar dados locais
    if not verificar_banco_local():
        print("❌ Nenhum dado encontrado para migrar")
        return False
    
    # Passo 3: Fazer backup
    backup_file = fazer_backup_completo()
    if not backup_file:
        return False
    
    # Passo 4: Configurar Supabase
    if not configurar_supabase():
        return False
    
    # Passo 5: Testar conexão
    if not testar_conexao_supabase():
        print("❌ Não foi possível conectar ao Supabase")
        print("💡 Verifique:")
        print("   - Credenciais do Supabase")
        print("   - Configuração da DATABASE_URL")
        print("   - Conectividade de rede")
        return False
    
    # Passo 6: Aplicar migrações
    if not aplicar_migracoes_supabase():
        return False
    
    # Passo 7: Carregar dados
    if not carregar_dados_supabase(backup_file):
        return False
    
    # Passo 8: Verificar migração
    if not verificar_migracao():
        return False
    
    # Passo 9: Criar superusuário
    criar_superuser_supabase()
    
    # Passo 10: Limpar arquivos temporários
    limpar_arquivos_temporarios(backup_file)
    
    print("\n" + "=" * 60)
    print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("📋 RESUMO:")
    print("✅ Dados migrados do banco local para o Supabase")
    print("✅ Migrações aplicadas")
    print("✅ Superusuário configurado")
    print()
    print("🌐 PRÓXIMOS PASSOS:")
    print("1. Teste a aplicação no Render: https://sysprom.onrender.com")
    print("2. Faça login com as credenciais do superusuário")
    print("3. Verifique se todos os dados estão presentes")
    print("4. Teste as funcionalidades principais")
    print()
    print("🔧 Para usar localmente com Supabase:")
    print("   python manage.py runserver --settings=sepromcbmepi.settings_render")
    print()
    print("🔧 Para usar localmente com banco local:")
    print("   python manage.py runserver")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Migração falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Migração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 