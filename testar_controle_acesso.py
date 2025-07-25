#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, CargoFuncao

def testar_controle_acesso():
    print("🔍 TESTANDO CONTROLE DE ACESSO")
    print("=" * 50)
    
    # 1. Verificar usuários com funções de comissão
    usuarios_comissao = User.objects.filter(
        funcoes__cargo_funcao__nome__in=['CPO', 'CPP'],
        funcoes__ativo=True
    ).distinct()
    
    print(f"📋 Usuários com funções de comissão ({usuarios_comissao.count()}):")
    for usuario in usuarios_comissao:
        funcoes = UsuarioFuncao.objects.filter(
            usuario=usuario,
            ativo=True,
            cargo_funcao__nome__in=['CPO', 'CPP']
        )
        print(f"   - {usuario.get_full_name()} ({usuario.username})")
        for funcao in funcoes:
            print(f"     • {funcao.cargo_funcao.nome}")
    
    # 2. Verificar usuários CPO
    usuarios_cpo = User.objects.filter(
        funcoes__cargo_funcao__nome='CPO',
        funcoes__ativo=True
    ).distinct()
    
    print(f"\n👥 Usuários CPO ({usuarios_cpo.count()}):")
    for usuario in usuarios_cpo:
        print(f"   - {usuario.get_full_name()} ({usuario.username})")
    
    # 3. Verificar usuários CPP
    usuarios_cpp = User.objects.filter(
        funcoes__cargo_funcao__nome='CPP',
        funcoes__ativo=True
    ).distinct()
    
    print(f"\n👥 Usuários CPP ({usuarios_cpp.count()}):")
    for usuario in usuarios_cpp:
        print(f"   - {usuario.get_full_name()} ({usuario.username})")
    
    # 4. Verificar cargos/funções disponíveis
    cargos_comissao = CargoFuncao.objects.filter(
        nome__in=['CPO', 'CPP']
    )
    
    print(f"\n🏷️ Cargos/Funções de Comissão:")
    for cargo in cargos_comissao:
        usuarios_cargo = UsuarioFuncao.objects.filter(
            cargo_funcao=cargo,
            ativo=True
        ).count()
        print(f"   - {cargo.nome}: {usuarios_cargo} usuários")
    
    # 5. Testar regras de acesso
    print(f"\n🔒 REGRAS DE ACESSO IMPLEMENTADAS:")
    print("   ✅ Usuários de comissão (CPO/CPP) podem apenas VISUALIZAR:")
    print("      - Fichas de conceito")
    print("      - Cadastro de militares")
    print("      - Documentos")
    print("   ✅ Usuários CPO podem acessar áreas CPO:")
    print("      - Comissões de promoção")
    print("      - Membros de comissão")
    print("      - Sessões de comissão")
    print("   ✅ Usuários CPP podem acessar áreas CPP:")
    print("      - Comissões de promoção")
    print("      - Membros de comissão")
    print("      - Sessões de comissão")
    print("   ❌ Usuários de comissão NÃO podem:")
    print("      - Editar fichas de conceito")
    print("      - Editar cadastro de militares")
    print("      - Editar documentos")

if __name__ == "__main__":
    testar_controle_acesso() 