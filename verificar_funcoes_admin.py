#!/usr/bin/env python
"""
Script para verificar as funções específicas do usuário admin
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, CargoFuncao

def verificar_funcoes_admin():
    """Verifica as funções específicas do usuário admin"""
    
    print("🔍 VERIFICANDO FUNÇÕES DO ADMIN")
    print("=" * 60)
    
    # Buscar usuário admin
    try:
        user_admin = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user_admin.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    # Verificar todas as funções
    print(f"\n1️⃣ TODAS AS FUNÇÕES:")
    funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
    
    if funcoes.exists():
        for funcao in funcoes:
            print(f"   • {funcao.cargo_funcao.nome} (ID: {funcao.cargo_funcao.id})")
    else:
        print("   ❌ Nenhuma função ativa encontrada")
    
    # Verificar funções especiais necessárias para almanaques
    print(f"\n2️⃣ FUNÇÕES ESPECIAIS (necessárias para almanaques):")
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções']
    funcoes_especiais = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função especial encontrada")
        print("   🔧 Isso explica por que não vê os almanaques!")
    
    # Verificar se existem esses cargos no sistema
    print(f"\n3️⃣ CARGOS ESPECIAIS NO SISTEMA:")
    for cargo_nome in cargos_especiais:
        try:
            cargo = CargoFuncao.objects.get(nome=cargo_nome)
            print(f"   ✅ {cargo_nome} (ID: {cargo.id})")
        except CargoFuncao.DoesNotExist:
            print(f"   ❌ {cargo_nome} - NÃO EXISTE no sistema")
    
    # Verificar outras funções que podem dar acesso
    print(f"\n4️⃣ OUTRAS FUNÇÕES QUE PODEM DAR ACESSO:")
    outros_cargos = ['Administrador do Sistema', 'Administrador']
    outras_funcoes = funcoes.filter(cargo_funcao__nome__in=outros_cargos)
    
    if outras_funcoes.exists():
        for funcao in outras_funcoes:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função administrativa encontrada")
    
    # Recomendações
    print(f"\n5️⃣ RECOMENDAÇÕES:")
    
    if not funcoes_especiais.exists():
        print("   🔧 SOLUÇÃO: Adicionar função especial")
        print("   📝 Opções:")
        print("     1. Adicionar função 'Diretor de Gestão de Pessoas'")
        print("     2. Adicionar função 'Chefe da Seção de Promoções'")
        print("     3. Modificar a view para incluir superusuários")
        
        # Verificar se os cargos existem
        for cargo_nome in cargos_especiais:
            try:
                cargo = CargoFuncao.objects.get(nome=cargo_nome)
                print(f"     - Cargo '{cargo_nome}' existe (ID: {cargo.id})")
            except CargoFuncao.DoesNotExist:
                print(f"     - Cargo '{cargo_nome}' NÃO existe - precisa ser criado")
    else:
        print("   ✅ Já tem funções especiais - problema pode ser outro")

if __name__ == "__main__":
    verificar_funcoes_admin() 