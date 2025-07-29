#!/usr/bin/env python3
"""
Script para testar se o app.py está funcionando corretamente
"""

import os
import sys
import django

def testar_configuracao():
    """Testa se a configuração está funcionando"""
    
    print("🧪 Testando configuração do app.py...")
    
    try:
        # Configurar ambiente como no Render
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_render')
        
        # Configurar Django
        django.setup()
        
        print("✅ Django configurado com sucesso")
        
        # Importar configurações
        from django.conf import settings
        
        print(f"📊 DEBUG: {settings.DEBUG}")
        print(f"🌐 ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"🗄️ DATABASE ENGINE: {settings.DATABASES['default']['ENGINE']}")
        
        # Testar importação do app
        from app import app
        print("✅ app.py importado com sucesso")
        
        # Testar se o pytz está funcionando
        try:
            import pytz
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            print(f"✅ pytz funcionando - Timezone Brasília: {brasilia_tz}")
        except ImportError as e:
            print(f"❌ Erro ao importar pytz: {e}")
            return False
        
        print("\n✅ Configuração testada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar configuração: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_importacoes():
    """Testa se todas as importações necessárias funcionam"""
    
    print("\n🔍 Testando importações...")
    
    try:
        # Testar importação do settings_render
        from sepromcbmepi import settings_render
        print("✅ settings_render importado")
        
        # Testar importação do wsgi
        from sepromcbmepi.wsgi import application
        print("✅ wsgi.application importado")
        
        # Testar importação do app
        from app import app
        print("✅ app importado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 Testando configuração para Render")
    print("=" * 50)
    
    # Testar importações
    if not testar_importacoes():
        print("\n❌ Falha nas importações básicas")
        return
    
    # Testar configuração
    if testar_configuracao():
        print("\n🎉 Tudo funcionando! Pronto para deploy no Render.")
        print("\n📋 Próximos passos:")
        print("1. Faça commit das alterações")
        print("2. Faça push para o repositório")
        print("3. O Render irá fazer deploy automaticamente")
    else:
        print("\n❌ Há problemas na configuração que precisam ser corrigidos")

if __name__ == "__main__":
    main() 