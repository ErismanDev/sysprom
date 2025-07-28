#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste das variáveis de ambiente
"""

import os
from dotenv import load_dotenv

print("🔧 Testando variáveis de ambiente...")
print("=" * 50)

# Carregar variáveis de ambiente
load_dotenv()

# Lista de variáveis para testar
variaveis = [
    'SUPABASE_HOST',
    'SUPABASE_PORT', 
    'SUPABASE_DATABASE',
    'SUPABASE_USER',
    'SUPABASE_PASSWORD',
    'SECRET_KEY',
    'DEBUG',
    'ALLOWED_HOSTS'
]

print("📋 Variáveis carregadas:")
for var in variaveis:
    valor = os.environ.get(var, 'NÃO DEFINIDA')
    if 'PASSWORD' in var:
        valor = '*' * len(valor) if valor != 'NÃO DEFINIDA' else valor
    print(f"   • {var}: {valor}")

print("\n" + "=" * 50)
print("✅ Teste concluído!")

# Testar se o Django consegue carregar as configurações
try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')
    django.setup()
    
    from django.conf import settings
    print("\n🔍 Testando configurações do Django:")
    print(f"   • DEBUG: {settings.DEBUG}")
    print(f"   • ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   • DATABASE HOST: {settings.DATABASES['default']['HOST']}")
    print(f"   • DATABASE NAME: {settings.DATABASES['default']['NAME']}")
    print(f"   • DATABASE USER: {settings.DATABASES['default']['USER']}")
    
    print("\n🎉 Todas as configurações estão funcionando!")
    
except Exception as e:
    print(f"\n❌ Erro ao testar Django: {e}") 