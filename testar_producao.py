#!/usr/bin/env python
"""
Script para testar configurações de produção
"""

import os
import sys
import django
from django.conf import settings

def testar_configuracoes_producao():
    """Testa as configurações de produção"""
    
    print("🧪 Testando Configurações de Produção AWS...")
    print("=" * 50)
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_aws_production')
    django.setup()
    
    # Testes
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ DATABASE: {settings.DATABASES['default']['ENGINE']}")
    print(f"✅ STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"✅ SECURE_SSL_REDIRECT: {settings.SECURE_SSL_REDIRECT}")
    print(f"✅ SECURE_BROWSER_XSS_FILTER: {settings.SECURE_BROWSER_XSS_FILTER}")
    
    # Testar conexão com banco
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão com banco: OK")
    except Exception as e:
        print(f"❌ Erro na conexão com banco: {e}")
    
    print("=" * 50)
    print("🎉 Teste de configurações concluído!")

if __name__ == "__main__":
    testar_configuracoes_producao() 