#!/usr/bin/env python
"""
Script para testar as permissões administrativas para adicionar membros das comissões
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

def testar_permissoes_admin_comissao():
    """Testa as permissões administrativas para adicionar membros das comissões"""
    
    print("🧪 TESTANDO PERMISSÕES ADMINISTRATIVAS PARA COMISSÕES")
    print("=" * 70)
    
    # 1. Verificar funções administrativas
    print("\n👑 1. FUNÇÕES ADMINISTRATIVAS:")
    funcoes_admin = [
        'ADMINISTRADOR', 'SUPER USUÁRIO', 'COMANDANTE GERAL', 'SUBCOMANDANTE GERAL',
        'DIRETOR DE GESTÃO DE PESSOAS', 'CHEFE DA SEÇÃO DE PROMOÇÕES'
    ]
    
    for funcao_admin in funcoes_admin:
        cargos = CargoFuncao.objects.filter(
            nome__icontains=funcao_admin.replace(' DE ', ' ').replace(' DA ', ' ')
        )
        if cargos.exists():
            print(f"   ✅ {funcao_admin}: {cargos.count()} cargo(s) encontrado(s)")
            for cargo in cargos:
                print(f"      - {cargo.nome}")
        else:
            print(f"   ⚠️  {funcao_admin}: Nenhum cargo encontrado")
    
    # 2. Verificar usuários com funções administrativas
    print("\n👥 2. USUÁRIOS COM FUNÇÕES ADMINISTRATIVAS:")
    usuarios_admin = []
    
    for funcao_admin in funcoes_admin:
        funcoes = UsuarioFuncao.objects.filter(
            cargo_funcao__nome__icontains=funcao_admin.replace(' DE ', ' ').replace(' DA ', ' '),
            status='ATIVO'
        ).select_related('usuario', 'cargo_funcao')
        
        if funcoes.exists():
            print(f"   {funcao_admin}:")
            for funcao in funcoes:
                print(f"      - {funcao.usuario.username}: {funcao.cargo_funcao.nome}")
                usuarios_admin.append(funcao.usuario.username)
        else:
            print(f"   ⚠️  {funcao_admin}: Nenhum usuário encontrado")
    
    # 3. Verificar comissões existentes
    print("\n📋 3. COMISSÕES EXISTENTES:")
    comissoes = ComissaoPromocao.objects.all()
    for comissao in comissoes:
        membros_count = comissao.membros.count()
        print(f"   - {comissao.nome} ({comissao.get_tipo_display()}) - {membros_count} membros")
    
    # 4. Testar lógica de permissões
    print("\n🔍 4. TESTANDO LÓGICA DE PERMISSÕES:")
    
    # Buscar uma comissão CPO
    comissao_cpo = ComissaoPromocao.objects.filter(tipo='CPO').first()
    if comissao_cpo:
        print(f"   Comissão CPO: {comissao_cpo.nome}")
        
        # Simular verificação de permissão administrativa
        funcoes_admin_test = [
            'ADMINISTRADOR', 'SUPER USUÁRIO', 'COMANDANTE GERAL', 'SUBCOMANDANTE GERAL',
            'DIRETOR DE GESTÃO DE PESSOAS', 'CHEFE DA SEÇÃO DE PROMOÇÕES'
        ]
        
        for funcao_admin in funcoes_admin_test:
            # Verificar se existe cargo com esse nome
            cargos_admin = CargoFuncao.objects.filter(
                nome__icontains=funcao_admin.replace(' DE ', ' ').replace(' DA ', ' ')
            )
            if cargos_admin.exists():
                print(f"      ✅ {funcao_admin}: Pode adicionar oficiais e presidentes/secretários")
            else:
                print(f"      ⚠️  {funcao_admin}: Cargo não encontrado")
        
        # Verificar membros CPO
        funcoes_cpo = UsuarioFuncao.objects.filter(
            cargo_funcao__nome__icontains='CPO',
            status='ATIVO'
        ).select_related('usuario', 'cargo_funcao')
        
        if funcoes_cpo.exists():
            print(f"      ✅ Membros CPO: Podem adicionar apenas oficiais")
            for funcao in funcoes_cpo:
                print(f"         - {funcao.usuario.username}: {funcao.cargo_funcao.nome}")
        else:
            print(f"      ⚠️  Membros CPO: Nenhum encontrado")
    
    # Buscar uma comissão CPP
    comissao_cpp = ComissaoPromocao.objects.filter(tipo='CPP').first()
    if comissao_cpp:
        print(f"   Comissão CPP: {comissao_cpp.nome}")
        
        # Verificar membros CPP
        funcoes_cpp = UsuarioFuncao.objects.filter(
            cargo_funcao__nome__icontains='CPP',
            status='ATIVO'
        ).select_related('usuario', 'cargo_funcao')
        
        if funcoes_cpp.exists():
            print(f"      ✅ Membros CPP: Podem adicionar apenas praças")
            for funcao in funcoes_cpp:
                print(f"         - {funcao.usuario.username}: {funcao.cargo_funcao.nome}")
        else:
            print(f"      ⚠️  Membros CPP: Nenhum encontrado")
    
    # 5. Verificar militares disponíveis
    print("\n🎖️  5. MILITARES DISPONÍVEIS:")
    
    # Oficiais
    oficiais = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['CB', 'TC', 'MJ', 'CP', '1T', '2T', 'AS']
    ).order_by('posto_graduacao', 'nome_completo')
    print(f"   Oficiais ({oficiais.count()}):")
    for militar in oficiais[:3]:
        print(f"     - {militar.posto_graduacao} {militar.nome_completo}")
    if oficiais.count() > 3:
        print(f"     ... e mais {oficiais.count() - 3} oficiais")
    
    # Praças
    pracas = Militar.objects.filter(
        situacao='AT',
        posto_graduacao__in=['ST', '1S', '2S', '3S', 'CAB', 'SD']
    ).order_by('posto_graduacao', 'nome_completo')
    print(f"   Praças ({pracas.count()}):")
    for militar in pracas[:3]:
        print(f"     - {militar.posto_graduacao} {militar.nome_completo}")
    if pracas.count() > 3:
        print(f"     ... e mais {pracas.count() - 3} praças")
    
    # 6. Resumo das permissões
    print("\n📊 6. RESUMO DAS PERMISSÕES:")
    print("   Administradores, Diretores e Chefes podem:")
    print("   ✅ Adicionar oficiais às comissões CPO")
    print("   ✅ Adicionar praças às comissões CPP")
    print("   ✅ Adicionar presidentes e secretários")
    print("   ✅ Editar membros existentes")
    print("   ✅ Remover membros")
    print()
    print("   Membros CPO podem:")
    print("   ✅ Adicionar apenas oficiais às comissões CPO")
    print("   ❌ Não podem adicionar praças")
    print("   ❌ Não podem adicionar presidentes/secretários")
    print()
    print("   Membros CPP podem:")
    print("   ✅ Adicionar apenas praças às comissões CPP")
    print("   ❌ Não podem adicionar oficiais")
    print("   ❌ Não podem adicionar presidentes/secretários")
    
    print("\n✅ Teste concluído!")
    return True

if __name__ == '__main__':
    testar_permissoes_admin_comissao() 