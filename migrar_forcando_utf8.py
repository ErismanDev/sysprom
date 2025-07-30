#!/usr/bin/env python3
"""
Script para migrar dados forçando codificação UTF-8
"""

import os
import sys
import django
import json
import codecs
from datetime import datetime

def configurar_supabase():
    """Configura o ambiente para Supabase"""
    print("🌐 Configurando ambiente Supabase...")
    
    # Configurar variáveis de ambiente
    os.environ['DATABASE_URL'] = "postgresql://postgres.vubnekyyfjcrswaufnla:2YXGdmXESoZAoPkO@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings_render'
    
    try:
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

def carregar_dados_manualmente(backup_file):
    """Carrega os dados manualmente com codificação forçada"""
    print(f"\n📤 Carregando dados manualmente: {backup_file}")
    
    try:
        # Tentar diferentes codificações
        codificacoes = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        dados = None
        for codificacao in codificacoes:
            try:
                print(f"   Tentando codificação: {codificacao}")
                with open(backup_file, 'r', encoding=codificacao) as f:
                    dados = json.load(f)
                print(f"   ✅ Sucesso com codificação: {codificacao}")
                break
            except UnicodeDecodeError:
                print(f"   ❌ Falhou com codificação: {codificacao}")
                continue
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON inválido com codificação: {codificacao} - {e}")
                continue
        
        if dados is None:
            print("❌ Não foi possível ler o arquivo com nenhuma codificação")
            return False
        
        # Carregar dados usando Django
        from django.core.management import call_command
        from django.core.management.base import CommandError
        
        # Criar arquivo temporário com codificação correta
        temp_file = f"temp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        try:
            call_command('loaddata', temp_file)
            print("✅ Dados carregados no Supabase")
            
            # Remover arquivo temporário
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao processar backup: {e}")
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
        
        # Criar superusuário padrão
        print("📝 Criando superusuário padrão...")
        
        User.objects.create_superuser(
            username="admin",
            email="admin@cbmepi.com",
            password="admin123"
        )
        print("✅ Superusuário 'admin' criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("❌ Uso: python migrar_forcando_utf8.py <arquivo_backup>")
        print("Exemplo: python migrar_forcando_utf8.py backup_utf8_20250729_122049.json")
        return False
    
    backup_file = sys.argv[1]
    
    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return False
    
    print("🚀 MIGRAÇÃO FORÇANDO UTF-8")
    print("=" * 50)
    print(f"📁 Backup: {backup_file}")
    
    # Passo 1: Configurar Supabase
    if not configurar_supabase():
        return False
    
    # Passo 2: Testar conexão
    if not testar_conexao_supabase():
        print("❌ Não foi possível conectar ao Supabase")
        return False
    
    # Passo 3: Aplicar migrações
    if not aplicar_migracoes_supabase():
        return False
    
    # Passo 4: Carregar dados
    if not carregar_dados_manualmente(backup_file):
        return False
    
    # Passo 5: Verificar migração
    if not verificar_migracao():
        return False
    
    # Passo 6: Criar superusuário
    criar_superuser_supabase()
    
    print("\n" + "=" * 50)
    print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 50)
    print()
    print("📋 RESUMO:")
    print("✅ Dados migrados com codificação forçada para o Supabase")
    print("✅ Migrações aplicadas")
    print("✅ Superusuário configurado")
    print()
    print("🌐 PRÓXIMOS PASSOS:")
    print("1. Teste a aplicação no Render: https://sysprom.onrender.com")
    print("2. Faça login com: admin / admin123")
    print("3. Verifique se todos os dados estão presentes")
    print("4. Teste as funcionalidades principais")
    
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