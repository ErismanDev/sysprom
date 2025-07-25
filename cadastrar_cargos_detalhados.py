#!/usr/bin/env python
"""
Script para cadastrar cargos/funções detalhadas no modelo CargoFuncao
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao

def cadastrar_cargos_detalhados():
    """Cadastra os cargos/funções detalhadas no modelo CargoFuncao"""
    
    # Lista de cargos detalhados para CPO e CPP
    cargos_cpo = [
        {
            'nome': 'Presidente da CPO',
            'descricao': 'Presidente da Comissão de Promoções de Oficiais',
            'codigo': 'PRESIDENTE_CPO',
            'ordem': 1
        },
        {
            'nome': 'Membro Nato da CPO',
            'descricao': 'Membro Nato da Comissão de Promoções de Oficiais',
            'codigo': 'NATO_CPO',
            'ordem': 2
        },
        {
            'nome': 'Membro Efetivo da CPO',
            'descricao': 'Membro Efetivo da Comissão de Promoções de Oficiais',
            'codigo': 'EFETIVO_CPO',
            'ordem': 3
        },
        {
            'nome': 'Secretário da CPO',
            'descricao': 'Secretário da Comissão de Promoções de Oficiais',
            'codigo': 'SECRETARIO_CPO',
            'ordem': 4
        },
        {
            'nome': 'Suplente da CPO',
            'descricao': 'Suplente da Comissão de Promoções de Oficiais',
            'codigo': 'SUPLENTE_CPO',
            'ordem': 5
        }
    ]

    # CPP - Comissão de Promoções de Praças
    cargos_cpp = [
        {
            'nome': 'Presidente da CPP',
            'descricao': 'Presidente da Comissão de Promoções de Praças',
            'codigo': 'PRESIDENTE_CPP',
            'ordem': 6
        },
        {
            'nome': 'Membro Nato da CPP',
            'descricao': 'Membro Nato da Comissão de Promoções de Praças',
            'codigo': 'NATO_CPP',
            'ordem': 7
        },
        {
            'nome': 'Membro Efetivo da CPP',
            'descricao': 'Membro Efetivo da Comissão de Promoções de Praças',
            'codigo': 'EFETIVO_CPP',
            'ordem': 8
        },
        {
            'nome': 'Secretário da CPP',
            'descricao': 'Secretário da Comissão de Promoções de Praças',
            'codigo': 'SECRETARIO_CPP',
            'ordem': 9
        },
        {
            'nome': 'Suplente da CPP',
            'descricao': 'Suplente da Comissão de Promoções de Praças',
            'codigo': 'SUPLENTE_CPP',
            'ordem': 10
        }
    ]
    
    print("🔧 Cadastrando cargos/funções detalhadas...")
    print("=" * 60)
    
    cargos_criados = 0
    cargos_existentes = 0
    
    for cargo_info in cargos_detalhados:
        # Verificar se o cargo já existe
        cargo_existente = CargoFuncao.objects.filter(
            nome=cargo_info['nome']
        ).first()
        
        if cargo_existente:
            print(f"⚠️  Cargo já existe: {cargo_info['nome']}")
            cargos_existentes += 1
            continue
        
        # Criar novo cargo
        novo_cargo = CargoFuncao.objects.create(
            nome=cargo_info['nome'],
            descricao=cargo_info['descricao'],
            ordem=cargo_info['ordem'],
            ativo=cargo_info['ativo']
        )
        
        print(f"✅ Cargo criado: {novo_cargo.nome}")
        cargos_criados += 1
    
    print("=" * 60)
    print(f"📊 Resumo:")
    print(f"   ✅ Cargos criados: {cargos_criados}")
    print(f"   ⚠️  Cargos já existentes: {cargos_existentes}")
    print(f"   📋 Total processados: {cargos_criados + cargos_existentes}")
    
    # Mostrar cargos cadastrados
    print("\n📋 Cargos cadastrados:")
    cargos_ativos = CargoFuncao.objects.filter(ativo=True).order_by('ordem', 'nome')
    for cargo in cargos_ativos:
        print(f"   - {cargo.nome}")
    
    return True

if __name__ == "__main__":
    try:
        sucesso = cadastrar_cargos_detalhados()
        if sucesso:
            print("\n🎉 Script executado com sucesso!")
        else:
            print("\n❌ Erro ao executar o script!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc() 