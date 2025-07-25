#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import Militar, UsuarioFuncao, CargoFuncao

def verificar_funcoes_especiais():
    print("🔍 VERIFICANDO FUNÇÕES ESPECIAIS")
    print("=" * 50)
    
    # 1. Verificar se as funções especiais existem
    funcoes_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções']
    
    print("📋 Funções especiais que permitem CRUD completo:")
    for funcao_nome in funcoes_especiais:
        try:
            cargo = CargoFuncao.objects.get(nome=funcao_nome)
            usuarios_cargo = UsuarioFuncao.objects.filter(
                cargo_funcao=cargo,
                status='AT'
            ).count()
            print(f"   ✅ {funcao_nome}: {usuarios_cargo} usuários ativos")
        except CargoFuncao.DoesNotExist:
            print(f"   ❌ {funcao_nome}: NÃO CADASTRADA")
    
    # 2. Listar usuários com funções especiais
    print(f"\n👥 Usuários com funções especiais:")
    usuarios_especiais = User.objects.filter(
        funcoes__cargo_funcao__nome__in=funcoes_especiais,
        funcoes__status='AT'
    ).distinct()
    
    if usuarios_especiais.exists():
        for usuario in usuarios_especiais:
            funcoes = UsuarioFuncao.objects.filter(
                usuario=usuario,
                status='AT',
                cargo_funcao__nome__in=funcoes_especiais
            )
            print(f"   - {usuario.get_full_name()} ({usuario.username})")
            for funcao in funcoes:
                print(f"     • {funcao.cargo_funcao.nome}")
    else:
        print("   Nenhum usuário encontrado com funções especiais")
    
    # 3. Verificar todas as funções cadastradas
    print(f"\n🏷️ Todas as funções/cargos cadastrados:")
    todos_cargos = CargoFuncao.objects.all().order_by('nome')
    for cargo in todos_cargos:
        usuarios_cargo = UsuarioFuncao.objects.filter(
            cargo_funcao=cargo,
            status='AT'
        ).count()
        print(f"   - {cargo.nome}: {usuarios_cargo} usuários")
    
    # 4. Resumo das regras implementadas
    print(f"\n🔒 REGRAS DE ACESSO IMPLEMENTADAS:")
    print("   ✅ Usuários de comissão (CPO/CPP) podem apenas VISUALIZAR:")
    print("      - Fichas de conceito")
    print("      - Cadastro de militares")
    print("      - Documentos")
    print("   ✅ Usuários CPO podem acessar áreas CPO")
    print("   ✅ Usuários CPP podem acessar áreas CPP")
    print("   ✅ FUNÇÕES ESPECIAIS podem fazer CRUD COMPLETO:")
    print("      - Diretor de Gestão de Pessoas")
    print("      - Chefe da Seção de Promoções")
    print("      (Podem criar, editar e excluir fichas de conceito e cadastro de militares)")

if __name__ == "__main__":
    verificar_funcoes_especiais() 