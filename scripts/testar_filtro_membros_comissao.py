#!/usr/bin/env python
"""
Script para testar a funcionalidade de filtro de membros por função do usuário
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import (
    ComissaoPromocao, MembroComissao, Militar, 
    UsuarioFuncao, CargoFuncao
)

def testar_filtro_membros_comissao():
    """Testa a funcionalidade de filtro de membros por função"""
    
    print("🧪 TESTANDO FILTRO DE MEMBROS POR FUNÇÃO")
    print("=" * 60)
    
    # 1. Verificar comissões existentes
    print("\n📋 1. COMISSÕES EXISTENTES:")
    comissoes = ComissaoPromocao.objects.all()
    for comissao in comissoes:
        print(f"   - {comissao.nome} ({comissao.get_tipo_display()}) - ID: {comissao.pk}")
    
    # 2. Verificar funções de usuário
    print("\n👥 2. FUNÇÕES DE USUÁRIO:")
    funcoes = UsuarioFuncao.objects.filter(status='ATIVO').select_related('usuario', 'cargo_funcao')
    for funcao in funcoes:
        print(f"   - {funcao.usuario.username}: {funcao.cargo_funcao.nome} ({funcao.get_tipo_funcao_display()})")
    
    # 3. Verificar militares por categoria
    print("\n🎖️  3. MILITARES POR CATEGORIA:")
    
    # Oficiais
    oficiais = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS']
    ).order_by('posto_graduacao', 'nome_completo')
    print(f"   Oficiais ({oficiais.count()}):")
    for militar in oficiais[:5]:  # Mostrar apenas os primeiros 5
        print(f"     - {militar.posto_graduacao} {militar.nome_completo}")
    if oficiais.count() > 5:
        print(f"     ... e mais {oficiais.count() - 5} oficiais")
    
    # Praças
    pracas = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
    ).order_by('posto_graduacao', 'nome_completo')
    print(f"   Praças ({pracas.count()}):")
    for militar in pracas[:5]:  # Mostrar apenas os primeiros 5
        print(f"     - {militar.posto_graduacao} {militar.nome_completo}")
    if pracas.count() > 5:
        print(f"     ... e mais {pracas.count() - 5} praças")
    
    # 4. Testar lógica de filtro
    print("\n🔍 4. TESTANDO LÓGICA DE FILTRO:")
    
    # Buscar uma comissão CPO
    comissao_cpo = ComissaoPromocao.objects.filter(tipo='CPO').first()
    if comissao_cpo:
        print(f"   Comissão CPO encontrada: {comissao_cpo.nome}")
        
        # Buscar uma função CPO
        funcao_cpo = UsuarioFuncao.objects.filter(
            cargo_funcao__nome__icontains='CPO',
            status='ATIVO'
        ).first()
        
        if funcao_cpo:
            print(f"   Função CPO encontrada: {funcao_cpo.cargo_funcao.nome}")
            print(f"   Usuário: {funcao_cpo.usuario.username}")
            
            # Simular filtro de oficiais
            oficiais_filtrados = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS']
            ).order_by('nome_completo')
            
            print(f"   Militares disponíveis para CPO: {oficiais_filtrados.count()}")
            for militar in oficiais_filtrados[:3]:
                print(f"     - {militar.posto_graduacao} {militar.nome_completo}")
        else:
            print("   ⚠️  Nenhuma função CPO encontrada")
    else:
        print("   ⚠️  Nenhuma comissão CPO encontrada")
    
    # Buscar uma comissão CPP
    comissao_cpp = ComissaoPromocao.objects.filter(tipo='CPP').first()
    if comissao_cpp:
        print(f"   Comissão CPP encontrada: {comissao_cpp.nome}")
        
        # Buscar uma função CPP
        funcao_cpp = UsuarioFuncao.objects.filter(
            cargo_funcao__nome__icontains='CPP',
            status='ATIVO'
        ).first()
        
        if funcao_cpp:
            print(f"   Função CPP encontrada: {funcao_cpp.cargo_funcao.nome}")
            print(f"   Usuário: {funcao_cpp.usuario.username}")
            
            # Simular filtro de praças
            pracas_filtradas = Militar.objects.filter(
                situacao='AT',
                posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
            ).order_by('nome_completo')
            
            print(f"   Militares disponíveis para CPP: {pracas_filtradas.count()}")
            for militar in pracas_filtradas[:3]:
                print(f"     - {militar.posto_graduacao} {militar.nome_completo}")
        else:
            print("   ⚠️  Nenhuma função CPP encontrada")
    else:
        print("   ⚠️  Nenhuma comissão CPP encontrada")
    
    # 5. Verificar membros existentes
    print("\n👥 5. MEMBROS EXISTENTES NAS COMISSÕES:")
    for comissao in comissoes:
        membros = comissao.membros.all()
        print(f"   {comissao.nome} ({comissao.get_tipo_display()}): {membros.count()} membros")
        for membro in membros[:3]:  # Mostrar apenas os primeiros 3
            print(f"     - {membro.militar.posto_graduacao} {membro.militar.nome_completo} ({membro.get_tipo_display()})")
        if membros.count() > 3:
            print(f"     ... e mais {membros.count() - 3} membros")
    
    print("\n✅ Teste concluído!")
    return True

if __name__ == '__main__':
    testar_filtro_membros_comissao() 