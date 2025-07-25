#!/usr/bin/env python
"""
Script para corrigir o nome "secretario" na tabela de funções
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import CargoFuncao
from django.db import transaction

def corrigir_nome_secretario():
    """
    Corrige o nome "secretario" para "Secretário" na tabela de funções
    """
    print("🔧 Verificando e corrigindo nome 'secretario' na tabela de funções...")
    print("=" * 60)
    
    # Buscar cargos que contêm "secretario" (sem acento)
    cargos_secretario = CargoFuncao.objects.filter(nome__icontains='secretario')
    
    print(f"📊 Cargos encontrados com 'secretario': {cargos_secretario.count()}")
    
    if cargos_secretario.exists():
        print("\n📋 Cargos que precisam ser corrigidos:")
        for cargo in cargos_secretario:
            print(f"   • ID: {cargo.id} | Nome atual: '{cargo.nome}'")
        
        print("\n🔄 Iniciando correção...")
        
        with transaction.atomic():
            for cargo in cargos_secretario:
                nome_antigo = cargo.nome
                
                # Corrigir o nome
                if 'secretario' in cargo.nome.lower():
                    # Substituir "secretario" por "Secretário"
                    nome_novo = cargo.nome.replace('secretario', 'Secretário').replace('SECRETARIO', 'Secretário')
                    
                    # Atualizar o cargo
                    cargo.nome = nome_novo
                    cargo.save()
                    
                    print(f"✅ Corrigido: '{nome_antigo}' → '{nome_novo}'")
        
        print("\n✅ Correção concluída!")
    else:
        print("✅ Nenhum cargo com 'secretario' encontrado!")
    
    # Verificar se ainda há problemas
    print("\n🔍 Verificação final:")
    cargos_finais = CargoFuncao.objects.filter(nome__icontains='secretario')
    if cargos_finais.exists():
        print("⚠️  Ainda existem cargos com 'secretario':")
        for cargo in cargos_finais:
            print(f"   • {cargo.nome}")
    else:
        print("✅ Todos os cargos foram corrigidos!")
    
    # Listar todos os cargos com "Secretário" (correto)
    print("\n📋 Cargos com 'Secretário' (correto):")
    cargos_corretos = CargoFuncao.objects.filter(nome__icontains='Secretário')
    for cargo in cargos_corretos:
        print(f"   • {cargo.nome}")

def main():
    """
    Função principal
    """
    corrigir_nome_secretario()

if __name__ == '__main__':
    main() 