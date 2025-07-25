#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao, UsuarioFuncao
from django.contrib.auth.models import User

def verificar_cargos_cpo_cpp():
    print("🔍 Verificando cargos CPO e CPP no sistema...")
    print("-" * 60)
    
    # 1. Buscar cargos CPO
    cargos_cpo = CargoFuncao.objects.filter(nome__icontains='CPO').order_by('nome')
    print(f"\n🎖️  CARGOS CPO (Comissão de Promoções de Oficiais):")
    if cargos_cpo.exists():
        for cargo in cargos_cpo:
            usuarios_count = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo,
                status='ATIVO'
            ).count()
            print(f"   ✅ {cargo.nome} ({usuarios_count} usuários)")
    else:
        print("   ❌ Nenhum cargo CPO encontrado")
    
    # 2. Buscar cargos CPP
    cargos_cpp = CargoFuncao.objects.filter(nome__icontains='CPP').order_by('nome')
    print(f"\n🎖️  CARGOS CPP (Comissão de Promoções de Praças):")
    if cargos_cpp.exists():
        for cargo in cargos_cpp:
            usuarios_count = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo,
                status='ATIVO'
            ).count()
            print(f"   ✅ {cargo.nome} ({usuarios_count} usuários)")
    else:
        print("   ❌ Nenhum cargo CPP encontrado")
    
    # 3. Buscar todos os cargos para referência
    print(f"\n📋 TODOS OS CARGOS DISPONÍVEIS:")
    todos_cargos = CargoFuncao.objects.filter(ativo=True).order_by('nome')
    for cargo in todos_cargos:
        usuarios_count = UsuarioFuncao.objects.filter(
            cargo_funcao=cargo,
            status='ATIVO'
        ).count()
        print(f"   - {cargo.nome} ({usuarios_count} usuários)")
    
    # 4. Verificar usuários com funções CPO
    print(f"\n👥 USUÁRIOS COM FUNÇÕES CPO:")
    usuarios_cpo = UsuarioFuncao.objects.filter(
        cargo_funcao__nome__icontains='CPO',
        status='ATIVO'
    ).select_related('usuario', 'cargo_funcao')
    
    if usuarios_cpo.exists():
        for funcao in usuarios_cpo:
            print(f"   👤 {funcao.usuario.get_full_name()} ({funcao.usuario.username}): {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhum usuário com função CPO encontrado")
    
    # 5. Verificar usuários com funções CPP
    print(f"\n👥 USUÁRIOS COM FUNÇÕES CPP:")
    usuarios_cpp = UsuarioFuncao.objects.filter(
        cargo_funcao__nome__icontains='CPP',
        status='ATIVO'
    ).select_related('usuario', 'cargo_funcao')
    
    if usuarios_cpp.exists():
        for funcao in usuarios_cpp:
            print(f"   👤 {funcao.usuario.get_full_name()} ({funcao.usuario.username}): {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhum usuário com função CPP encontrado")

if __name__ == '__main__':
    verificar_cargos_cpo_cpp() 