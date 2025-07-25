#!/usr/bin/env python
"""
Script para corrigir os últimos problemas de encoding nas descrições dos cargos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao
from django.db import transaction

def corrigir_ultimos_problemas():
    """Corrige os últimos problemas de encoding"""
    print("🔧 Corrigindo os últimos problemas de encoding...")
    print("=" * 60)
    
    # Mapeamento específico dos últimos problemas
    correcoes = {
        'Diretor de GestÒo de Pessoas': 'Diretor de Gestão de Pessoas',
        'Chefe da SeçÒo de Promoções': 'Chefe da Seção de Promoções',
        'Chefe da SeçÒo de Pessoal': 'Chefe da Seção de Pessoal'
    }
    
    cargos_corrigidos = 0
    
    for descricao_errada, descricao_correta in correcoes.items():
        try:
            cargo = CargoFuncao.objects.get(descricao=descricao_errada)
            cargo.descricao = descricao_correta
            cargo.save()
            cargos_corrigidos += 1
            print(f"   ✅ Corrigido: {cargo.nome}")
            print(f"      De: '{descricao_errada}'")
            print(f"      Para: '{descricao_correta}'")
        except CargoFuncao.DoesNotExist:
            print(f"   ⚠️  Cargo não encontrado com descrição: '{descricao_errada}'")
        except Exception as e:
            print(f"   ❌ Erro ao corrigir: {e}")
    
    print(f"\n📊 Cargos corrigidos: {cargos_corrigidos}")
    return cargos_corrigidos

def verificar_resultado_final():
    """Verifica o resultado final"""
    print("\n🔍 Verificação final...")
    print("=" * 60)
    
    cargos = CargoFuncao.objects.all().order_by('nome')
    print("📋 Cargos com suas descrições:")
    
    for cargo in cargos:
        print(f"   • {cargo.nome}")
        if cargo.descricao:
            print(f"     Descrição: {cargo.descricao}")
    
    # Verificar se ainda há caracteres corrompidos
    caracteres_corrompidos = ['Ò', 'ç']
    problemas_restantes = 0
    
    for cargo in cargos:
        if cargo.descricao and any(c in cargo.descricao for c in caracteres_corrompidos):
            problemas_restantes += 1
            print(f"   ⚠️  Ainda há problema em: {cargo.nome} - {cargo.descricao}")
    
    if problemas_restantes == 0:
        print("\n🎉 TODOS OS PROBLEMAS DE ENCODING FORAM CORRIGIDOS!")
    else:
        print(f"\n⚠️  Ainda existem {problemas_restantes} problemas")

def main():
    """Função principal"""
    print("🚀 Corrigindo os últimos problemas de encoding...")
    print("=" * 60)
    
    with transaction.atomic():
        cargos_corrigidos = corrigir_ultimos_problemas()
        
        print("\n" + "=" * 60)
        print(f"📊 TOTAL DE CORREÇÕES: {cargos_corrigidos}")
        
        if cargos_corrigidos > 0:
            print("✅ Correções aplicadas com sucesso!")
        else:
            print("✅ Nenhuma correção necessária!")
    
    verificar_resultado_final()

if __name__ == '__main__':
    main() 