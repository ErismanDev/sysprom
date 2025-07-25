#!/usr/bin/env python
"""
Script para corrigir problemas de encoding nos nomes dos cargos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao
from django.db import transaction

def corrigir_encoding_cargos():
    """
    Corrige problemas de encoding nos nomes dos cargos
    """
    print("🔧 Corrigindo problemas de encoding nos nomes dos cargos...")
    print("=" * 60)
    
    # Mapeamento de correções
    correcoes = {
        'Secretßrio da CPO': 'Secretário da CPO',
        'Secretßrio da CPP': 'Secretário da CPP',
        'Chefe da SeþÒo de Pessoal': 'Chefe da Seção de Pessoal',
        'Chefe da SeþÒo de Promoþ§es': 'Chefe da Seção de Promoções',
        'Diretor de GestÒo de Pessoas': 'Diretor de Gestão de Pessoas',
        'Gestor de Promoþ§es': 'Gestor de Promoções',
        'Membro de ComissÒo': 'Membro de Comissão',
        'Usußrio': 'Usuário'
    }
    
    print("📋 Correções necessárias:")
    for nome_errado, nome_correto in correcoes.items():
        print(f"   • '{nome_errado}' → '{nome_correto}'")
    
    print("\n🔄 Iniciando correções...")
    
    with transaction.atomic():
        for nome_errado, nome_correto in correcoes.items():
            try:
                cargo = CargoFuncao.objects.get(nome=nome_errado)
                cargo.nome = nome_correto
                cargo.save()
                print(f"✅ Corrigido: '{nome_errado}' → '{nome_correto}'")
            except CargoFuncao.DoesNotExist:
                print(f"⚠️  Cargo não encontrado: '{nome_errado}'")
            except Exception as e:
                print(f"❌ Erro ao corrigir '{nome_errado}': {e}")
    
    print("\n✅ Correções concluídas!")
    
    # Verificação final
    print("\n🔍 Verificação final dos cargos:")
    todos_cargos = CargoFuncao.objects.all().order_by('nome')
    for cargo in todos_cargos:
        print(f"   • {cargo.nome}")
    
    # Verificar se ainda há problemas
    cargos_problematicos = CargoFuncao.objects.filter(
        nome__regex=r'[À-ÿ]'
    )
    
    if cargos_problematicos.exists():
        print(f"\n⚠️  Ainda existem {cargos_problematicos.count()} cargos com caracteres especiais:")
        for cargo in cargos_problematicos:
            print(f"   • {cargo.nome}")
    else:
        print("\n✅ Todos os problemas de encoding foram corrigidos!")

def main():
    """
    Função principal
    """
    corrigir_encoding_cargos()

if __name__ == '__main__':
    main() 