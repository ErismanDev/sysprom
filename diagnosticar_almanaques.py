#!/usr/bin/env python
"""
Script para diagnosticar por que o usuário admin não consegue ver os almanaques
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import UsuarioFuncao, MembroComissao, CargoFuncao
from django.test import RequestFactory
from militares.context_processors import menu_permissions_processor

def diagnosticar_almanaques():
    """Diagnostica por que o usuário admin não consegue ver os almanaques"""
    
    print("🔍 DIAGNÓSTICO: POR QUE NÃO VEJO OS ALMANAQUES?")
    print("=" * 60)
    
    # Buscar usuário admin
    try:
        user_admin = User.objects.get(username='erisman')
        print(f"✅ Usuário encontrado: {user_admin.username}")
    except User.DoesNotExist:
        print("❌ Usuário 'erisman' não encontrado")
        return
    
    print(f"📊 Dados do usuário:")
    print(f"   • is_superuser: {user_admin.is_superuser}")
    print(f"   • is_staff: {user_admin.is_staff}")
    print(f"   • is_active: {user_admin.is_active}")
    
    # 1. Verificar funções do usuário
    print(f"\n1️⃣ FUNÇÕES DO USUÁRIO:")
    funcoes = UsuarioFuncao.objects.filter(usuario=user_admin, status='ATIVO')
    
    if funcoes.exists():
        for funcao in funcoes:
            print(f"   • {funcao.cargo_funcao.nome} (ID: {funcao.cargo_funcao.id})")
    else:
        print("   ❌ Nenhuma função ativa encontrada")
    
    # 2. Verificar se tem funções especiais
    print(f"\n2️⃣ FUNÇÕES ESPECIAIS:")
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções', 'Administrador do Sistema', 'Administrador']
    funcoes_especiais = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    
    if funcoes_especiais.exists():
        for funcao in funcoes_especiais:
            print(f"   ✅ {funcao.cargo_funcao.nome}")
    else:
        print("   ❌ Nenhuma função especial encontrada")
    
    # 3. Verificar membros de comissão
    print(f"\n3️⃣ MEMBROS DE COMISSÃO:")
    membros = MembroComissao.objects.filter(usuario=user_admin, ativo=True, comissao__status='ATIVA')
    
    if membros.exists():
        for membro in membros:
            print(f"   • {membro.comissao.tipo} - {membro.comissao.nome}")
            print(f"     Cargo: {membro.cargo}")
            print(f"     Presidente: {membro.eh_presidente()}")
    else:
        print("   ❌ Nenhum membro de comissão ativo encontrado")
    
    # 4. Testar context processor
    print(f"\n4️⃣ CONTEXT PROCESSOR:")
    factory = RequestFactory()
    request = factory.get('/')
    request.user = user_admin
    
    context = menu_permissions_processor(request)
    menu_permissions = context.get('menu_permissions', {})
    
    print(f"   • show_almanaques: {menu_permissions.get('show_almanaques', False)}")
    print(f"   • show_quadros_fixacao: {menu_permissions.get('show_quadros_fixacao', False)}")
    print(f"   • show_comissoes: {menu_permissions.get('show_comissoes', False)}")
    print(f"   • is_special: {menu_permissions.get('is_special', False)}")
    print(f"   • is_cpo: {menu_permissions.get('is_cpo', False)}")
    print(f"   • is_cpp: {menu_permissions.get('is_cpp', False)}")
    
    # 5. Verificar lógica da view almanaque_list
    print(f"\n5️⃣ LÓGICA DA VIEW ALMANAQUE_LIST:")
    
    # Verificar se tem funções especiais
    funcoes_ativas = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    if funcoes_ativas.exists():
        print("   ✅ Tem funções especiais - deveria ver todos os almanaques")
        print("   📋 Almanaques que deveria ver: TODOS (ativo=True)")
    else:
        print("   ❌ Não tem funções especiais")
        
        # Verificar se é membro de comissão
        if membros.exists():
            tem_cpo = membros.filter(comissao__tipo='CPO').exists()
            tem_cpp = membros.filter(comissao__tipo='CPP').exists()
            
            print(f"   • É membro CPO: {tem_cpo}")
            print(f"   • É membro CPP: {tem_cpp}")
            
            if tem_cpo and tem_cpp:
                print("   ✅ Membro das duas comissões - deveria ver TODOS os almanaques")
            elif tem_cpo:
                print("   ✅ Membro CPO - deveria ver almanaques de OFICIAIS")
            elif tem_cpp:
                print("   ✅ Membro CPP - deveria ver almanaques de PRACAS")
            else:
                print("   ❌ Membro de comissão mas não CPO nem CPP")
        else:
            print("   ❌ Não é membro de comissão")
            print("   📋 Almanaques que deveria ver: NENHUM")
    
    # 6. Verificar se há almanaques no banco
    print(f"\n6️⃣ ALMANAQUES NO BANCO:")
    from militares.models import AlmanaqueMilitar
    
    total_almanaques = AlmanaqueMilitar.objects.count()
    almanaques_ativos = AlmanaqueMilitar.objects.filter(ativo=True).count()
    
    print(f"   • Total de almanaques: {total_almanaques}")
    print(f"   • Almanaques ativos: {almanaques_ativos}")
    
    if almanaques_ativos > 0:
        print("   ✅ Existem almanaques ativos no banco")
        
        # Listar alguns almanaques
        almanaques = AlmanaqueMilitar.objects.filter(ativo=True)[:5]
        for almanaque in almanaques:
            print(f"     - {almanaque.titulo} ({almanaque.tipo})")
    else:
        print("   ❌ Nenhum almanaque ativo encontrado")
    
    # 7. Recomendações
    print(f"\n7️⃣ RECOMENDAÇÕES:")
    
    if not funcoes_especiais.exists() and not membros.exists():
        print("   🔧 SOLUÇÃO: Adicionar função especial ou membro de comissão")
        print("   📝 Opções:")
        print("     1. Adicionar função 'Diretor de Gestão de Pessoas'")
        print("     2. Adicionar função 'Chefe da Seção de Promoções'")
        print("     3. Adicionar função 'Administrador do Sistema'")
        print("     4. Adicionar como membro de CPO ou CPP")
    
    elif almanaques_ativos == 0:
        print("   🔧 SOLUÇÃO: Criar almanaques no sistema")
        print("   📝 Acesse: /militares/almanaques/novo/")
    
    else:
        print("   ✅ Tudo parece estar configurado corretamente")
        print("   🔍 Verifique se o menu está aparecendo no template")

if __name__ == "__main__":
    diagnosticar_almanaques() 