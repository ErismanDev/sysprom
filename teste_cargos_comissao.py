#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.forms import MembroComissaoForm
from militares.models import CargoComissao

def testar_cargos_comissao():
    print("=== TESTE DOS CARGOS DA COMISSÃO ===")
    
    # Testar formulário CPO
    print("\n1. Testando CPO (Comissão de Promoções de Oficiais):")
    form_cpo = MembroComissaoForm(comissao_tipo='CPO')
    
    # Verificar opções do campo cargo
    cargo_choices = form_cpo.fields['cargo'].choices
    print(f"   Opções de cargo disponíveis: {len(cargo_choices)}")
    
    for choice in cargo_choices:
        if choice[0]:  # Ignorar opção vazia
            print(f"   - {choice[1]}")
    
    # Verificar se os cargos corretos estão presentes
    cargos_esperados = ['Presidente da Comissão', 'Membro Nato', 'Secretário', 'Membro Efetivo']
    cargos_presentes = [choice[1] for choice in cargo_choices if choice[0]]
    
    print(f"\n   Cargos esperados: {cargos_esperados}")
    print(f"   Cargos presentes: {cargos_presentes}")
    
    # Verificar se todos os cargos esperados estão presentes
    todos_presentes = all(cargo in cargos_presentes for cargo in cargos_esperados)
    if todos_presentes:
        print("   ✓ Todos os cargos esperados estão presentes!")
    else:
        print("   ✗ Alguns cargos esperados não estão presentes!")
    
    # Testar formulário CPP
    print("\n2. Testando CPP (Comissão de Promoções de Praças):")
    form_cpp = MembroComissaoForm(comissao_tipo='CPP')
    
    cargo_choices_cpp = form_cpp.fields['cargo'].choices
    print(f"   Opções de cargo disponíveis: {len(cargo_choices_cpp)}")
    
    for choice in cargo_choices_cpp:
        if choice[0]:  # Ignorar opção vazia
            print(f"   - {choice[1]}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    testar_cargos_comissao() 