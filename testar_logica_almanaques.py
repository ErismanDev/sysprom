#!/usr/bin/env python
"""
Script para testar apenas a lógica da view almanaque_list
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import AlmanaqueMilitar, UsuarioFuncao, MembroComissao

def testar_logica_almanaques():
    """Testa apenas a lógica da view almanaque_list"""
    
    print("🧪 TESTANDO LÓGICA DA VIEW ALMANAQUES")
    print("=" * 60)
    
    # Buscar usuário admin
    try:
        user_admin = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user_admin.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    # Verificar dados do usuário
    print(f"📊 Dados do usuário:")
    print(f"   • is_superuser: {user_admin.is_superuser}")
    print(f"   • is_staff: {user_admin.is_staff}")
    
    # Verificar funções especiais
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    funcoes_ativas = UsuarioFuncao.objects.filter(
        usuario=user_admin,
        cargo_funcao__nome__in=cargos_especiais,
        status='ATIVO',
    )
    
    print(f"   • Tem funções especiais: {funcoes_ativas.exists()}")
    if funcoes_ativas.exists():
        for funcao in funcoes_ativas:
            print(f"     - {funcao.cargo_funcao.nome}")
    
    # Verificar almanaques no banco
    print(f"\n📋 ALMANAQUES NO BANCO:")
    total_almanaques = AlmanaqueMilitar.objects.count()
    almanaques_ativos = AlmanaqueMilitar.objects.filter(ativo=True).count()
    
    print(f"   • Total de almanaques: {total_almanaques}")
    print(f"   • Almanaques ativos: {almanaques_ativos}")
    
    if almanaques_ativos > 0:
        almanaques = AlmanaqueMilitar.objects.filter(ativo=True)
        for almanaque in almanaques:
            print(f"     - {almanaque.titulo} ({almanaque.tipo})")
    
    # Simular a lógica da view
    print(f"\n🔍 SIMULANDO LÓGICA DA VIEW:")
    
    # Primeira condição: superusuário, staff ou funções especiais
    if user_admin.is_superuser or user_admin.is_staff or funcoes_ativas.exists():
        print("   ✅ Condição 1: Usuário é superusuário/staff/tem funções especiais")
        almanaques = AlmanaqueMilitar.objects.filter(ativo=True).order_by('-data_geracao')
        print(f"   📋 Resultado: {almanaques.count()} almanaques")
        
        for almanaque in almanaques:
            print(f"     - {almanaque.titulo} ({almanaque.tipo})")
            
    else:
        print("   ❌ Condição 1: Usuário NÃO é superusuário/staff/tem funções especiais")
        
        # Segunda condição: membros de comissão
        membros_comissao = MembroComissao.objects.filter(
            usuario=user_admin,
            ativo=True,
            comissao__status='ATIVA'
        )
        
        if membros_comissao.exists():
            print("   ✅ Condição 2: Usuário é membro de comissão")
            
            tem_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
            
            print(f"   • É membro CPO: {tem_cpo}")
            print(f"   • É membro CPP: {tem_cpp}")
            
            if tem_cpo and tem_cpp:
                almanaques = AlmanaqueMilitar.objects.filter(ativo=True).order_by('-data_geracao')
                print(f"   📋 Resultado: {almanaques.count()} almanaques (todas)")
            elif tem_cpo:
                almanaques = AlmanaqueMilitar.objects.filter(tipo='OFICIAIS', ativo=True).order_by('-data_geracao')
                print(f"   📋 Resultado: {almanaques.count()} almanaques (oficiais)")
            elif tem_cpp:
                almanaques = AlmanaqueMilitar.objects.filter(tipo='PRACAS', ativo=True).order_by('-data_geracao')
                print(f"   📋 Resultado: {almanaques.count()} almanaques (praças)")
            else:
                almanaques = AlmanaqueMilitar.objects.none()
                print(f"   📋 Resultado: {almanaques.count()} almanaques (nenhum)")
        else:
            print("   ❌ Condição 2: Usuário NÃO é membro de comissão")
            almanaques = AlmanaqueMilitar.objects.none()
            print(f"   📋 Resultado: {almanaques.count()} almanaques (nenhum)")
    
    # Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    if almanaques.count() > 0:
        print("   ✅ A lógica da view está funcionando corretamente!")
        print("   📋 Você deveria ver os almanaques na interface")
        print("   🔍 Se não está vendo, pode ser problema de:")
        print("     1. Cache do navegador (Ctrl+F5)")
        print("     2. Template não está renderizando corretamente")
        print("     3. Context processor com erro")
    else:
        print("   ❌ A lógica da view não está retornando almanaques")
        print("   🔧 Verificar configuração de permissões")

if __name__ == "__main__":
    testar_logica_almanaques() 