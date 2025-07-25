#!/usr/bin/env python
"""
Script para corrigir os nomes das comissões no banco de dados
Substitui "Comissão de Promoção" por "Comissão de Promoções"
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import ComissaoPromocao

def corrigir_nomes_comissoes():
    """Corrige os nomes das comissões no banco de dados"""
    
    # Buscar todas as comissões
    comissoes = ComissaoPromocao.objects.all()
    
    print(f"Encontradas {comissoes.count()} comissões no banco de dados")
    
    for comissao in comissoes:
        nome_original = comissao.nome
        nome_corrigido = nome_original.replace("Comissão de Promoção", "Comissão de Promoções")
        
        if nome_original != nome_corrigido:
            print(f"Corrigindo: '{nome_original}' -> '{nome_corrigido}'")
            comissao.nome = nome_corrigido
            comissao.save()
        else:
            print(f"Já correto: '{nome_original}'")
    
    print("\nCorreção concluída!")

if __name__ == "__main__":
    corrigir_nomes_comissoes() 