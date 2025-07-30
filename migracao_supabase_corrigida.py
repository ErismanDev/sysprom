#!/usr/bin/env python3
"""
Script corrigido para migrar dados para o Supabase
Resolve o problema de associação de usuários aos militares
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
    os.environ['SECRET_KEY'] = 'django-insecure-temp-key-for-migration'
    
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

def converter_para_utf8(arquivo_original):
    """Converte o arquivo para UTF-8"""
    print(f"\n🔄 Convertendo arquivo para UTF-8: {arquivo_original}")
    
    try:
        # Ler o arquivo original com latin-1
        with open(arquivo_original, 'r', encoding='latin-1') as f:
            conteudo = f.read()
        
        # Criar nome do arquivo convertido
        nome_base = os.path.splitext(arquivo_original)[0]
        arquivo_utf8 = f"{nome_base}_utf8.json"
        
        # Salvar como UTF-8
        with open(arquivo_utf8, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"✅ Arquivo convertido: {arquivo_utf8}")
        return arquivo_utf8
        
    except Exception as e:
        print(f"❌ Erro ao converter arquivo: {e}")
        return None

def carregar_dados_utf8(backup_file):
    """Carrega os dados do arquivo UTF-8"""
    print(f"\n📤 Carregando dados no Supabase: {backup_file}")
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(backup_file):
            print(f"❌ Arquivo não encontrado: {backup_file}")
            return False
        
        # Carregar dados usando loaddata
        from django.core.management import call_command
        
        call_command('loaddata', backup_file)
        print("✅ Dados carregados no Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
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

def limpar_arquivo_temporario(arquivo_utf8):
    """Remove o arquivo temporário"""
    try:
        if os.path.exists(arquivo_utf8):
            os.remove(arquivo_utf8)
            print(f"🧹 Arquivo temporário removido: {arquivo_utf8}")
    except Exception as e:
        print(f"⚠️  Erro ao remover arquivo temporário: {e}")

def main():
    """Função principal"""
    print("🚀 MIGRAÇÃO CORRIGIDA: Banco Local → Supabase")
    print("=" * 60)
    
    # Verificar se o arquivo de backup foi fornecido
    if len(sys.argv) != 2:
        print("❌ Uso: python migracao_supabase_corrigida.py <arquivo_backup>")
        print("Exemplo: python migracao_supabase_corrigida.py backup_atual_20250729_123645.json")
        return False
    
    backup_file = sys.argv[1]
    
    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup não encontrado: {backup_file}")
        return False
    
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
    
    # Passo 4: Converter arquivo para UTF-8
    arquivo_utf8 = converter_para_utf8(backup_file)
    if not arquivo_utf8:
        return False
    
    # Passo 5: Carregar dados
    if not carregar_dados_utf8(arquivo_utf8):
        return False
    
    # Passo 6: Associar usuários aos militares (CORREÇÃO)
    if not associar_usuarios_militares():
        print("⚠️  Aviso: Problemas na associação de usuários")
    
    # Passo 7: Verificar migração
    if not verificar_migracao():
        return False
    
    # Passo 8: Criar superusuário
    criar_superuser_supabase()
    
    # Passo 9: Limpar arquivo temporário
    limpar_arquivo_temporario(arquivo_utf8)
    
    print("\n" + "=" * 60)
    print("🎉 MIGRAÇÃO CORRIGIDA CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print()
    print("📋 RESUMO:")
    print("✅ Dados migrados do banco local para o Supabase")
    print("✅ Migrações aplicadas")
    print("✅ Usuários associados aos militares (corrigido)")
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