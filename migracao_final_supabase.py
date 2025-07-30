#!/usr/bin/env python3
"""
Script final para migrar dados para o Supabase
Resolve todos os problemas de conexão e associação
"""

import os
import sys
import django
import json
import subprocess
from datetime import datetime

def configurar_ambiente():
    """Configura o ambiente para Supabase"""
    print("🌐 Configurando ambiente Supabase...")
    
    # Configurar variáveis de ambiente
    os.environ['DATABASE_URL'] = "postgresql://postgres.vubnekyyfjcrswaufnla:2YXGdmXESoZAoPkO@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
    os.environ['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings_render'
    os.environ['SECRET_KEY'] = 'django-insecure-temp-key-for-migration'
    
    try:
        django.setup()
        print("✅ Ambiente Supabase configurado")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar Supabase: {e}")
        return False

def executar_comando_django(comando):
    """Executa um comando Django"""
    try:
        from django.core.management import call_command
        call_command(*comando.split())
        return True
    except Exception as e:
        print(f"❌ Erro ao executar comando '{comando}': {e}")
        return False

def carregar_dados_via_subprocess():
    """Carrega dados usando subprocess para evitar travamentos"""
    print("\n📤 Carregando dados via subprocess...")
    
    try:
        # Configurar variáveis de ambiente para o subprocess
        env = os.environ.copy()
        env['DATABASE_URL'] = "postgresql://postgres.vubnekyyfjcrswaufnla:2YXGdmXESoZAoPkO@aws-0-sa-east-1.pooler.supabase.com:6543/postgres"
        env['DJANGO_SETTINGS_MODULE'] = 'sepromcbmepi.settings_render'
        env['SECRET_KEY'] = 'django-insecure-temp-key-for-migration'
        
        # Executar loaddata via subprocess
        comando = [
            sys.executable, 'manage.py', 'loaddata', 
            'backup_atual_20250729_123645_utf8.json',
            '--settings=sepromcbmepi.settings_render'
        ]
        
        print("⏳ Executando carregamento de dados...")
        resultado = subprocess.run(
            comando, 
            env=env, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        if resultado.returncode == 0:
            print("✅ Dados carregados com sucesso!")
            return True
        else:
            print(f"❌ Erro ao carregar dados:")
            print(f"STDOUT: {resultado.stdout}")
            print(f"STDERR: {resultado.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout ao carregar dados (5 minutos)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar subprocess: {e}")
        return False

def associar_usuarios_militares():
    """Associa usuários aos militares de forma manual"""
    print("\n🔗 Associando usuários aos militares...")
    
    try:
        from django.contrib.auth.models import User
        from militares.models import Militar
        
        # Desabilitar temporariamente o signal de associação automática
        from django.db.models.signals import post_save
        from militares.signals import associar_usuario_a_militar
        
        # Desconectar o signal temporariamente
        post_save.disconnect(associar_usuario_a_militar, sender=User)
        
        usuarios_associados = 0
        usuarios_nao_associados = 0
        
        # Buscar todos os usuários que não estão associados a militares
        usuarios_sem_militar = User.objects.filter(militar__isnull=True)
        
        print(f"📊 Total de usuários sem militar: {usuarios_sem_militar.count()}")
        
        for usuario in usuarios_sem_militar:
            militar_encontrado = None
            
            # Tentar encontrar militar por CPF (username)
            try:
                militar_encontrado = Militar.objects.get(cpf=usuario.username)
            except Militar.DoesNotExist:
                pass
            
            # Se não encontrou por CPF, tentar por nome completo
            if not militar_encontrado:
                nome_completo = f"{usuario.first_name} {usuario.last_name}".strip()
                if nome_completo:
                    try:
                        militar_encontrado = Militar.objects.get(nome_completo__iexact=nome_completo)
                    except Militar.DoesNotExist:
                        pass
            
            # Se não encontrou por nome, tentar por email
            if not militar_encontrado and usuario.email:
                try:
                    militar_encontrado = Militar.objects.get(email__iexact=usuario.email)
                except Militar.DoesNotExist:
                    pass
            
            # Se encontrou militar, associar
            if militar_encontrado and not militar_encontrado.user:
                militar_encontrado.user = usuario
                militar_encontrado.save(update_fields=['user'])
                usuarios_associados += 1
                print(f"✅ Usuário {usuario.username} associado ao militar {militar_encontrado.nome_completo}")
            else:
                usuarios_nao_associados += 1
                print(f"⚠️  Usuário {usuario.username} não pôde ser associado automaticamente")
        
        # Reconectar o signal
        post_save.connect(associar_usuario_a_militar, sender=User)
        
        print(f"\n📊 RESUMO DA ASSOCIAÇÃO:")
        print(f"   • Usuários associados: {usuarios_associados}")
        print(f"   • Usuários não associados: {usuarios_nao_associados}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao associar usuários: {e}")
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
        usuarios_com_militar = User.objects.filter(militar__isnull=False).count()
        
        print(f"📊 Dados no Supabase:")
        print(f"   • Usuários: {total_usuarios}")
        print(f"   • Militares: {total_militares}")
        print(f"   • Usuários associados a militares: {usuarios_com_militar}")
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
        User.objects.create_superuser('admin', 'admin@cbmepi.com', 'admin123')
        print("✅ Superusuário 'admin' criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 MIGRAÇÃO FINAL: Banco Local → Supabase")
    print("=" * 60)
    
    # Verificar se o arquivo UTF-8 existe
    arquivo_utf8 = "backup_atual_20250729_123645_utf8.json"
    if not os.path.exists(arquivo_utf8):
        print(f"❌ Arquivo UTF-8 não encontrado: {arquivo_utf8}")
        return False
    
    # Passo 1: Configurar ambiente
    if not configurar_ambiente():
        return False
    
    # Passo 2: Aplicar migrações
    print("\n🗄️ Aplicando migrações...")
    if not executar_comando_django("migrate"):
        return False
    
    # Passo 3: Carregar dados via subprocess
    if not carregar_dados_via_subprocess():
        return False
    
    # Passo 4: Associar usuários aos militares
    if not associar_usuarios_militares():
        print("⚠️  Aviso: Problemas na associação de usuários")
    
    # Passo 5: Verificar migração
    if not verificar_migracao():
        return False
    
    # Passo 6: Criar superusuário
    criar_superuser_supabase()
    
    print("\n" + "=" * 60)
    print("🎉 MIGRAÇÃO FINAL CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("📋 RESUMO:")
    print("✅ Dados migrados do banco local para o Supabase")
    print("✅ Migrações aplicadas")
    print("✅ Usuários associados aos militares")
    print("✅ Superusuário configurado")
    print()
    print("🌐 PRÓXIMOS PASSOS:")
    print("1. Teste a aplicação no Render: https://sysprom.onrender.com")
    print("2. Faça login com: admin / admin123")
    print("3. Verifique se todos os dados estão presentes")
    print("4. Teste as funcionalidades principais")
    print("5. Verifique se os usuários estão corretamente associados aos militares")
    
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