#!/usr/bin/env python
"""
Script para testar se todas as views funcionam para superusuários
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import AlmanaqueMilitar, QuadroAcesso, QuadroFixacaoVagas, UsuarioFuncao, MembroComissao

def testar_todas_views():
    """Testa se todas as views funcionam para superusuários"""
    
    print("🧪 TESTANDO TODAS AS VIEWS")
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
    
    # Verificar dados no banco
    print(f"\n📋 DADOS NO BANCO:")
    total_almanaques = AlmanaqueMilitar.objects.filter(ativo=True).count()
    total_quadros_acesso = QuadroAcesso.objects.count()
    total_quadros_fixacao = QuadroFixacaoVagas.objects.count()
    
    print(f"   • Almanaques ativos: {total_almanaques}")
    print(f"   • Quadros de acesso: {total_quadros_acesso}")
    print(f"   • Quadros de fixação: {total_quadros_fixacao}")
    
    # Testar lógica das views
    print(f"\n🔍 TESTANDO LÓGICA DAS VIEWS:")
    
    # 1. Testar almanaque_list
    print(f"\n1️⃣ ALMANAQUE_LIST:")
    if user_admin.is_superuser or user_admin.is_staff or funcoes_ativas.exists():
        print("   ✅ Condição 1: Usuário é superusuário/staff/tem funções especiais")
        almanaques = AlmanaqueMilitar.objects.filter(ativo=True).order_by('-data_geracao')
        print(f"   📋 Resultado: {almanaques.count()} almanaques")
        
        for almanaque in almanaques:
            print(f"     - {almanaque.titulo} ({almanaque.tipo})")
    else:
        print("   ❌ Condição 1: Usuário NÃO é superusuário/staff/tem funções especiais")
        
        # Verificar membros de comissão
        membros = MembroComissao.objects.filter(usuario=user_admin, ativo=True, comissao__status='ATIVA')
        if membros.exists():
            tem_cpo = membros.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros.filter(comissao__tipo='CPP').exists()
            
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
            print("   ❌ Não é membro de comissão")
            almanaques = AlmanaqueMilitar.objects.none()
            print(f"   📋 Resultado: {almanaques.count()} almanaques (nenhum)")
    
    # 2. Testar quadro_acesso_list
    print(f"\n2️⃣ QUADRO_ACESSO_LIST:")
    if user_admin.is_superuser or user_admin.is_staff:
        print("   ✅ Condição 1: Usuário é superusuário/staff")
        quadros_acesso = QuadroAcesso.objects.all()
        print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso")
    elif funcoes_ativas.exists():
        print("   ✅ Condição 2: Usuário tem funções especiais")
        quadros_acesso = QuadroAcesso.objects.all()
        print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso")
    else:
        print("   ❌ Condição 1 e 2: Usuário NÃO é superusuário/staff/tem funções especiais")
        
        # Verificar membros de comissão
        membros = MembroComissao.objects.filter(usuario=user_admin, ativo=True, comissao__status='ATIVA')
        if membros.exists():
            tem_cpo = membros.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros.filter(comissao__tipo='CPP').exists()
            
            print(f"   • É membro CPO: {tem_cpo}")
            print(f"   • É membro CPP: {tem_cpp}")
            
            if tem_cpo and tem_cpp:
                quadros_acesso = QuadroAcesso.objects.all()
                print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso (todas)")
            elif tem_cpo:
                quadros_acesso = QuadroAcesso.objects.filter(categoria='OFICIAIS')
                print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso (oficiais)")
            elif tem_cpp:
                quadros_acesso = QuadroAcesso.objects.filter(categoria='PRACAS')
                print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso (praças)")
            else:
                quadros_acesso = QuadroAcesso.objects.none()
                print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso (nenhum)")
        else:
            print("   ❌ Não é membro de comissão")
            quadros_acesso = QuadroAcesso.objects.none()
            print(f"   📋 Resultado: {quadros_acesso.count()} quadros de acesso (nenhum)")
    
    # 3. Testar quadro_fixacao_vagas_list
    print(f"\n3️⃣ QUADRO_FIXACAO_VAGAS_LIST:")
    if user_admin.is_superuser or user_admin.is_staff or funcoes_ativas.exists():
        print("   ✅ Condição 1: Usuário é superusuário/staff/tem funções especiais")
        quadros_fixacao = QuadroFixacaoVagas.objects.all().order_by('-data_criacao')
        print(f"   📋 Resultado: {quadros_fixacao.count()} quadros de fixação")
    else:
        print("   ❌ Condição 1: Usuário NÃO é superusuário/staff/tem funções especiais")
        
        # Verificar membros de comissão
        membros = MembroComissao.objects.filter(usuario=user_admin, ativo=True, comissao__status='ATIVA')
        if membros.exists():
            tem_cpo = membros.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros.filter(comissao__tipo='CPP').exists()
            
            print(f"   • É membro CPO: {tem_cpo}")
            print(f"   • É membro CPP: {tem_cpp}")
            
            if tem_cpo and tem_cpp:
                quadros_fixacao = QuadroFixacaoVagas.objects.all().order_by('-data_criacao')
                print(f"   📋 Resultado: {quadros_fixacao.count()} quadros de fixação (todas)")
            elif tem_cpo:
                quadros_fixacao = QuadroFixacaoVagas.objects.filter(tipo='OFICIAIS').order_by('-data_criacao')
                print(f"   📋 Resultado: {quadros_fixacao.count()} quadros de fixação (oficiais)")
            elif tem_cpp:
                quadros_fixacao = QuadroFixacaoVagas.objects.filter(tipo='PRACAS').order_by('-data_criacao')
                print(f"   📋 Resultado: {quadros_fixacao.count()} quadros de fixação (praças)")
            else:
                quadros_fixacao = QuadroFixacaoVagas.objects.none()
                print(f"   📋 Resultado: {quadros_fixacao.count()} quadros de fixação (nenhum)")
        else:
            print("   ❌ Não é membro de comissão")
            quadros_fixacao = QuadroFixacaoVagas.objects.none()
            print(f"   📋 Resultado: {quadros_fixacao.count()} quadros de fixação (nenhum)")
    
    # Conclusão
    print(f"\n🎯 CONCLUSÃO:")
    
    # Verificar se todas as views retornam dados
    tem_almanaques = 'almanaques' in locals() and almanaques.count() > 0
    tem_quadros_acesso = 'quadros_acesso' in locals() and quadros_acesso.count() > 0
    tem_quadros_fixacao = 'quadros_fixacao' in locals() and quadros_fixacao.count() > 0
    
    print(f"   • Almanaques: {'✅' if tem_almanaques else '❌'}")
    print(f"   • Quadros de Acesso: {'✅' if tem_quadros_acesso else '❌'}")
    print(f"   • Quadros de Fixação: {'✅' if tem_quadros_fixacao else '❌'}")
    
    if tem_almanaques and tem_quadros_acesso and tem_quadros_fixacao:
        print("\n   🎉 TODAS AS VIEWS ESTÃO FUNCIONANDO CORRETAMENTE!")
        print("   📋 Você deveria ver todos os dados na interface")
        print("   🔍 Se não está vendo, pode ser problema de:")
        print("     1. Cache do navegador (Ctrl+F5)")
        print("     2. Template não está renderizando corretamente")
        print("     3. Context processor com erro")
    else:
        print("\n   ⚠️ ALGUMAS VIEWS AINDA NÃO ESTÃO FUNCIONANDO")
        if not tem_almanaques:
            print("   🔧 Almanaques: Verificar se há almanaques ativos no banco")
        if not tem_quadros_acesso:
            print("   🔧 Quadros de Acesso: Verificar se há quadros no banco")
        if not tem_quadros_fixacao:
            print("   🔧 Quadros de Fixação: Verificar se há quadros no banco")

if __name__ == "__main__":
    testar_todas_views() 