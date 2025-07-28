#!/usr/bin/env python3
"""
Script para testar a configuração de produção localmente
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def testar_configuracao_producao():
    """Testa a configuração de produção localmente"""
    
    print("🧪 Testando configuração de produção...")
    print("=" * 50)
    
    # Configurar ambiente
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_aws_production')
    os.environ.setdefault('DEBUG', 'False')
    
    # Verificar variáveis críticas
    variaveis_criticas = [
        'SECRET_KEY',
        'SUPABASE_DATABASE',
        'SUPABASE_USER',
        'SUPABASE_PASSWORD',
        'SUPABASE_HOST',
    ]
    
    print("📋 Verificando variáveis de ambiente:")
    for var in variaveis_criticas:
        valor = os.environ.get(var)
        if valor:
            print(f"   ✓ {var}: {'*' * len(valor) if 'PASSWORD' in var else valor}")
        else:
            print(f"   ✗ {var}: NÃO CONFIGURADA")
    
    print("\n" + "=" * 50)
    
    try:
        # Configurar Django
        django.setup()
        
        print("✅ Django configurado com sucesso!")
        
        # Testar conexão com banco
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Conexão com banco de dados OK!")
        
        # Testar collectstatic
        print("\n📦 Testando collectstatic...")
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--dry-run'])
        print("✅ Collectstatic OK!")
        
        # Testar migrações
        print("\n🔄 Testando migrações...")
        execute_from_command_line(['manage.py', 'showmigrations'])
        print("✅ Migrações OK!")
        
        print("\n" + "=" * 50)
        print("🎉 Configuração de produção testada com sucesso!")
        print("   O sistema está pronto para deploy no AWS Amplify.")
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        print("\n🔧 Possíveis soluções:")
        print("   1. Verifique as variáveis de ambiente")
        print("   2. Teste a conexão com o Supabase")
        print("   3. Execute 'python corrigir_migracoes_ckeditor.py'")
        return False
    
    return True

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    
    print("📦 Verificando dependências...")
    
    dependencias = [
        'django',
        'django_ckeditor_5',
        'psycopg2-binary',
        'gunicorn',
        'whitenoise',
        'dj-database-url',
        'python-dotenv',
    ]
    
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep.replace('-', '_'))
            print(f"   ✓ {dep}")
        except ImportError:
            print(f"   ✗ {dep} - FALTANDO")
            faltando.append(dep)
    
    if faltando:
        print(f"\n⚠️  Dependências faltando: {', '.join(faltando)}")
        print("   Execute: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

if __name__ == '__main__':
    print("🚀 Teste de Deploy Local - Sistema SEPROM")
    print("=" * 60)
    
    # Verificar dependências
    if not verificar_dependencias():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # Testar configuração
    if testar_configuracao_producao():
        print("\n🎯 Próximos passos:")
        print("   1. Configure as variáveis de ambiente no AWS Amplify")
        print("   2. Faça commit das correções")
        print("   3. Faça push para o repositório")
        print("   4. Monitore o deploy no console do Amplify")
    else:
        print("\n❌ Corrija os problemas antes de fazer o deploy")
        sys.exit(1) 