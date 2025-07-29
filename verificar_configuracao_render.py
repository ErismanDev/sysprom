#!/usr/bin/env python3
"""
Script para verificar a configuração do Render
"""

import os
import sys
import django

def verificar_variaveis_ambiente():
    """Verifica se as variáveis de ambiente estão configuradas"""
    print("🔍 Verificando variáveis de ambiente...")
    
    # Variáveis importantes para o Render
    variaveis_importantes = [
        'DATABASE_URL',
        'DJANGO_SETTINGS_MODULE',
        'SECRET_KEY',
        'ALLOWED_HOSTS',
    ]
    
    for var in variaveis_importantes:
        valor = os.environ.get(var)
        if valor:
            if var == 'DATABASE_URL':
                # Mostrar apenas o início da URL por segurança
                print(f"✅ {var}: {valor[:50]}...")
            elif var == 'SECRET_KEY':
                # Mostrar apenas o início da chave por segurança
                print(f"✅ {var}: {valor[:20]}...")
            else:
                print(f"✅ {var}: {valor}")
        else:
            print(f"❌ {var}: Não definida")
    
    return True

def testar_configuracao_render():
    """Testa a configuração do Render"""
    print("\n🧪 Testando configuração do Render...")
    
    try:
        # Configurar para usar settings_render
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_render')
        
        # Configurar Django
        django.setup()
        
        # Importar configurações
        from django.conf import settings
        
        print("✅ Django configurado com settings_render")
        
        # Verificar configurações importantes
        print(f"📊 DEBUG: {settings.DEBUG}")
        print(f"🌐 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"🗄️ DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"🌐 DATABASE HOST: {settings.DATABASES['default']['HOST']}")
        print(f"📊 DATABASE NAME: {settings.DATABASES['default']['NAME']}")
        print(f"👤 DATABASE USER: {settings.DATABASES['default']['USER']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def testar_conexao_banco():
    """Testa a conexão com o banco"""
    print("\n🔗 Testando conexão com o banco...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result and result[0] == 1:
            print("✅ Conexão com banco estabelecida")
            return True
        else:
            print("❌ Conexão com banco falhou")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def verificar_arquivos_estaticos():
    """Verifica configuração de arquivos estáticos"""
    print("\n📁 Verificando arquivos estáticos...")
    
    try:
        from django.conf import settings
        
        print(f"📂 STATIC_ROOT: {settings.STATIC_ROOT}")
        print(f"🌐 STATIC_URL: {settings.STATIC_URL}")
        print(f"📦 STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
        
        # Verificar se o diretório existe
        if os.path.exists(settings.STATIC_ROOT):
            print("✅ STATIC_ROOT existe")
        else:
            print("⚠️  STATIC_ROOT não existe")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração de arquivos estáticos: {e}")
        return False

def verificar_dados_banco():
    """Verifica se há dados no banco"""
    print("\n📊 Verificando dados no banco...")
    
    try:
        from django.contrib.auth.models import User
        from militares.models import Militar, ComissaoPromocao
        
        # Contar registros
        total_usuarios = User.objects.count()
        total_militares = Militar.objects.count()
        total_comissoes = ComissaoPromocao.objects.count()
        
        print(f"👥 Usuários: {total_usuarios}")
        print(f"🎖️  Militares: {total_militares}")
        print(f"🏛️  Comissões: {total_comissoes}")
        
        if total_usuarios > 0:
            print("✅ Dados encontrados no banco")
            return True
        else:
            print("⚠️  Nenhum dado encontrado no banco")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 VERIFICAÇÃO DE CONFIGURAÇÃO DO RENDER")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    verificar_variaveis_ambiente()
    
    # Testar configuração
    if not testar_configuracao_render():
        print("\n❌ Configuração do Render falhou")
        return False
    
    # Testar conexão com banco
    if not testar_conexao_banco():
        print("\n❌ Conexão com banco falhou")
        print("💡 Verifique:")
        print("   - DATABASE_URL no painel do Render")
        print("   - Credenciais do Supabase")
        print("   - Conectividade de rede")
        return False
    
    # Verificar arquivos estáticos
    verificar_arquivos_estaticos()
    
    # Verificar dados
    verificar_dados_banco()
    
    print("\n" + "=" * 50)
    print("✅ VERIFICAÇÃO CONCLUÍDA")
    print("=" * 50)
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Se tudo estiver OK, teste a aplicação no Render")
    print("2. Se houver problemas, verifique os logs no painel do Render")
    print("3. Se necessário, execute a migração de dados")
    print()
    print("🔧 Para migrar dados:")
    print("   python migrar_dados_completos_supabase.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Verificação falhou. Verifique os erros acima.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Verificação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 