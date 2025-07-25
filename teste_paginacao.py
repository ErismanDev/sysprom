#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from django.core.paginator import Paginator
from militares.models import Militar

def testar_paginacao():
    print("Testando paginação...")
    
    # Buscar militares
    militares = Militar.objects.filter(situacao='AT')
    print(f"Total de militares ativos: {militares.count()}")
    
    # Testar paginação
    paginator = Paginator(militares, 20)
    print(f"Total de páginas: {paginator.num_pages}")
    
    # Testar primeira página
    page = paginator.get_page(1)
    print(f"Página 1 - Itens: {len(page)}")
    print(f"Página 1 - Start index: {page.start_index()}")
    print(f"Página 1 - End index: {page.end_index()}")
    
    # Testar segunda página (se existir)
    if paginator.num_pages > 1:
        page2 = paginator.get_page(2)
        print(f"Página 2 - Itens: {len(page2)}")
        print(f"Página 2 - Start index: {page2.start_index()}")
        print(f"Página 2 - End index: {page2.end_index()}")
    
    print("Teste concluído!")

if __name__ == "__main__":
    testar_paginacao() 