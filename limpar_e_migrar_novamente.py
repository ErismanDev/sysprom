#!/usr/bin/env python3
"""
Script para limpar o banco Supabase e migrar novamente
"""

import os
import sys
import django
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

def limpar_banco_supabase():
    """Limpa todos os dados do banco Supabase"""
    print("\n🧹 Limpando banco Supabase...")
    
    try:
        from django.core.management import call_command
        
        # Limpar todos os dados
        call_command('flush', '--noinput')
        print("✅ Banco Supabase limpo")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")
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

def migrar_dados_por_lotes(backup_file):
    """Migra dados por lotes para evitar problemas de chave duplicada"""
    print(f"\n📤 Migrando dados por lotes: {backup_file}")
    
    try:
        import json
        
        # Ler o arquivo de backup
        with open(backup_file, 'r', encoding='latin-1') as f:
            dados = json.load(f)
        
        print(f"📊 Total de registros: {len(dados)}")
        
        # Separar dados por modelo
        usuarios = []
        militares = []
        outros = []
        
        for item in dados:
            modelo = item.get('model', '')
            if 'auth.user' in modelo:
                usuarios.append(item)
            elif 'militares.militar' in modelo:
                militares.append(item)
            else:
                outros.append(item)
        
        print(f"👥 Usuários: {len(usuarios)}")
        print(f"🎖️  Militares: {len(militares)}")
        print(f"📋 Outros: {len(outros)}")
        
        # Migrar usuários primeiro
        if usuarios:
            print("\n📤 Migrando usuários...")
            temp_file = f"temp_usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(usuarios, f, ensure_ascii=False, indent=2)
            
            from django.core.management import call_command
            call_command('loaddata', temp_file)
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print("✅ Usuários migrados")
        
        # Migrar militares
        if militares:
            print("\n📤 Migrando militares...")
            temp_file = f"temp_militares_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(militares, f, ensure_ascii=False, indent=2)
            
            from django.core.management import call_command
            call_command('loaddata', temp_file)
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print("✅ Militares migrados")
        
        # Migrar outros dados
        if outros:
            print("\n📤 Migrando outros dados...")
            temp_file = f"temp_outros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(outros, f, ensure_ascii=False, indent=2)
            
            from django.core.management import call_command
            call_command('loaddata', temp_file)
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            print("✅ Outros dados migrados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao migrar dados por lotes: {e}")
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
        print("❌ Uso: python limpar_e_migrar_novamente.py <arquivo_backup>")
        print("Exemplo: python limpar_e_migrar_novamente.py backup_utf8_20250729_122049.json")
        return False
    
    backup_file = sys.argv[1]
    
    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return False
    
    print("🚀 LIMPEZA E MIGRAÇÃO NOVA")
    print("=" * 50)
    print(f"📁 Backup: {backup_file}")
    
    # Passo 1: Configurar Supabase
    if not configurar_supabase():
        return False
    
    # Passo 2: Limpar banco
    if not limpar_banco_supabase():
        return False
    
    # Passo 3: Aplicar migrações
    if not aplicar_migracoes_supabase():
        return False
    
    # Passo 4: Migrar dados por lotes
    if not migrar_dados_por_lotes(backup_file):
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
    print("✅ Banco limpo e dados migrados por lotes")
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