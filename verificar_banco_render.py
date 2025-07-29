#!/usr/bin/env python3
"""
Script para verificar a configuração do banco de dados no Render
"""

import os
import sys
import django

def verificar_configuracao_banco():
    """Verifica se a configuração do banco está correta"""
    
    print("🔍 Verificando configuração do banco de dados...")
    
    # Configurar ambiente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_render')
    
    try:
        # Configurar Django
        django.setup()
        
        # Importar configurações
        from django.conf import settings
        
        print(f"🗄️ DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
        print(f"🌐 DATABASE HOST: {settings.DATABASES['default']['HOST']}")
        print(f"📊 DATABASE NAME: {settings.DATABASES['default']['NAME']}")
        print(f"👤 DATABASE USER: {settings.DATABASES['default']['USER']}")
        
        # Verificar se a DATABASE_URL está definida
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            print(f"🔗 DATABASE_URL: {database_url[:50]}...")
        else:
            print("⚠️  DATABASE_URL não definida")
        
        # Testar conexão com o banco
        print("\n🧪 Testando conexão com o banco...")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Conexão bem-sucedida: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração do banco: {e}")
        return False

def verificar_arquivos_estaticos():
    """Verifica se os arquivos estáticos estão configurados corretamente"""
    
    print("\n📁 Verificando configuração de arquivos estáticos...")
    
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

def main():
    """Função principal"""
    
    print("🚀 Verificação de Configuração do Render")
    print("=" * 50)
    
    # Verificar banco
    banco_ok = verificar_configuracao_banco()
    
    # Verificar arquivos estáticos
    static_ok = verificar_arquivos_estaticos()
    
    if banco_ok and static_ok:
        print("\n✅ Configuração verificada com sucesso!")
        print("\n📋 Se ainda houver problemas:")
        print("1. Verifique a DATABASE_URL no painel do Render")
        print("2. Confirme que a senha do Supabase está correta")
        print("3. Verifique se o banco está acessível")
    else:
        print("\n❌ Há problemas na configuração que precisam ser corrigidos")

if __name__ == "__main__":
    main() 