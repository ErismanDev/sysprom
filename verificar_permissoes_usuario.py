#!/usr/bin/env python
"""
Script para verificar as permissões do usuário atual
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.contrib.auth.models import User
from militares.models import MembroComissao, ComissaoPromocao, FuncaoMilitar, Militar

def verificar_permissoes_usuario():
    print("🔍 VERIFICAÇÃO DE PERMISSÕES DO USUÁRIO\n")
    
    # Buscar usuário José ERISMAN
    try:
        usuario = User.objects.get(username='490.083.823-34')
        print(f"👤 Usuário: {usuario.get_full_name()} ({usuario.username})")
    except User.DoesNotExist:
        print("❌ Usuário não encontrado")
        return
    
    # Verificar grupos
    grupos = usuario.groups.all()
    print(f"\n📋 Grupos:")
    for grupo in grupos:
        print(f"  - {grupo.name}")
    
    # Verificar funções militares
    funcoes = FuncaoMilitar.objects.filter(usuario=usuario, status='ATIVO')
    print(f"\n🎖️ Funções Militares Ativas:")
    for funcao in funcoes:
        print(f"  - {funcao.cargo_funcao.nome}")
    
    # Verificar membros de comissão
    membros_comissao = MembroComissao.objects.filter(
        usuario=usuario,
        ativo=True
    ).select_related('comissao', 'cargo')
    
    print(f"\n🏛️ Membros de Comissão:")
    for membro in membros_comissao:
        print(f"  - {membro.comissao.nome} ({membro.comissao.tipo})")
        print(f"    Cargo: {membro.cargo.nome if membro.cargo else 'N/A'}")
        print(f"    Ativo: {membro.ativo}")
        print(f"    Status da Comissão: {membro.comissao.status}")
    
    # Verificar se é presidente
    comissoes_ativas = ComissaoPromocao.objects.filter(status='ATIVA')
    print(f"\n👑 Verificação de Presidência:")
    for comissao in comissoes_ativas:
        if comissao.eh_presidente(usuario):
            print(f"  ✅ Presidente da {comissao.nome} ({comissao.tipo})")
        else:
            print(f"  ❌ NÃO é presidente da {comissao.nome} ({comissao.tipo})")
    
    # Verificar permissões específicas
    print(f"\n🔐 Permissões Específicas:")
    
    # Verificar se pode assinar documentos de oficiais
    comissao_cpo = ComissaoPromocao.get_comissao_ativa_por_tipo('CPO')
    if comissao_cpo:
        pode_assinar_oficiais = comissao_cpo.pode_assinar_documento_oficial(usuario)
        print(f"  - Pode assinar documentos de oficiais: {pode_assinar_oficiais}")
    else:
        print(f"  - CPO não encontrada")
    
    # Verificar se pode assinar documentos de praças
    comissao_cpp = ComissaoPromocao.get_comissao_ativa_por_tipo('CPP')
    if comissao_cpp:
        pode_assinar_pracas = comissao_cpp.pode_assinar_documento_praca(usuario)
        print(f"  - Pode assinar documentos de praças: {pode_assinar_pracas}")
    else:
        print(f"  - CPP não encontrada")
    
    # Verificar acesso a quadros de fixação
    print(f"\n📊 Acesso a Quadros de Fixação:")
    
    # Verificar se tem cargo especial
    cargos_especiais = ['Diretor de Gestão de Pessoas', 'Chefe da Seção de Promoções']
    funcoes_especiais = funcoes.filter(cargo_funcao__nome__in=cargos_especiais)
    if funcoes_especiais.exists():
        print(f"  ✅ Tem cargo especial: {[f.cargo_funcao.nome for f in funcoes_especiais]}")
    else:
        print(f"  ❌ NÃO tem cargo especial")
    
    # Verificar se é membro de comissão
    if membros_comissao.exists():
        tem_cpo = membros_comissao.filter(comissao__tipo='CPO').exists()
        tem_cpp = membros_comissao.filter(comissao__tipo='CPP').exists()
        print(f"  - Membro CPO: {tem_cpo}")
        print(f"  - Membro CPP: {tem_cpp}")
        
        if tem_cpo and tem_cpp:
            print(f"  ✅ Pode acessar TODOS os quadros de fixação")
        elif tem_cpo:
            print(f"  ✅ Pode acessar apenas quadros de OFICIAIS")
        elif tem_cpp:
            print(f"  ✅ Pode acessar apenas quadros de PRACAS")
        else:
            print(f"  ❌ NÃO pode acessar quadros de fixação")
    else:
        print(f"  ❌ NÃO é membro de nenhuma comissão")

if __name__ == "__main__":
    verificar_permissoes_usuario() 