#!/usr/bin/env python
"""
Script para testar a funcionalidade da nota do CHO
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar, QuadroAcesso
from decimal import Decimal

def testar_nota_cho():
    """Testa a funcionalidade da nota do CHO"""
    print("=== TESTE DA FUNCIONALIDADE NOTA CHO ===\n")
    
    # Buscar subtenentes
    subtenentes = Militar.objects.filter(
        posto_graduacao='ST',
        situacao='AT'
    ).order_by('nome_completo')
    
    print(f"Encontrados {subtenentes.count()} subtenentes ativos:\n")
    
    for militar in subtenentes:
        print(f"{militar.nome_completo}")
        print(f"  - Possui CHO: {'Sim' if militar.curso_cho else 'Não'}")
        if militar.curso_cho and militar.nota_cho:
            print(f"  - Nota do CHO: {militar.nota_cho}")
        else:
            print(f"  - Nota do CHO: Não informada")
        print()
    
    # Testar ordenação em um quadro de acesso
    print("=== TESTE DE ORDENAÇÃO EM QUADRO DE ACESSO ===\n")
    
    # Criar um quadro de acesso de teste
    from datetime import date
    quadro = QuadroAcesso.objects.create(
        tipo='ANTIGUIDADE',
        categoria='OFICIAIS',
        data_promocao=date(2025, 7, 18),
        status='EM_ELABORACAO'
    )
    
    # Adicionar subtenentes ao quadro
    for militar in subtenentes:
        if militar.apto_quadro_acesso():
            quadro.adicionar_militar_manual(militar)
    
    # Gerar o quadro completo
    quadro.gerar_quadro_completo()
    
    # Mostrar a ordenação
    itens = quadro.itemquadroacesso_set.all().order_by('posicao')
    
    print("Ordenação dos subtenentes no quadro de acesso:")
    for item in itens:
        militar = item.militar
        nota_cho = militar.nota_cho if militar.nota_cho else "N/A"
        print(f"{item.posicao}º - {militar.nome_completo} - Nota CHO: {nota_cho}")
    
    # Limpar o quadro de teste
    quadro.delete()
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == '__main__':
    testar_nota_cho() 