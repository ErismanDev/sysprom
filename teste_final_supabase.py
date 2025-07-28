#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste Final do Supabase
"""

import os
import sys
import django

print("=== Teste Final do Supabase ===")

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings_supabase')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from militares.models import CargoFuncao, Militar

try:
    print("1. Testando conexão com banco...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"   ✅ PostgreSQL: {version[0]}")
    
    print("2. Verificando usuários...")
    user_count = User.objects.count()
    print(f"   ✅ Usuários no banco: {user_count}")
    
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"   ✅ Admin encontrado: {admin_user.username}")
    else:
        print("   ❌ Admin não encontrado")
    
    print("3. Verificando cargos/funções...")
    cargo_count = CargoFuncao.objects.count()
    print(f"   ✅ Cargos no banco: {cargo_count}")
    
    cargo_padrao = CargoFuncao.objects.filter(nome='Usuário').first()
    if cargo_padrao:
        print(f"   ✅ Cargo padrão encontrado: {cargo_padrao.nome}")
    else:
        print("   ❌ Cargo padrão não encontrado")
    
    print("4. Verificando militares...")
    militar_count = Militar.objects.count()
    print(f"   ✅ Militares no banco: {militar_count}")
    
    print("5. Testando operações básicas...")
    # Testar criação de um cargo
    novo_cargo, created = CargoFuncao.objects.get_or_create(
        nome='Teste Supabase',
        defaults={
            'descricao': 'Cargo de teste para verificar Supabase',
            'ativo': True,
            'ordem': 999
        }
    )
    if created:
        print(f"   ✅ Cargo de teste criado: {novo_cargo.nome}")
        # Remover o cargo de teste
        novo_cargo.delete()
        print("   ✅ Cargo de teste removido")
    else:
        print(f"   ✅ Cargo de teste já existia: {novo_cargo.nome}")
    
    print("\n=== Teste Final Concluído com Sucesso! ===")
    print("🎉 O Supabase está funcionando perfeitamente!")
    print("\n📋 Resumo da Configuração:")
    print(f"   • PostgreSQL: {version[0]}")
    print(f"   • Usuários: {user_count}")
    print(f"   • Cargos: {cargo_count}")
    print(f"   • Militares: {militar_count}")
    print("\n🚀 Para usar em produção:")
    print("   python manage.py runserver --settings=sepromcbmepi.settings_supabase")
    print("\n🔧 Para usar em desenvolvimento (banco local):")
    print("   python manage.py runserver")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc() 