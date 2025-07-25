#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sepromcbmepi.settings')
django.setup()

from militares.models import Militar
from django.db.models import Count

def verificar_postos():
    print("=== POSTOS COM MILITARES ATIVOS ===")
    
    postos = Militar.objects.filter(
        situacao='AT'
    ).values('posto_graduacao', 'quadro').annotate(
        count=Count('id')
    ).order_by('posto_graduacao', 'quadro')
    
    for posto in postos:
        print(f"{posto['posto_graduacao']} - {posto['quadro']}: {posto['count']} militares")
        
        # Mostrar alguns exemplos
        militares = Militar.objects.filter(
            posto_graduacao=posto['posto_graduacao'],
            quadro=posto['quadro'],
            situacao='AT'
        ).order_by('numeracao_antiguidade')[:5]
        
        for militar in militares:
            print(f"  {militar.numeracao_antiguidade}º - {militar.nome_completo}")
        print()

if __name__ == '__main__':
    verificar_postos() 